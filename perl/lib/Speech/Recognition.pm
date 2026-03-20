package Speech::Recognition;

use v5.36;

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition - Perl library for speech recognition, with support for
several engines and APIs, online and offline

=head1 SYNOPSIS

    use Speech::Recognition;

    my $r = Speech::Recognition::Recognizer->new;

    # Recognise from a WAV/AIFF/FLAC file
    my $audio;
    Speech::Recognition::AudioFile->new(filename => 'speech.wav')->with(sub ($src) {
        $audio = $r->record($src);
    });

    # Use one of many backends
    my $text = $r->recognize_google($audio);
    my $text = $r->recognize_openai($audio, api_key => $ENV{OPENAI_API_KEY});
    my $text = $r->recognize_groq($audio,   api_key => $ENV{GROQ_API_KEY});
    my $text = $r->recognize_wit($audio,    key     => $wit_key);
    my $text = $r->recognize_azure($audio,  key     => $az_key,   location => 'eastus');
    my $text = $r->recognize_ibm($audio,    key     => $ibm_key);
    my $text = $r->recognize_houndify($audio,
        client_id  => $hound_id,
        client_key => $hound_key,
    );

    # Adjust threshold to ambient noise before recording
    Speech::Recognition::Microphone->new->with(sub ($mic) {
        $r->adjust_for_ambient_noise($mic, 1);
        my $audio = $r->listen($mic, timeout => 10);
        print $r->recognize_google($audio);
    });

=head1 DESCRIPTION

C<Speech::Recognition> is a Perl port of the Python
L<SpeechRecognition|https://pypi.org/project/SpeechRecognition/> library by
Anthony Zhang (Uberi).

The library provides a unified, backend-agnostic API for speech recognition.
Audio can come from:

=over 4

=item * Audio files: WAV (PCM), AIFF/AIFF-C, native FLAC
(L<Speech::Recognition::AudioFile>)

=item * A microphone via C<arecord> or C<sox>
(L<Speech::Recognition::Microphone>)

=back

Supported online recognition backends:

=over 4

=item * B<Google Speech API v2> (legacy) – L<Speech::Recognition::Recognizer::Google>

=item * B<Wit.ai> – L<Speech::Recognition::Recognizer::Wit>

=item * B<Microsoft Azure Speech> – L<Speech::Recognition::Recognizer::Azure>

=item * B<Microsoft Bing Speech> (legacy) – L<Speech::Recognition::Recognizer::Bing>

=item * B<Houndify> – L<Speech::Recognition::Recognizer::Houndify>

=item * B<IBM Watson Speech to Text> – L<Speech::Recognition::Recognizer::IBM>

=item * B<OpenAI Whisper API> – L<Speech::Recognition::Recognizer::OpenAI>

=item * B<Groq Whisper API> – L<Speech::Recognition::Recognizer::Groq>

=back

Offline recognition (PocketSphinx, Vosk, local Whisper) is not yet
implemented in this Perl port.  See F<TODO.md> for details.

=head1 QUICK IMPORT

Importing C<Speech::Recognition> does I<not> export anything.  Access
classes directly by their full name, or assign convenient aliases:

    use Speech::Recognition;

    my $Recognizer = 'Speech::Recognition::Recognizer';
    my $AudioFile  = 'Speech::Recognition::AudioFile';
    my $Microphone = 'Speech::Recognition::Microphone';

=head1 EXCEPTIONS

All exceptions inherit from C<Speech::Recognition::Exception>.

    eval { $r->recognize_google($audio) };
    if ( ref $@ && $@->isa('Speech::Recognition::Exception::UnknownValueError') ) {
        warn "Could not understand audio\n";
    }
    elsif ( ref $@ && $@->isa('Speech::Recognition::Exception::RequestError') ) {
        warn "API error: " . $@->message . "\n";
    }

=head1 PERL vs PYTHON DIFFERENCES

=over 4

=item * Python uses C<with ... as source:> for audio sources.  In Perl use
C<< $source->with(sub ($src) { ... }) >> or manual C<open>/C<close>.

=item * Python's C<audioop> library is replaced by pure-Perl audio helpers in
L<Speech::Recognition::AudioData>.  For production use consider C<sox> for
high-quality resampling.

=item * Offline backends (PocketSphinx, Vosk, Whisper-local) require FFI or
subprocess wrappers not yet implemented.  See F<TODO.md>.

=item * Microphone capture uses C<arecord> or C<rec> (from C<sox>) instead of
PyAudio.

=back

=head1 VERSION

0.01

=cut

# Pull in the main classes so a single C<use Speech::Recognition> is enough.
use Speech::Recognition::Exception  ();
use Speech::Recognition::AudioData  ();
use Speech::Recognition::AudioFile  ();
use Speech::Recognition::Microphone ();
use Speech::Recognition::Recognizer ();

1;

__END__

=head1 AUTHOR

Perl port of the Python SpeechRecognition library by Anthony Zhang (Uberi).

Original Python library: L<https://github.com/Uberi/speech_recognition>

Perl port: L<https://github.com/trbutler/speech_recognition>

=head1 LICENSE

BSD 3-Clause License

=head1 SEE ALSO

L<Speech::Recognition::Recognizer>,
L<Speech::Recognition::AudioFile>,
L<Speech::Recognition::AudioData>,
L<Speech::Recognition::Microphone>,
L<Speech::Recognition::Exception>

=cut
