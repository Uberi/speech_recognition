package Speech::Recognition::AudioFile;

use v5.36;
use Carp       qw(croak);
use File::Temp qw(tempfile);

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::AudioFile - Audio source backed by a WAV, AIFF, or FLAC file

=head1 SYNOPSIS

    use Speech::Recognition::AudioFile;
    use Speech::Recognition::Recognizer;

    my $r = Speech::Recognition::Recognizer->new;

    # Using the with() helper (recommended — ensures the file is closed)
    my $audio;
    Speech::Recognition::AudioFile->new(filename => 'speech.wav')->with(sub ($src) {
        $audio = $r->record($src);
    });

    # Or manage open/close manually
    my $source = Speech::Recognition::AudioFile->new(filename => 'speech.wav');
    $source->open;
    my $audio2 = $r->record($source);
    $source->close;

=head1 DESCRIPTION

Provides an audio-source interface over a file on disk.  Supported formats are:

=over 4

=item * WAV (PCM only)

=item * AIFF / AIFF-C

=item * Native FLAC (decoded via the C<flac> command-line tool)

=back

Stereo files are automatically downmixed to mono.

=cut

# ---------------------------------------------------------------------------
# Inner stream class
# ---------------------------------------------------------------------------

package Speech::Recognition::AudioFile::Stream;

use v5.36;

sub new ( $class, $pcm_data, $sample_width ) {
    return bless {
        _data  => $pcm_data,
        _pos   => 0,
        _width => $sample_width,
    }, $class;
}

# Read $nsamples samples and return the corresponding bytes.
sub read ( $self, $nsamples ) {
    my $nbytes = $nsamples * $self->{_width};
    my $avail  = length( $self->{_data} ) - $self->{_pos};
    return '' if $avail <= 0;
    $nbytes = $avail if $nbytes > $avail;
    my $chunk = substr( $self->{_data}, $self->{_pos}, $nbytes );
    $self->{_pos} += length($chunk);
    return $chunk;
}

sub close ($self) {
    $self->{_data} = '';
    $self->{_pos}  = 0;
}

# ---------------------------------------------------------------------------
# AudioFile
# ---------------------------------------------------------------------------

package Speech::Recognition::AudioFile;

use v5.36;
use Carp       qw(croak);
use File::Temp qw(tempfile);

=head1 CONSTRUCTORS

=head2 new(filename => $path)

Creates a new C<AudioFile> instance.  C<filename> is required.

=cut

sub new ( $class, %args ) {
    croak 'filename is required' unless defined $args{filename};
    return bless {
        filename     => $args{filename},
        stream       => undef,
        SAMPLE_RATE  => undef,
        SAMPLE_WIDTH => undef,
        CHUNK        => 4096,
        DURATION     => undef,
        FRAME_COUNT  => undef,
        _tmp_files   => [],
    }, $class;
}

=head1 METHODS

=head2 open()

Opens the audio file and prepares the stream.  Must be called before passing
the source to C<Recognizer-E<gt>record>.  Returns C<$self> for chaining.

=cut

sub open ($self) {
    croak 'This audio source is already open'
        if defined $self->{stream};
    $self->_open_file( $self->{filename} );
    return $self;
}

=head2 close()

Closes the audio source and releases resources.

=cut

sub close ($self) {
    if ( defined $self->{stream} ) {
        $self->{stream}->close;
        $self->{stream}   = undef;
        $self->{DURATION} = undef;
    }
    # Remove any temp files created during FLAC decoding
    for my $f ( @{ $self->{_tmp_files} } ) {
        unlink $f if -f $f;
    }
    $self->{_tmp_files} = [];
}

=head2 with($callback)

Opens the source, calls C<$callback->($self)>, then closes the source even if
an exception is thrown.  Returns the value returned by C<$callback>.

This is the idiomatic Perl equivalent of Python's C<with> statement.

=cut

sub with ( $self, $callback ) {
    $self->open;
    my $result = eval { $callback->($self) };
    my $err    = $@;
    $self->close;
    die $err if $err;
    return $result;
}

# Convenience accessors used by Recognizer
sub stream       ($self) { $self->{stream} }
sub SAMPLE_RATE  ($self) { $self->{SAMPLE_RATE} }
sub SAMPLE_WIDTH ($self) { $self->{SAMPLE_WIDTH} }
sub CHUNK        ($self) { $self->{CHUNK} }
sub DURATION     ($self) { $self->{DURATION} }
sub FRAME_COUNT  ($self) { $self->{FRAME_COUNT} }

# isa check for AudioSource duck-typing
sub isa_audio_source { 1 }

# ---------------------------------------------------------------------------
# Private: file parsing
# ---------------------------------------------------------------------------

sub _open_file ( $self, $filename ) {
    if ( _try_open_wav( $self, $filename ) ) { return }
    if ( _try_open_aiff( $self, $filename ) ) { return }
    if ( _try_open_flac( $self, $filename ) ) { return }
    croak "Audio file could not be read as WAV, AIFF, or FLAC: $filename";
}

# --- WAV ---

sub _try_open_wav ( $self, $filename ) {
    CORE::open my $fh, '<', $filename or return 0;
    binmode $fh;

    my $header = '';
    read $fh, $header, 12;
    unless ( length($header) == 12 ) { CORE::close $fh; return 0 }

    my ( $riff, undef, $wave ) = unpack( 'a4 V a4', $header );
    unless ( $riff eq 'RIFF' && $wave eq 'WAVE' ) { CORE::close $fh; return 0 }

    my ( $rate, $sw, $nch, $data_start, $data_sz );

    while ( !eof $fh ) {
        my $ch = '';
        read $fh, $ch, 8;
        last unless length($ch) == 8;
        my ( $id, $csz ) = unpack( 'a4 V', $ch );

        if ( $id eq 'fmt ' ) {
            my $fmt = '';
            read $fh, $fmt, $csz;
            my ( $fmt_tag, $nc, $sr ) = unpack( 'v v V', $fmt );
            unless ( $fmt_tag == 1 || $fmt_tag == 3 ) {    # PCM or IEEE float
                CORE::close $fh;
                croak "Only PCM WAV files are supported (format tag: $fmt_tag)";
            }
            my $bps = unpack( 'v', substr( $fmt, 14, 2 ) );
            $nch = $nc;
            $rate = $sr;
            $sw   = int( $bps / 8 );
        }
        elsif ( $id eq 'data' ) {
            $data_start = tell $fh;
            $data_sz    = $csz;
            last;
        }
        else {
            # Chunks must be padded to even byte boundaries
            my $skip = $csz + ( $csz % 2 );
            seek $fh, $skip, 1;
        }
    }

    unless ( defined $data_start && defined $rate && defined $sw ) {
        CORE::close $fh;
        return 0;
    }

    seek $fh, $data_start, 0;
    my $pcm = '';
    read $fh, $pcm, $data_sz;
    CORE::close $fh;

    $pcm = _stereo_to_mono( $pcm, $sw ) if $nch && $nch == 2;

    $self->_set_audio( $pcm, $rate, $sw );
    return 1;
}

# --- AIFF ---

sub _try_open_aiff ( $self, $filename ) {
    CORE::open my $fh, '<', $filename or return 0;
    binmode $fh;

    my $header = '';
    read $fh, $header, 12;
    unless ( length($header) == 12 ) { CORE::close $fh; return 0 }

    my ( $form, undef, $type ) = unpack( 'a4 N a4', $header );
    unless ( $form eq 'FORM' && ( $type eq 'AIFF' || $type eq 'AIFC' ) ) {
        CORE::close $fh;
        return 0;
    }

    my ( $rate, $sw, $nch, $nframes, $pcm_data );

    while ( !eof $fh ) {
        my $ch = '';
        read $fh, $ch, 8;
        last unless length($ch) == 8;
        my ( $id, $csz ) = unpack( 'a4 N', $ch );

        if ( $id eq 'COMM' ) {
            my $comm = '';
            read $fh, $comm, $csz;
            ( $nch, $nframes ) = unpack( 'n N', $comm );
            my $bps = unpack( 'n', substr( $comm, 6, 2 ) );
            $sw   = int( $bps / 8 );
            $rate = int( _decode_80bit_float( substr( $comm, 8, 10 ) ) );
        }
        elsif ( $id eq 'SSND' ) {
            my $meta = '';
            read $fh, $meta, 8;    # skip offset and blockSize
            my $audio_sz = $csz - 8;
            read $fh, $pcm_data, $audio_sz;
            last;
        }
        else {
            my $skip = $csz + ( $csz % 2 );
            seek $fh, $skip, 1;
        }
    }
    CORE::close $fh;

    return 0 unless defined $pcm_data && defined $rate && defined $sw;

    # AIFF is big-endian; convert to little-endian
    require Speech::Recognition::AudioData;
    $pcm_data = Speech::Recognition::AudioData::_byteswap( $pcm_data, $sw );
    $pcm_data = _stereo_to_mono( $pcm_data, $sw ) if $nch && $nch == 2;

    $self->_set_audio( $pcm_data, $rate, $sw );
    return 1;
}

# --- FLAC (decode via 'flac' command) ---

sub _try_open_flac ( $self, $filename ) {
    # Detect FLAC by magic bytes
    CORE::open my $fh, '<', $filename or return 0;
    binmode $fh;
    my $magic = '';
    read $fh, $magic, 4;
    CORE::close $fh;
    return 0 unless $magic eq 'fLaC';

    my $flac = eval { _find_flac() } or return 0;

    my ( $tmp_fh, $tmp_wav ) = tempfile( SUFFIX => '.wav', UNLINK => 0 );
    CORE::close $tmp_fh;
    push @{ $self->{_tmp_files} }, $tmp_wav;

    system( $flac, '--decode', '--silent', "--output-name=$tmp_wav", '--force', $filename ) == 0
        or croak "flac decoder failed for '$filename' (exit $?)";

    my $ok = _try_open_wav( $self, $tmp_wav );
    croak "Could not read FLAC-decoded WAV from '$tmp_wav'" unless $ok;
    return 1;
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

sub _set_audio ( $self, $pcm, $rate, $sw ) {
    croak "sample_width must be 1-4" unless $sw >= 1 && $sw <= 4;
    $self->{SAMPLE_RATE}  = $rate;
    $self->{SAMPLE_WIDTH} = $sw;
    $self->{FRAME_COUNT}  = int( length($pcm) / $sw );
    $self->{DURATION}     = $self->{FRAME_COUNT} / $rate;
    $self->{stream}       = Speech::Recognition::AudioFile::Stream->new( $pcm, $sw );
}

# Decode a 10-byte 80-bit extended float (AIFF sample rate field, big-endian).
sub _decode_80bit_float ($bytes) {
    my @b  = unpack( 'C10', $bytes );
    my $exp = ( ( $b[0] & 0x7F ) << 8 ) | $b[1];
    $exp -= 16383;    # unbias
    my $mantissa = 0;
    $mantissa = $mantissa * 256 + $b[$_] for 2 .. 9;
    return $mantissa * 2**( $exp - 63 );
}

sub _stereo_to_mono ( $data, $sw ) {
    my $fmt  = $sw == 1 ? 'C*' : $sw == 2 ? 'v*' : 'V*';
    my @s    = unpack( $fmt, $data );
    my $half = 2**( $sw * 8 - 1 );
    my $mod  = 2**( $sw * 8 );
    my @mono;
    for ( my $i = 0 ; $i < @s ; $i += 2 ) {
        my $l = $s[$i]     >= $half ? $s[$i]     - $mod : $s[$i];
        my $r = $s[ $i + 1 ] >= $half ? $s[ $i + 1 ] - $mod : $s[ $i + 1 ];
        my $m = int( ( $l + $r ) / 2 );
        push @mono, $m < 0 ? $m + $mod : $m;
    }
    return pack( $fmt, @mono );
}

sub _find_flac {
    for my $dir ( split /:/, ( $ENV{PATH} // '/usr/local/bin:/usr/bin:/bin' ) ) {
        my $exe = "$dir/flac";
        return $exe if -f $exe && -x $exe;
    }
    croak "FLAC tool not found on PATH";
}

1;

__END__

=head1 NOTES

=over 4

=item *

Only uncompressed PCM WAV files are supported.  Compressed WAV formats
(ADPCM, etc.) will cause an error.

=item *

FLAC decoding requires the C<flac> command to be on C<$PATH>.

=item *

Stereo audio is automatically downmixed to mono by averaging the two channels.

=back

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
