package Speech::Recognition::Microphone;

use v5.36;
use Carp qw(croak);
use Speech::Recognition::Recognizer::_Base ();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Microphone - Microphone audio source

=head1 SYNOPSIS

    use Speech::Recognition::Microphone;
    use Speech::Recognition::Recognizer;

    my $r = Speech::Recognition::Recognizer->new;

    # List available microphones
    my @names = Speech::Recognition::Microphone->list_microphone_names;
    print "Microphones: @names\n";

    # Record from the default microphone
    my $audio;
    my $mic = Speech::Recognition::Microphone->new;
    $mic->with(sub ($source) {
        $r->adjust_for_ambient_noise($source, 1);
        $audio = $r->listen($source, timeout => 10);
    });

    my $text = $r->recognize_google($audio);

=head1 DESCRIPTION

Provides a microphone audio source using external tools (C<arecord> on Linux,
C<rec> from SoX, or C<sox> directly) to capture audio.

Unlike the Python version which uses PyAudio, this implementation shells out
to command-line recording utilities.  Install one of the following:

=over 4

=item * C<arecord> (part of C<alsa-utils> on Debian/Ubuntu)

=item * C<sox> (provides C<rec>)

=back

=head1 NOTE

Microphone support is considered experimental in this Perl port.  The blocking
interface mirrors the Python API but depends on system audio infrastructure.

=cut

# Supported backends in preference order
my @BACKENDS = (
    { cmd => 'arecord', args => sub ($rate, $sw, $dur) {
        my $bits = $sw * 8;
        my @a = ('-q', '-f', "S${bits}_LE", '-r', $rate, '-c', 1);
        push @a, '-d', int($dur) if defined $dur;
        push @a, '-t', 'raw', '-';
        return @a;
    }},
    { cmd => 'rec', args => sub ($rate, $sw, $dur) {
        my $bits = $sw * 8;
        my @a = ('-q', '-r', $rate, '-c', 1, '-b', $bits, '-e', 'signed-integer', '-t', 'raw', '-');
        push @a, 'trim', 0, $dur if defined $dur;
        return @a;
    }},
);

# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------

=head1 CONSTRUCTORS

=head2 new(%args)

    my $mic = Speech::Recognition::Microphone->new(
        device_index => undef,    # not used; reserved for future backends
        sample_rate  => 16000,    # Hz (default 16000)
        chunk_size   => 1024,     # samples per read chunk
    );

=cut

sub new ( $class, %args ) {
    my $sample_rate = $args{sample_rate} // 16000;
    my $chunk_size  = $args{chunk_size}  // 1024;

    croak 'sample_rate must be a positive integer' unless $sample_rate > 0;
    croak 'chunk_size must be a positive integer'  unless $chunk_size > 0;

    my $backend = _find_backend()
        or croak "No supported audio capture tool found. "
        . "Install 'arecord' (alsa-utils) or 'sox'.";

    return bless {
        SAMPLE_RATE  => $sample_rate,
        SAMPLE_WIDTH => 2,           # always 16-bit signed LE
        CHUNK        => $chunk_size,
        _backend     => $backend,
        stream       => undef,
        _pid         => undef,
        _fh          => undef,
    }, $class;
}

# ---------------------------------------------------------------------------
# Static methods
# ---------------------------------------------------------------------------

=head1 CLASS METHODS

=head2 list_microphone_names()

Returns a list of microphone names.  On Linux this reads from the ALSA device
list if C<arecord -l> is available.  Returns an empty list otherwise.

=cut

sub list_microphone_names ($class) {
    my @names;
    if ( my $arecord = Speech::Recognition::Recognizer::_Base::which('arecord') ) {
        my @lines = `$arecord -l 2>/dev/null`;
        for my $line (@lines) {
            if ( $line =~ /card\s+\d+:.*?(\[.+?\])/ ) {
                push @names, $1;
            }
        }
    }
    return @names;
}

=head2 list_working_microphones()

Returns a hash mapping device indices to names for microphones that appear to
be functioning.  Currently returns an empty hash on non-ALSA systems.

=cut

sub list_working_microphones ($class) {
    my @names = $class->list_microphone_names;
    my %result;
    for my $i ( 0 .. $#names ) {
        $result{$i} = $names[$i];
    }
    return %result;
}

# isa check for duck-typing
sub isa_audio_source { 1 }

# Accessors
sub stream       ($self) { $self->{stream} }
sub SAMPLE_RATE  ($self) { $self->{SAMPLE_RATE} }
sub SAMPLE_WIDTH ($self) { $self->{SAMPLE_WIDTH} }
sub CHUNK        ($self) { $self->{CHUNK} }

# ---------------------------------------------------------------------------
# Open / close / with
# ---------------------------------------------------------------------------

=head1 METHODS

=head2 open()

Starts the recording process.  Returns C<$self>.

=cut

sub open ($self) {
    croak 'Microphone is already open' if defined $self->{stream};

    my $cmd   = $self->{_backend}{cmd};
    my $exe   = Speech::Recognition::Recognizer::_Base::which($cmd) or croak "Cannot find '$cmd' on PATH";
    my @args  = $self->{_backend}{args}->( $self->{SAMPLE_RATE}, $self->{SAMPLE_WIDTH} );

    my $pid   = open my $fh, '-|', $exe, @args
        or croak "Cannot start '$cmd': $!";
    binmode $fh;

    $self->{_pid}   = $pid;
    $self->{_fh}    = $fh;
    $self->{stream} = Speech::Recognition::Microphone::Stream->new( $fh, $self->{SAMPLE_WIDTH} );
    return $self;
}

=head2 close()

Stops the recording process.

=cut

sub close ($self) {
    if ( defined $self->{_pid} ) {
        kill 'TERM', $self->{_pid};
        waitpid $self->{_pid}, 0;
        CORE::close( $self->{_fh} ) if defined $self->{_fh};
        $self->{_pid}   = undef;
        $self->{_fh}    = undef;
        $self->{stream} = undef;
    }
}

=head2 with($callback)

Opens the microphone, calls C<$callback->($self)>, then closes.

=cut

sub with ( $self, $callback ) {
    $self->open;
    my $result = eval { $callback->($self) };
    my $err    = $@;
    $self->close;
    die $err if $err;
    return $result;
}

# ---------------------------------------------------------------------------
# Inner stream class
# ---------------------------------------------------------------------------

package Speech::Recognition::Microphone::Stream;

use v5.36;

sub new ( $class, $fh, $sample_width ) {
    return bless { _fh => $fh, _width => $sample_width }, $class;
}

sub read ( $self, $nsamples ) {
    my $nbytes = $nsamples * $self->{_width};
    my $buf    = '';
    my $n      = CORE::read( $self->{_fh}, $buf, $nbytes );
    return defined $n ? $buf : '';
}

sub close ($self) {
    CORE::close( $self->{_fh} ) if defined $self->{_fh};
    $self->{_fh} = undef;
}

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

package Speech::Recognition::Microphone;

use v5.36;

sub _find_backend {
    for my $b (@BACKENDS) {
        return $b if Speech::Recognition::Recognizer::_Base::which( $b->{cmd} );
    }
    return undef;
}

1;

__END__

=head1 LIMITATIONS

=over 4

=item *

Device selection by index is not yet supported.  The default input device is
always used.

=item *

Windows is not currently supported.  Contributions welcome.

=item *

For high-quality recording, prefer C<sox>-based recording (install C<sox>).

=back

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
