package Speech::Recognition::AudioData;

use v5.36;
use Carp      qw(croak);
use POSIX     qw(floor);
use File::Temp qw(tempfile);
use IPC::Open3 ();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::AudioData - Container for raw audio data

=head1 SYNOPSIS

    use Speech::Recognition::AudioData;

    # Typically obtained from Recognizer->record or Recognizer->listen
    my $audio = Speech::Recognition::AudioData->new(
        frame_data   => $raw_bytes,   # raw PCM bytes (little-endian)
        sample_rate  => 16000,        # Hz
        sample_width => 2,            # bytes per sample (1-4)
    );

    my $wav  = $audio->get_wav_data;
    my $flac = $audio->get_flac_data;

    # Create directly from a file
    my $audio2 = Speech::Recognition::AudioData->from_file('/path/to/file.wav');

=head1 DESCRIPTION

Represents mono PCM audio data.  The raw audio is stored as little-endian
signed integer samples (except for 8-bit, which is unsigned/unsigned-biased
at 128, following the WAV convention).

=cut

# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------

=head1 CONSTRUCTORS

=head2 new(%args)

    my $audio = Speech::Recognition::AudioData->new(
        frame_data   => $bytes,
        sample_rate  => 16000,
        sample_width => 2,
    );

All three arguments are required.  C<sample_width> must be 1, 2, 3, or 4.

=cut

sub new ( $class, %args ) {
    my $frame_data   = $args{frame_data}   // croak 'frame_data is required';
    my $sample_rate  = $args{sample_rate}  // croak 'sample_rate is required';
    my $sample_width = $args{sample_width} // croak 'sample_width is required';

    croak 'sample_rate must be a positive integer'
        unless $sample_rate > 0;
    croak 'sample_width must be between 1 and 4 inclusive'
        unless $sample_width >= 1 && $sample_width <= 4;

    return bless {
        frame_data   => $frame_data,
        sample_rate  => int($sample_rate),
        sample_width => int($sample_width),
    }, $class;
}

=head2 from_file($file_path)

Class method.  Creates an C<AudioData> instance from a WAV, AIFF, or FLAC file.

    my $audio = Speech::Recognition::AudioData->from_file('/path/to/file.wav');

=cut

sub from_file ( $class, $file_path ) {
    require Speech::Recognition::Recognizer;
    require Speech::Recognition::AudioFile;

    my $r      = Speech::Recognition::Recognizer->new;
    my $source = Speech::Recognition::AudioFile->new( filename => $file_path );
    my $audio;
    $source->with( sub ($src) { $audio = $r->record($src) } );
    return $audio;
}

# ---------------------------------------------------------------------------
# Accessors
# ---------------------------------------------------------------------------

=head1 ACCESSORS

=head2 frame_data

Raw PCM bytes (little-endian).

=head2 sample_rate

Samples per second (Hz).

=head2 sample_width

Bytes per sample (1–4).

=cut

sub frame_data   ($self) { $self->{frame_data} }
sub sample_rate  ($self) { $self->{sample_rate} }
sub sample_width ($self) { $self->{sample_width} }

# ---------------------------------------------------------------------------
# Public methods
# ---------------------------------------------------------------------------

=head1 METHODS

=head2 get_segment($start_ms, $end_ms)

Returns a new C<AudioData> instance containing only the audio between
C<$start_ms> and C<$end_ms> milliseconds.  Both arguments are optional and
default to the beginning and end of the audio respectively.

=cut

sub get_segment ( $self, $start_ms = undef, $end_ms = undef ) {
    croak 'start_ms must be non-negative'
        if defined $start_ms && $start_ms < 0;
    croak 'end_ms must be >= start_ms'
        if defined $end_ms && defined $start_ms && $end_ms < $start_ms;

    my $sr  = $self->{sample_rate};
    my $sw  = $self->{sample_width};
    my $len = length( $self->{frame_data} );

    my $start_byte =
        defined $start_ms
        ? int( ( $start_ms * $sr * $sw ) / 1000 )
        : 0;
    my $end_byte =
        defined $end_ms
        ? int( ( $end_ms * $sr * $sw ) / 1000 )
        : $len;

    $start_byte = 0    if $start_byte < 0;
    $end_byte   = $len if $end_byte > $len;

    return Speech::Recognition::AudioData->new(
        frame_data   => substr( $self->{frame_data}, $start_byte, $end_byte - $start_byte ),
        sample_rate  => $sr,
        sample_width => $sw,
    );
}

=head2 get_raw_data(%args)

Returns raw PCM bytes, optionally resampled and/or width-converted.

    my $raw = $audio->get_raw_data(convert_rate => 8000, convert_width => 2);

=cut

sub get_raw_data ( $self, %args ) {
    my $convert_rate  = $args{convert_rate};
    my $convert_width = $args{convert_width};

    croak 'convert_rate must be a positive integer'
        if defined $convert_rate && $convert_rate <= 0;
    croak 'convert_width must be between 1 and 4 inclusive'
        if defined $convert_width
        && ( $convert_width < 1 || $convert_width > 4 );

    my $raw = $self->{frame_data};
    my $sw  = $self->{sample_width};

    # 8-bit WAV uses unsigned samples centred at 128; treat as signed internally
    $raw = _bias( $raw, 1, -128 ) if $sw == 1;

    # Resample if needed
    if ( defined $convert_rate && $self->{sample_rate} != $convert_rate ) {
        $raw = _ratecv( $raw, $sw, $self->{sample_rate}, $convert_rate );
    }

    # Convert sample width if needed
    if ( defined $convert_width && $sw != $convert_width ) {
        $raw = _lin2lin( $raw, $sw, $convert_width );
        $sw  = $convert_width;
    }

    # Restore unsigned 8-bit convention for output
    $raw = _bias( $raw, 1, 128 ) if ( $convert_width // $self->{sample_width} ) == 1;

    return $raw;
}

=head2 get_wav_data(%args)

Returns the audio as a WAV file (bytes).  Suitable for writing directly to a
C<.wav> file or sending to an online API.

    my $wav = $audio->get_wav_data(convert_rate => 16000, convert_width => 2);

=cut

sub get_wav_data ( $self, %args ) {
    my $convert_rate  = $args{convert_rate};
    my $convert_width = $args{convert_width};
    my $raw           = $self->get_raw_data(%args);
    my $sample_rate   = $convert_rate  // $self->{sample_rate};
    my $sample_width  = $convert_width // $self->{sample_width};
    return _make_wav( $raw, $sample_rate, $sample_width );
}

=head2 get_aiff_data(%args)

Returns the audio as an AIFF-C file (bytes).

    my $aiff = $audio->get_aiff_data(convert_rate => 16000);

=cut

sub get_aiff_data ( $self, %args ) {
    my $convert_rate  = $args{convert_rate};
    my $convert_width = $args{convert_width};
    my $raw           = $self->get_raw_data(%args);
    my $sample_rate   = $convert_rate  // $self->{sample_rate};
    my $sample_width  = $convert_width // $self->{sample_width};

    # AIFF is big-endian; swap bytes of each sample
    $raw = _byteswap( $raw, $sample_width );
    return _make_aiff( $raw, $sample_rate, $sample_width );
}

=head2 get_flac_data(%args)

Returns the audio as a FLAC file (bytes).  Requires the C<flac> command-line
tool.  FLAC does not support 32-bit samples; if the source is 32-bit and
C<convert_width> is not specified, the output will be 24-bit.

    my $flac = $audio->get_flac_data(convert_rate => 16000);

=cut

sub get_flac_data ( $self, %args ) {
    # FLAC supports at most 24-bit samples
    if ( $self->{sample_width} > 3 && !exists $args{convert_width} ) {
        $args{convert_width} = 3;
    }
    my $wav = $self->get_wav_data(%args);
    return _wav_to_flac($wav);
}

# ---------------------------------------------------------------------------
# Private audio-processing helpers (analogous to Python's audioop module)
# ---------------------------------------------------------------------------

# Add a signed bias to every sample (like audioop.bias).
# $width must be 1, 2, 3, or 4.
sub _bias ( $data, $width, $delta ) {
    my $mod = 2**( $width * 8 );
    my @s = $width == 3 ? _unpack24($data) : unpack( _pack_fmt($width), $data );
    @s = map { ( $_ + $delta ) % $mod } @s;
    return $width == 3 ? _pack24(@s) : pack( _pack_fmt($width), @s );
}

# Compute RMS energy (like audioop.rms).
sub _rms ( $data, $width ) {
    my @s = $width == 3 ? _unpack24($data) : unpack( _pack_fmt($width), $data );
    my $n    = @s or return 0;
    my $half = 2**( $width * 8 - 1 );
    my $mod  = 2**( $width * 8 );

    # Convert unsigned representation to signed
    @s = map { $_ >= $half ? $_ - $mod : $_ } @s;

    my $sum = 0;
    $sum += $_ * $_ for @s;
    return sqrt( $sum / $n );
}

# Linear-interpolation sample-rate conversion (like audioop.ratecv).
# Returns resampled data as raw bytes.
sub _ratecv ( $data, $width, $inrate, $outrate ) {
    return $data if $inrate == $outrate;

    my @in = $width == 3 ? _unpack24($data) : unpack( _pack_fmt($width), $data );
    my $n    = @in or return $data;

    my $half = 2**( $width * 8 - 1 );
    my $mod  = 2**( $width * 8 );

    # To signed
    @in = map { $_ >= $half ? $_ - $mod : $_ } @in;

    my $out_n = int( $n * $outrate / $inrate + 0.5 );
    my @out;
    for my $i ( 0 .. $out_n - 1 ) {
        my $pos  = $i * $inrate / $outrate;
        my $idx0 = int($pos);
        my $idx1 = $idx0 + 1 < $n ? $idx0 + 1 : $idx0;
        my $frac = $pos - $idx0;
        my $s    = $in[$idx0] * ( 1.0 - $frac ) + $in[$idx1] * $frac;
        push @out, int( $s >= 0 ? $s + 0.5 : $s - 0.5 );
    }

    # Back to unsigned
    @out = map { $_ < 0 ? $_ + $mod : $_ } @out;
    return $width == 3 ? _pack24(@out) : pack( _pack_fmt($width), @out );
}

# Convert between sample widths (like audioop.lin2lin).
# Supports widths 1, 2, 3, and 4.
sub _lin2lin ( $data, $from_w, $to_w ) {
    return $data if $from_w == $to_w;

    my $from_mod  = 2**( $from_w * 8 );
    my $from_half = $from_mod / 2;
    my $to_mod    = 2**( $to_w * 8 );
    my $to_max    = $to_mod / 2 - 1;
    my $to_min    = -$to_mod / 2;

    my @s = $from_w == 3 ? _unpack24($data) : unpack( _pack_fmt($from_w), $data );

    # To signed
    @s = map { $_ >= $from_half ? $_ - $from_mod : $_ } @s;

    # Scale
    if ( $from_w < $to_w ) {
        my $shift = ( $to_w - $from_w ) * 8;
        @s = map { $_ * 2**$shift } @s;
    }
    else {
        my $shift = ( $from_w - $to_w ) * 8;
        @s = map { int( $_ / 2**$shift ) } @s;
    }

    # Clamp and convert to unsigned target
    @s = map {
        my $v = $_ > $to_max ? $to_max : $_ < $to_min ? $to_min : $_;
        $v < 0 ? $v + $to_mod : $v;
    } @s;

    return $to_w == 3 ? _pack24(@s) : pack( _pack_fmt($to_w), @s );
}

# Byte-swap all samples (for little-endian -> big-endian conversion).
sub _byteswap ( $data, $width ) {
    return $data if $width == 1;
    my $result = '';
    my $len    = length($data);
    for ( my $i = 0 ; $i < $len ; $i += $width ) {
        $result .= scalar reverse substr( $data, $i, $width );
    }
    return $result;
}

# pack format string for the given sample width (unsigned LE)
# NOTE: width=3 (24-bit) is NOT handled by this function; use _unpack24 / _pack24.
sub _pack_fmt ($width) {
    my %f = ( 1 => 'C*', 2 => 'v*', 4 => 'V*' );
    return $f{$width} // croak "Unsupported sample width: $width";
}

# Unpack little-endian unsigned 24-bit samples into an array of integers.
sub _unpack24 ($data) {
    my @out;
    my $len = length($data);
    for ( my $i = 0; $i + 2 < $len; $i += 3 ) {
        my ( $b0, $b1, $b2 ) = unpack( 'C C C', substr( $data, $i, 3 ) );
        push @out, $b0 | ( $b1 << 8 ) | ( $b2 << 16 );
    }
    return @out;
}

# Pack an array of unsigned 24-bit integers into little-endian bytes.
sub _pack24 (@vals) {
    my $out = '';
    for my $v (@vals) {
        $v &= 0xFFFFFF;
        $out .= pack( 'C C C', $v & 0xFF, ( $v >> 8 ) & 0xFF, ( $v >> 16 ) & 0xFF );
    }
    return $out;
}

# ---------------------------------------------------------------------------
# WAV / AIFF builders
# ---------------------------------------------------------------------------

sub _make_wav ( $raw, $rate, $sw ) {
    my $nch       = 1;
    my $bps       = $sw * 8;
    my $byte_rate = $rate * $nch * $sw;
    my $align     = $nch * $sw;
    my $data_sz   = length($raw);
    my $fmt       = pack( 'v v V V v v', 1, $nch, $rate, $byte_rate, $align, $bps );
    my $riff_sz   = 4 + 8 + length($fmt) + 8 + $data_sz;

    return "RIFF"
        . pack( 'V', $riff_sz ) . "WAVE"
        . "fmt "
        . pack( 'V', length($fmt) ) . $fmt
        . "data"
        . pack( 'V', $data_sz ) . $raw;
}

sub _make_aiff ( $raw, $rate, $sw ) {
    my $nch     = 1;
    my $nframes = int( length($raw) / $sw );
    my $bps     = $sw * 8;
    my $rate80  = _encode_80bit_float($rate);

    my $comm = pack( 'n N n', $nch, $nframes, $bps ) . $rate80;
    my $ssnd = pack( 'N N', 0, 0 ) . $raw;    # offset=0, blockSize=0

    my $form_body =
        "AIFF"
        . "COMM" . pack( 'N', length($comm) ) . $comm
        . "SSND" . pack( 'N', length($ssnd) ) . $ssnd;

    return "FORM" . pack( 'N', length($form_body) ) . $form_body;
}

# Encode an integer as a 10-byte IEEE 754 80-bit extended float (big-endian).
# Used for the AIFF sample-rate field.
my %_80BIT_CACHE = (
    8000  => "\x40\x0B\xFA\x00\x00\x00\x00\x00\x00\x00",
    11025 => "\x40\x0C\xAC\x44\x00\x00\x00\x00\x00\x00",
    16000 => "\x40\x0C\xFA\x00\x00\x00\x00\x00\x00\x00",
    22050 => "\x40\x0D\xAC\x44\x00\x00\x00\x00\x00\x00",
    32000 => "\x40\x0D\xFA\x00\x00\x00\x00\x00\x00\x00",
    44100 => "\x40\x0E\xAC\x44\x00\x00\x00\x00\x00\x00",
    48000 => "\x40\x0E\xBB\x80\x00\x00\x00\x00\x00\x00",
    96000 => "\x40\x0F\xBB\x80\x00\x00\x00\x00\x00\x00",
);

sub _encode_80bit_float ($value) {
    return $_80BIT_CACHE{$value} if exists $_80BIT_CACHE{$value};
    return "\x00" x 10          if $value == 0;

    my $exp        = floor( log($value) / log(2) );
    my $biased_exp = $exp + 16383;
    my $b0         = ( $biased_exp >> 8 ) & 0x7F;
    my $b1         = $biased_exp & 0xFF;

    # Mantissa = value * 2^(63 - exp); split into two 32-bit halves
    my $shift    = 63 - $exp;
    my $full     = $shift >= 0 ? $value * ( 2**$shift ) : int( $value / ( 2**( -$shift ) ) );
    my $mant_hi  = int( $full / 2**32 );
    my $mant_lo  = int( $full - $mant_hi * 2**32 );

    return pack( 'CC N N', $b0, $b1, $mant_hi, $mant_lo );
}

# ---------------------------------------------------------------------------
# FLAC conversion via the 'flac' command-line tool
# ---------------------------------------------------------------------------

sub _wav_to_flac ($wav_data) {
    my $flac = _find_flac();

    my ( $in_fh, $in_file ) = tempfile( SUFFIX => '.wav', UNLINK => 1 );
    binmode $in_fh;
    print {$in_fh} $wav_data;
    close $in_fh;

    my ( $out_fh, $out_file ) = tempfile( SUFFIX => '.flac', UNLINK => 1 );
    close $out_fh;

    system( $flac, '--silent', '--best', "--output-name=$out_file", '--force', $in_file ) == 0
        or croak "flac encoder failed (exit code $?)";

    open my $fh, '<', $out_file or croak "Cannot read FLAC output '$out_file': $!";
    binmode $fh;
    my $data = do { local $/; <$fh> };
    close $fh;

    return $data;
}

sub _find_flac {
    for my $dir ( split /:/, ( $ENV{PATH} // '/usr/local/bin:/usr/bin:/bin' ) ) {
        my $exe = "$dir/flac";
        return $exe if -f $exe && -x $exe;
    }
    croak
        "FLAC converter not found - install the 'flac' command-line tool "
        . "(e.g. 'apt-get install flac')";
}

1;

__END__

=head1 AUDIO PROCESSING NOTES

=over 4

=item *

8-bit WAV samples use an unsigned representation centred at 128 (the WAV
convention).  Internally they are treated as signed for arithmetic.

=item *

Sample-rate conversion uses linear interpolation.  For high-quality
resampling consider post-processing with C<sox>.

=item *

FLAC encoding and decoding requires the C<flac> command to be on C<$PATH>.
Install it with C<apt-get install flac> or your OS equivalent.

=back

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
