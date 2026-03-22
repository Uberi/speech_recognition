package Speech::Recognition::Recognizer::_Base;

use v5.36;
use Carp            qw(croak);
use IPC::Open3            ();
use IO::Select            ();
use LWP::UserAgent        ();
use HTTP::Request         ();
use HTTP::Request::Common qw(POST);
use URI::Escape           qw(uri_escape);

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer::_Base - Shared helpers for recognition backends

=head1 DESCRIPTION

Internal module.  Not for direct use.

=cut

# ---------------------------------------------------------------------------
# JSON (prefer JSON::XS for speed; fall back to JSON::PP from core)
# ---------------------------------------------------------------------------

my $_json_decode;
my $_json_encode;

BEGIN {
    if ( eval { require JSON::XS; 1 } ) {
        $_json_decode = \&JSON::XS::decode_json;
        $_json_encode = \&JSON::XS::encode_json;
    }
    else {
        require JSON::PP;
        $_json_decode = \&JSON::PP::decode_json;
        $_json_encode = \&JSON::PP::encode_json;
    }
}

sub decode_json ($text)  { $_json_decode->($text) }
sub encode_json ($data)  { $_json_encode->($data) }

# ---------------------------------------------------------------------------
# LWP user-agent factory
# ---------------------------------------------------------------------------

sub make_ua ( $timeout = 30 ) {
    my $ver = $Speech::Recognition::VERSION // '0.01';
    my $ua = LWP::UserAgent->new(
        timeout => $timeout // 30,
        agent   => "Speech-Recognition-Perl/$ver",
    );
    $ua->env_proxy;
    return $ua;
}

# ---------------------------------------------------------------------------
# Convenience: throw typed exceptions
# ---------------------------------------------------------------------------

sub throw_request ($msg) {
    require Speech::Recognition::Exception;
    Speech::Recognition::Exception::RequestError->throw($msg);
}

sub throw_unknown {
    require Speech::Recognition::Exception;
    Speech::Recognition::Exception::UnknownValueError->throw();
}

sub throw_setup ($msg) {
    require Speech::Recognition::Exception;
    Speech::Recognition::Exception::SetupError->throw($msg);
}

# ---------------------------------------------------------------------------
# URL encoding
# ---------------------------------------------------------------------------

sub urlencode (%params) {
    join '&', map { uri_escape($_) . '=' . uri_escape( $params{$_} ) }
        sort keys %params;
}

# ---------------------------------------------------------------------------
# Run an external command; return (stdout, stderr).
# Throws RequestError on non-zero exit.
# ---------------------------------------------------------------------------

sub run_cmd (@cmd) {
    my ( $child_in, $child_out, $child_err );
    my $pid;

    {
        local $@;
        my $ok = eval {
            $pid = IPC::Open3::open3( $child_in, $child_out, $child_err, @cmd );
            1;
        };
        if ( !$ok ) {
            my $err = $@ || $!;
            $err //= 'unknown error';
            throw_request("Failed to run '$cmd[0]': $err");
        }
    }
    close $child_in;

    my $sel = IO::Select->new( $child_out, $child_err );
    my ( $out_text, $err_text ) = ( '', '' );
    while ( my @ready = $sel->can_read() ) {
        for my $fh (@ready) {
            my $buf   = '';
            my $bytes = sysread $fh, $buf, 4096;
            if ( defined $bytes ) {
                if ( $bytes == 0 ) {
                    $sel->remove($fh);
                    close $fh;
                }
                else {
                    if ( $fh == $child_out ) { $out_text .= $buf }
                    else                     { $err_text .= $buf }
                }
            }
            else {
                next if $!{EAGAIN} || $!{EWOULDBLOCK};
                $sel->remove($fh);
                close $fh;
            }
        }
    }
    waitpid $pid, 0;
    my $exit = $? >> 8;

    if ( $exit != 0 ) {
        ( my $prog = $cmd[0] ) =~ s{.*/}{};
        my $detail = length $err_text ? ": $err_text" : '';
        throw_request("$prog failed (exit $exit)$detail");
    }

    return ( $out_text, $err_text );
}

# ---------------------------------------------------------------------------
# Find an executable on PATH
# ---------------------------------------------------------------------------

sub which ($name) {
    for my $dir ( split /:/, ( $ENV{PATH} // '/usr/local/bin:/usr/bin:/bin' ) ) {
        my $p = "$dir/$name";
        return $p if -f $p && -x $p;
    }
    return undef;
}

# ---------------------------------------------------------------------------
# Check and return audio_data
# ---------------------------------------------------------------------------

sub assert_audio ($audio_data) {
    require Speech::Recognition::AudioData;
    croak 'audio_data must be a Speech::Recognition::AudioData instance'
        unless ref $audio_data
        && $audio_data->isa('Speech::Recognition::AudioData');
    return $audio_data;
}

# ---------------------------------------------------------------------------
# Multipart POST builder (for Whisper-style APIs)
# ---------------------------------------------------------------------------

# Returns a complete HTTP::Request for a multipart/form-data POST.
# Uses HTTP::Request::Common (ships with LWP) for correct encoding.
#
# $fields   - arrayref of [name => value] pairs
# $file     - [field_name, filename, mime_type, data_bytes]
# $bearer   - API key string for Authorization header
#
sub multipart_request ( $url, $bearer, $fields, $file ) {
    my ( $fname, $ffilename, $fmime, $fdata ) = @$file;
    return POST $url,
        Authorization => "Bearer $bearer",
        Content_Type  => 'form-data',
        Content       => [
            ( map { $_->[0] => $_->[1] } @$fields ),
            $fname => [ undef, $ffilename, 'Content-Type' => $fmime, Content => $fdata ],
        ];
}

1;
