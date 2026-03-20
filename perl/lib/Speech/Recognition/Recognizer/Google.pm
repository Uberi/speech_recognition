package Speech::Recognition::Recognizer::Google;

use v5.36;
use Speech::Recognition::Recognizer::_Base qw();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer::Google - Google Speech Recognition backend

=head1 SYNOPSIS

    my $text = $r->recognize_google($audio,
        language => 'en-US',
        show_all => 0,
    );

=head1 DESCRIPTION

Uses Google's Speech Recognition API v2 (the public, unofficial endpoint).
This API is deprecated and may stop working without notice; it is provided for
compatibility with the Python SpeechRecognition library.

A C<key> argument can be provided to use your own API key.  If omitted, the
same default key used by the Python library is used.

=head1 ARGUMENTS

=over 4

=item * C<language> - BCP-47 language tag, default C<en-US>

=item * C<key> - API key (optional)

=item * C<show_all> - if true, returns the full decoded JSON response instead
of just the transcript string

=item * C<pfilter> - profanity filter level (0 or 2, default 0)

=back

=cut

# The same default key used by the Python speech_recognition library
use constant GOOGLE_DEFAULT_KEY => 'AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw';

sub recognize ( $self, $audio_data, %args ) {
    Speech::Recognition::Recognizer::_Base::assert_audio($audio_data);

    my $key      = $args{key}      // GOOGLE_DEFAULT_KEY;
    my $language = $args{language} // 'en-US';
    my $pfilter  = $args{pfilter}  // 0;
    my $show_all = $args{show_all} // 0;

    my $flac_data = $audio_data->get_flac_data(
        $audio_data->sample_rate < 8000
            ? ( convert_rate => 8000 )
            : ()
    );

    my %params = (
        client   => 'chromium',
        lang     => $language,
        key      => $key,
        pfilter  => $pfilter,
        output   => 'json',
    );

    require URI;
    my $url = 'https://www.google.com/speech-api/v2/recognize?'
        . _urlencode(%params);

    my $ua  = Speech::Recognition::Recognizer::_Base::make_ua(
        $self->{operation_timeout} // 30
    );
    my $req = HTTP::Request->new(
        POST => $url,
        [
            'Content-Type'   => 'audio/x-flac; rate=' . $audio_data->sample_rate,
            'User-Agent'     => 'Mozilla/5.0',
        ],
        $flac_data,
    );

    my $res = $ua->request($req);
    unless ( $res->is_success ) {
        Speech::Recognition::Recognizer::_Base::throw_request(
            'Google Speech request failed: ' . $res->status_line
        );
    }

    # The Google API returns multiple JSON lines; only non-empty lines matter
    my @results;
    for my $line ( split /\n/, $res->content ) {
        next unless $line =~ /\S/;
        my $obj = eval {
            Speech::Recognition::Recognizer::_Base::decode_json($line)
        };
        next unless defined $obj;
        push @results, @{ $obj->{result} // [] };
    }

    return \@results if $show_all;

    # Return the best (first) transcript
    for my $result (@results) {
        if ( ref $result->{alternative} eq 'ARRAY' && @{ $result->{alternative} } ) {
            return $result->{alternative}[0]{transcript};
        }
    }

    Speech::Recognition::Recognizer::_Base::throw_unknown();
}

sub _urlencode (%params) {
    join '&', map {
        _encode_uri_component($_) . '=' . _encode_uri_component( $params{$_} )
    } sort keys %params;
}

sub _encode_uri_component ($str) {
    $str =~ s/([^A-Za-z0-9\-_.~])/sprintf('%%%02X', ord($1))/ge;
    return $str;
}

1;

__END__

=head1 NOTES

The Google Speech API v2 endpoint is unofficial and unsupported.  It may
return results in a non-standard format or stop working entirely at any time.

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
