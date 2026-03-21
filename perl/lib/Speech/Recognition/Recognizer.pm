package Speech::Recognition::Recognizer;

use v5.36;
use Carp           qw(croak);
use POSIX          qw(ceil);
use threads;
use threads::shared qw(share);

use Speech::Recognition::AudioData  ();
use Speech::Recognition::Exception  ();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer - Core speech recognition engine

=head1 SYNOPSIS

    use Speech::Recognition::Recognizer;
    use Speech::Recognition::AudioFile;

    my $r = Speech::Recognition::Recognizer->new;

    # Record audio from a file
    my $audio;
    Speech::Recognition::AudioFile->new(filename => 'speech.wav')->with(sub ($src) {
        $audio = $r->record($src);
    });

    # Recognize using one of many backends
    my $text = $r->recognize_google($audio);
    my $text = $r->recognize_wit($audio, key => $wit_key);
    my $text = $r->recognize_openai($audio, api_key => $openai_key);

=head1 DESCRIPTION

C<Speech::Recognition::Recognizer> is the central class of the library.  It
manages audio capture (via C<record> and C<listen>) and dispatches to multiple
online speech-recognition backends.

=cut

# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------

=head1 CONSTRUCTORS

=head2 new(%args)

Creates a new C<Recognizer> instance.

    my $r = Speech::Recognition::Recognizer->new(
        energy_threshold                  => 300,
        dynamic_energy_threshold          => 1,
        dynamic_energy_adjustment_damping => 0.15,
        dynamic_energy_ratio              => 1.5,
        pause_threshold                   => 0.8,
        operation_timeout                 => undef,
        phrase_threshold                  => 0.3,
        non_speaking_duration             => 0.5,
    );

All arguments are optional.

=cut

sub new ( $class, %args ) {
    return bless {
        energy_threshold                  => $args{energy_threshold}                  // 300,
        dynamic_energy_threshold          => $args{dynamic_energy_threshold}          // 1,
        dynamic_energy_adjustment_damping => $args{dynamic_energy_adjustment_damping} // 0.15,
        dynamic_energy_ratio              => $args{dynamic_energy_ratio}              // 1.5,
        pause_threshold                   => $args{pause_threshold}                   // 0.8,
        operation_timeout                 => $args{operation_timeout},
        phrase_threshold                  => $args{phrase_threshold}                  // 0.3,
        non_speaking_duration             => $args{non_speaking_duration}             // 0.5,
    }, $class;
}

# ---------------------------------------------------------------------------
# Accessors / mutators
# ---------------------------------------------------------------------------

sub energy_threshold                  ($self)       { $self->{energy_threshold} }
sub set_energy_threshold              ($self, $v)   { $self->{energy_threshold} = $v }
sub dynamic_energy_threshold          ($self)       { $self->{dynamic_energy_threshold} }
sub set_dynamic_energy_threshold      ($self, $v)   { $self->{dynamic_energy_threshold} = $v }
sub dynamic_energy_adjustment_damping ($self)       { $self->{dynamic_energy_adjustment_damping} }
sub dynamic_energy_ratio              ($self)       { $self->{dynamic_energy_ratio} }
sub pause_threshold                   ($self)       { $self->{pause_threshold} }
sub operation_timeout                 ($self)       { $self->{operation_timeout} }
sub phrase_threshold                  ($self)       { $self->{phrase_threshold} }
sub non_speaking_duration             ($self)       { $self->{non_speaking_duration} }

# ---------------------------------------------------------------------------
# record
# ---------------------------------------------------------------------------

=head1 METHODS

=head2 record($source, %args)

Records audio from C<$source> (an open audio source such as
C<Speech::Recognition::AudioFile> or C<Speech::Recognition::Microphone>)
and returns an C<AudioData> instance.

Optional keyword arguments:

=over 4

=item * C<duration> - maximum seconds to record (records to end-of-stream if omitted)

=item * C<offset> - seconds to skip at the beginning

=back

=cut

sub record ( $self, $source, %args ) {
    _assert_source($source);
    my $duration = $args{duration};
    my $offset   = $args{offset};

    my $spb = $source->{CHUNK} / $source->{SAMPLE_RATE};    # seconds per buffer
    my ( $elapsed, $offset_elapsed, $offset_reached ) = ( 0, 0, !defined $offset );
    my @frames;

    while (1) {
        unless ($offset_reached) {
            $offset_elapsed += $spb;
            $offset_reached = 1 if $offset_elapsed > $offset;
        }

        my $buf = $source->{stream}->read( $source->{CHUNK} );
        last unless length $buf;

        if ($offset_reached) {
            $elapsed += $spb;
            last if defined $duration && $elapsed > $duration;
            push @frames, $buf;
        }
    }

    return Speech::Recognition::AudioData->new(
        frame_data   => join( '', @frames ),
        sample_rate  => $source->{SAMPLE_RATE},
        sample_width => $source->{SAMPLE_WIDTH},
    );
}

# ---------------------------------------------------------------------------
# adjust_for_ambient_noise
# ---------------------------------------------------------------------------

=head2 adjust_for_ambient_noise($source, $duration)

Listens to C<$source> for up to C<$duration> seconds (default 1) and adjusts
C<energy_threshold> to match the ambient noise level.

=cut

sub adjust_for_ambient_noise ( $self, $source, $duration = 1 ) {
    _assert_source($source);

    my $spb     = $source->{CHUNK} / $source->{SAMPLE_RATE};
    my $elapsed = 0;

    while (1) {
        $elapsed += $spb;
        last if $elapsed > $duration;

        my $buf = $source->{stream}->read( $source->{CHUNK} );
        my $energy = Speech::Recognition::AudioData::_rms( $buf, $source->{SAMPLE_WIDTH} );

        my $damping       = $self->{dynamic_energy_adjustment_damping}**$spb;
        my $target_energy = $energy * $self->{dynamic_energy_ratio};
        $self->{energy_threshold} =
            $self->{energy_threshold} * $damping + $target_energy * ( 1 - $damping );
    }
}

# ---------------------------------------------------------------------------
# listen
# ---------------------------------------------------------------------------

=head2 listen($source, %args)

Listens to C<$source> and returns an C<AudioData> instance representing one
spoken phrase.

Optional keyword arguments:

=over 4

=item * C<timeout> - seconds to wait for speech to start (throws
C<WaitTimeoutError> if exceeded)

=item * C<phrase_time_limit> - maximum seconds for a single phrase

=back

=cut

sub listen ( $self, $source, %args ) {
    _assert_source($source);
    my $timeout           = $args{timeout};
    my $phrase_time_limit = $args{phrase_time_limit};

    croak 'pause_threshold must be >= non_speaking_duration >= 0'
        unless $self->{pause_threshold} >= $self->{non_speaking_duration}
        && $self->{non_speaking_duration} >= 0;

    my $spb = $source->{CHUNK} / $source->{SAMPLE_RATE};
    my $pause_buf_count =
        int( ceil( $self->{pause_threshold} / $spb ) );
    my $phrase_buf_count =
        int( ceil( $self->{phrase_threshold} / $spb ) );
    my $non_speaking_buf_count =
        int( ceil( $self->{non_speaking_duration} / $spb ) );

    my $elapsed = 0;
    my $buf     = '';
    my ( $pause_count, $phrase_count ) = ( 0, 0 );
    my @frames;

    # Outer retry loop: keep trying until we get a phrase that is long enough
    # (matches Python's _listen outer while loop).
    while (1) {
        @frames = ();

        # Wait for speech to start
        while (1) {
            $elapsed += $spb;
            if ( defined $timeout && $elapsed > $timeout ) {
                Speech::Recognition::Exception::WaitTimeoutError->throw(
                    'listening timed out while waiting for phrase to start'
                );
            }

            $buf = $source->{stream}->read( $source->{CHUNK} );
            last unless length $buf;

            push @frames, $buf;
            shift @frames if @frames > $non_speaking_buf_count;

            my $energy =
                Speech::Recognition::AudioData::_rms( $buf, $source->{SAMPLE_WIDTH} );
            last if $energy > $self->{energy_threshold};

            if ( $self->{dynamic_energy_threshold} ) {
                my $damping = $self->{dynamic_energy_adjustment_damping}**$spb;
                my $target  = $energy * $self->{dynamic_energy_ratio};
                $self->{energy_threshold} =
                    $self->{energy_threshold} * $damping + $target * ( 1 - $damping );
            }
        }

        # Record until silence
        ( $pause_count, $phrase_count ) = ( 0, 0 );
        my $phrase_start = $elapsed;

        while (1) {
            $elapsed += $spb;
            if ( defined $phrase_time_limit && $elapsed - $phrase_start > $phrase_time_limit ) {
                last;
            }

            $buf = $source->{stream}->read( $source->{CHUNK} );
            last unless length $buf;

            push @frames, $buf;
            $phrase_count++;

            my $energy =
                Speech::Recognition::AudioData::_rms( $buf, $source->{SAMPLE_WIDTH} );
            if ( $energy > $self->{energy_threshold} ) {
                $pause_count = 0;
            }
            else {
                $pause_count++;
            }
            last if $pause_count > $pause_buf_count;

            if ( $self->{dynamic_energy_threshold} ) {
                my $damping = $self->{dynamic_energy_adjustment_damping}**$spb;
                my $target  = $energy * $self->{dynamic_energy_ratio};
                $self->{energy_threshold} =
                    $self->{energy_threshold} * $damping + $target * ( 1 - $damping );
            }
        }

        # Check if the phrase is long enough; if so, stop retrying
        # (matches Python: `if phrase_count >= phrase_buffer_count or len(buffer) == 0: break`)
        $phrase_count -= $pause_count;
        last if $phrase_count >= $phrase_buf_count || !length($buf);
    }

    # Drop trailing silence beyond non_speaking_duration
    my $excess = $pause_count - $non_speaking_buf_count;
    if ( $excess > 0 ) {
        splice @frames, -$excess;
    }

    return Speech::Recognition::AudioData->new(
        frame_data   => join( '', @frames ),
        sample_rate  => $source->{SAMPLE_RATE},
        sample_width => $source->{SAMPLE_WIDTH},
    );
}

# ---------------------------------------------------------------------------
# listen_in_background
# ---------------------------------------------------------------------------

=head2 listen_in_background($source, $callback, %args)

Spawns a background thread that continuously listens on C<$source> and calls
C<$callback->($recognizer, $audio_data)> for each detected phrase.

Returns a stopper sub.  Call it to stop the background listener:

    my $stop = $r->listen_in_background($source, \&my_callback);
    # ... do other things ...
    $stop->();           # request stop (returns immediately)
    $stop->(1);          # wait for the thread to finish

Optional keyword arguments:

=over 4

=item * C<phrase_time_limit>

=back

=cut

sub listen_in_background ( $self, $source, $callback, %args ) {
    my $phrase_time_limit = $args{phrase_time_limit};
    my $running = 1;
    share($running);

    my $thr = threads->create( sub {
        $source->open;
        while ($running) {
            eval {
                my $audio = $self->listen( $source,
                    timeout           => 1,
                    phrase_time_limit => $phrase_time_limit,
                );
                $callback->( $self, $audio ) if $running;
            };
            # WaitTimeoutError is normal; ignore it and keep looping
        }
        $source->close;
    } );
    $thr->detach;

    return sub ( $wait = 0 ) {
        $running = 0;
        $thr->join if $wait && $thr->is_running;
    };
}

# ---------------------------------------------------------------------------
# Recognition backends (delegate to separate modules)
# ---------------------------------------------------------------------------

=head2 recognize_google($audio_data, %args)

Recognizes speech using the (legacy) Google Speech Recognition API.

    my $text = $r->recognize_google($audio, language => 'en-US');

See L<Speech::Recognition::Recognizer::Google> for full documentation.

=cut

sub recognize_google ( $self, $audio_data, %args ) {
    require Speech::Recognition::Recognizer::Google;
    return Speech::Recognition::Recognizer::Google::recognize(
        $self, $audio_data, %args
    );
}

=head2 recognize_wit($audio_data, %args)

Recognizes speech using the Wit.ai API.

    my $text = $r->recognize_wit($audio, key => $key);

See L<Speech::Recognition::Recognizer::Wit>.

=cut

sub recognize_wit ( $self, $audio_data, %args ) {
    require Speech::Recognition::Recognizer::Wit;
    return Speech::Recognition::Recognizer::Wit::recognize(
        $self, $audio_data, %args
    );
}

=head2 recognize_azure($audio_data, %args)

Recognizes speech using the Microsoft Azure Speech API.

    my $text = $r->recognize_azure($audio,
        key      => $subscription_key,
        language => 'en-US',
        location => 'westus',
    );

See L<Speech::Recognition::Recognizer::Azure>.

=cut

sub recognize_azure ( $self, $audio_data, %args ) {
    require Speech::Recognition::Recognizer::Azure;
    return Speech::Recognition::Recognizer::Azure::recognize(
        $self, $audio_data, %args
    );
}

=head2 recognize_bing($audio_data, %args)

Recognizes speech using the Microsoft Bing Speech API (legacy).

See L<Speech::Recognition::Recognizer::Bing>.

=cut

sub recognize_bing ( $self, $audio_data, %args ) {
    require Speech::Recognition::Recognizer::Bing;
    return Speech::Recognition::Recognizer::Bing::recognize(
        $self, $audio_data, %args
    );
}

=head2 recognize_houndify($audio_data, %args)

Recognizes speech using the Houndify API.

    my $text = $r->recognize_houndify($audio,
        client_id  => $id,
        client_key => $key,
    );

See L<Speech::Recognition::Recognizer::Houndify>.

=cut

sub recognize_houndify ( $self, $audio_data, %args ) {
    require Speech::Recognition::Recognizer::Houndify;
    return Speech::Recognition::Recognizer::Houndify::recognize(
        $self, $audio_data, %args
    );
}

=head2 recognize_ibm($audio_data, %args)

Recognizes speech using the IBM Speech to Text API.

    my $text = $r->recognize_ibm($audio, key => $api_key, language => 'en-US');

See L<Speech::Recognition::Recognizer::IBM>.

=cut

sub recognize_ibm ( $self, $audio_data, %args ) {
    require Speech::Recognition::Recognizer::IBM;
    return Speech::Recognition::Recognizer::IBM::recognize(
        $self, $audio_data, %args
    );
}

=head2 recognize_openai($audio_data, %args)

Recognizes speech using the OpenAI Whisper API.

    my $text = $r->recognize_openai($audio,
        api_key => $key,       # or set OPENAI_API_KEY env var
        model   => 'whisper-1',
    );

See L<Speech::Recognition::Recognizer::OpenAI>.

=cut

sub recognize_openai ( $self, $audio_data, %args ) {
    require Speech::Recognition::Recognizer::OpenAI;
    return Speech::Recognition::Recognizer::OpenAI::recognize(
        $self, $audio_data, %args
    );
}

=head2 recognize_groq($audio_data, %args)

Recognizes speech using the Groq Whisper API.

    my $text = $r->recognize_groq($audio,
        api_key => $key,       # or set GROQ_API_KEY env var
        model   => 'whisper-large-v3-turbo',
    );

See L<Speech::Recognition::Recognizer::Groq>.

=cut

sub recognize_groq ( $self, $audio_data, %args ) {
    require Speech::Recognition::Recognizer::Groq;
    return Speech::Recognition::Recognizer::Groq::recognize(
        $self, $audio_data, %args
    );
}

=head2 recognize_assemblyai($audio_data, %args)

Recognizes speech using the AssemblyAI API.

Because transcription is asynchronous, the first call submits the job and
immediately throws a C<TranscriptionNotReady> exception whose C<job_name>
holds the transcription ID.  Poll for the result by calling again with
C<audio_data =E<gt> undef> and C<job_name =E<gt> $id>.

    # Submit
    eval { $r->recognize_assemblyai($audio, api_token => $token) };
    my $job_id = $@->job_name if ref $@ && $@->isa('..::TranscriptionNotReady');

    # Poll
    my $text = $r->recognize_assemblyai(undef,
        api_token => $token,
        job_name  => $job_id,
    );

See L<Speech::Recognition::Recognizer::AssemblyAI>.

=cut

sub recognize_assemblyai ( $self, $audio_data, %args ) {
    require Speech::Recognition::Recognizer::AssemblyAI;
    return Speech::Recognition::Recognizer::AssemblyAI::recognize(
        $self, $audio_data, %args
    );
}

=head2 recognize_google_cloud($audio_data, %args)

Recognizes speech using the Google Cloud Speech-to-Text V1 REST API.

    my $text = $r->recognize_google_cloud($audio,
        credentials_json => '/path/to/service-account.json',
        language         => 'en-US',
    );

See L<Speech::Recognition::Recognizer::GoogleCloud>.

=cut

sub recognize_google_cloud ( $self, $audio_data, %args ) {
    require Speech::Recognition::Recognizer::GoogleCloud;
    return Speech::Recognition::Recognizer::GoogleCloud::recognize(
        $self, $audio_data, %args
    );
}

=head2 recognize_whisper_local($audio_data, %args)

Recognizes speech locally using the C<whisper> or C<whisper-cpp> binary.
No API key or internet connection is required at inference time.  C<whisper-cpp>
supports hardware acceleration via Metal (Apple Silicon), CUDA (NVIDIA), and
other backends with no Python dependency.

    my $text = $r->recognize_whisper_local($audio,
        model    => 'base',
        language => 'en',
    );

See L<Speech::Recognition::Recognizer::Whisper>.

=cut

sub recognize_whisper_local ( $self, $audio_data, %args ) {
    require Speech::Recognition::Recognizer::Whisper;
    return Speech::Recognition::Recognizer::Whisper::recognize(
        $self, $audio_data, %args
    );
}

# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

sub _assert_source ($source) {
    croak 'Source must be an audio source (AudioFile or Microphone)'
        unless ref $source
        && ( $source->can('isa_audio_source') || $source->isa('Speech::Recognition::AudioFile') );
    croak 'Audio source must be opened before use (call ->open or ->with)'
        unless defined $source->{stream};
}

1;

__END__

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
