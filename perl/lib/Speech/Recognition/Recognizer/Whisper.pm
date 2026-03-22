package Speech::Recognition::Recognizer::Whisper;

use v5.36;
use File::Temp qw(tempfile tempdir);
use Speech::Recognition::Recognizer::_Base qw();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer::Whisper - Local OpenAI Whisper recognition backend

=head1 SYNOPSIS

    my $text = $r->recognize_whisper_local($audio,
        model           => 'base',
        language        => 'en',
        response_format => 'srt',
    );

=head1 DESCRIPTION

Runs speech recognition locally using a Whisper command-line binary.  No API
key or internet connection is required at inference time.

The following binaries are searched on C<$PATH> in order:

=over 4

=item 1. C<whisper> — the official openai-whisper CLI
(C<pip install openai-whisper>).

=item 2. C<whisper-cpp> — a pure C++ re-implementation with no Python
dependency (L<https://github.com/ggerganov/whisper.cpp>).  Supports hardware
acceleration on Apple Silicon via Metal, NVIDIA GPUs via CUDA, and others.

=back

If neither binary is found a C<SetupError> is thrown with installation
instructions.

=head1 ARGUMENTS

=over 4

=item * C<model> - Whisper model name: C<tiny>, C<base>, C<small>, C<medium>,
C<large>, C<turbo>.  Default: C<base>.

=item * C<language> - ISO 639-1 language code hint (e.g. C<en>, C<fr>).
When omitted Whisper auto-detects the language.

=item * C<task> - C<transcribe> (default) or C<translate>.

=item * C<response_format> - Output format: C<json> (default), C<verbose_json>,
C<text>, C<srt>, C<vtt>.  C<json> and C<verbose_json> both produce JSON output;
C<srt> and C<vtt> produce subtitle files with timestamps; C<text> produces
plain text.

=item * C<show_all> - When C<response_format> is C<json> or C<verbose_json>,
return the full decoded JSON hash instead of just the transcript string.
Ignored for other formats.

=back

=cut

# ---------------------------------------------------------------------------
# Binary search order: whisper → whisper-cpp
# ---------------------------------------------------------------------------

my @_WHISPER_BINS = qw( whisper whisper-cpp );

sub _find_whisper_bin () {
    for my $name (@_WHISPER_BINS) {
        my $bin = Speech::Recognition::Recognizer::_Base::which($name);
        return ( $bin, $name ) if defined $bin;
    }
    return;
}

# ---------------------------------------------------------------------------
# Format map: response_format → [ openai-whisper fmt, whisper-cpp flag, ext ]
# ---------------------------------------------------------------------------

my %_FORMAT_MAP = (
    json         => [ 'json', '--output-json', 'json' ],
    verbose_json => [ 'json', '--output-json', 'json' ],
    text         => [ 'txt',  '--output-txt',  'txt'  ],
    srt          => [ 'srt',  '--output-srt',  'srt'  ],
    vtt          => [ 'vtt',  '--output-vtt',  'vtt'  ],
);

# ---------------------------------------------------------------------------
# Internal: run the located whisper binary and return output file content
# ---------------------------------------------------------------------------

# whisper (openai-whisper) uses a Python-style CLI interface;
# whisper-cpp uses slightly different flags.
sub _run_whisper ( $bin, $name, $wav_file, $model, $language, $task, $out_dir, $fmt ) {
    my $fmap = $_FORMAT_MAP{$fmt};
    my @cmd;

    if ( $name eq 'whisper-cpp' ) {
        # whisper.cpp CLI uses different flag names
        @cmd = (
            $bin,
            '--model'       => $model,
            $fmap->[1],                         # e.g. --output-srt
            '--output-file' => "$out_dir/output",
        );
        push @cmd, '--language', $language if defined $language;
        push @cmd, '--translate' if defined $task && $task eq 'translate';
        push @cmd, $wav_file;
    }
    else {
        # openai-whisper CLI interface
        @cmd = (
            $bin,
            '--model'         => $model,
            '--output_format' => $fmap->[0],    # e.g. srt
            '--output_dir'    => $out_dir,
            '--task'          => ( $task // 'transcribe' ),
        );
        push @cmd, '--language', $language if defined $language;
        push @cmd, $wav_file;
    }

    # whisper writes results to output files in $out_dir, not to stdout.
    # run_cmd captures stdout/stderr and throws RequestError on failure.
    Speech::Recognition::Recognizer::_Base::run_cmd(@cmd);

    # Locate the output file whisper wrote
    my $ext      = $fmap->[2];
    my $out_file;
    if ( $name eq 'whisper-cpp' ) {
        $out_file = "$out_dir/output.$ext";
    }
    else {
        ( my $basename = $wav_file ) =~ s{.*/}{};
        $basename =~ s/\.[^.]+$//;
        $out_file = "$out_dir/$basename.$ext";
    }

    open my $fh, '<', $out_file
        or Speech::Recognition::Recognizer::_Base::throw_request(
            "whisper did not write expected output file '$out_file'"
        );
    local $/;
    my $content = <$fh>;
    close $fh;

    return $content;
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

sub recognize ( $self, $audio_data, %args ) {
    Speech::Recognition::Recognizer::_Base::assert_audio($audio_data);

    my $model    = $args{model}           // 'base';
    my $language = $args{language};
    my $task     = $args{task}            // 'transcribe';
    my $fmt      = $args{response_format} // 'json';
    my $show_all = $args{show_all}        // 0;

    Speech::Recognition::Recognizer::_Base::throw_setup(
        "Unknown response_format '$fmt'; valid: json verbose_json text srt vtt"
    ) unless exists $_FORMAT_MAP{$fmt};

    my ( $bin, $name ) = _find_whisper_bin();
    unless ( defined $bin ) {
        Speech::Recognition::Recognizer::_Base::throw_setup(
            'No whisper binary found on PATH. Options:'
          . "\n  whisper     — pip install openai-whisper"
          . "\n  whisper-cpp — https://github.com/ggerganov/whisper.cpp"
          . "\n               (no Python required; Metal/CUDA acceleration supported)"
        );
    }

    # Write audio to a temporary WAV file that whisper can consume
    my $wav = $audio_data->get_wav_data;
    my ( $in_fh, $in_file ) = tempfile( SUFFIX => '.wav', UNLINK => 1 );
    binmode $in_fh;
    print {$in_fh} $wav;
    close $in_fh;

    my $out_dir = tempdir( CLEANUP => 1 );
    my $content = _run_whisper( $bin, $name, $in_file, $model, $language, $task, $out_dir, $fmt );

    # JSON formats: decode and return hash or text field
    if ( $fmt eq 'json' || $fmt eq 'verbose_json' ) {
        my $result = Speech::Recognition::Recognizer::_Base::decode_json($content);
        return $result if $show_all;
        my $text = $result->{text} // '';
        $text =~ s/^\s+|\s+$//g;
        Speech::Recognition::Recognizer::_Base::throw_unknown() unless length $text;
        return $text;
    }

    # text format: return trimmed plain text
    if ( $fmt eq 'text' ) {
        ( my $text = $content ) =~ s/^\s+|\s+$//g;
        Speech::Recognition::Recognizer::_Base::throw_unknown() unless length $text;
        return $text;
    }

    # srt / vtt: return the subtitle content as-is
    return $content;
}

1;

__END__

=head1 INSTALLATION

Install one of the following:

=over 4

=item * B<openai-whisper> (cross-platform):

    pip install openai-whisper

=item * B<whisper.cpp> (C++, no Python required, hardware-accelerated):

    git clone https://github.com/ggerganov/whisper.cpp
    cd whisper.cpp && make
    ./models/download-ggml-model.sh base.en
    # add the build directory to $PATH

whisper.cpp uses Metal automatically on Apple Silicon, CUDA on NVIDIA GPUs, and
falls back to CPU on other hardware.

=back

Model weights for openai-whisper are downloaded on first use and cached in
C<~/.cache/whisper>.  Subsequent runs are fully offline.

=head1 NOTES

Local inference can be slow without a GPU.  The C<tiny> and C<base> models are
fastest and work well for simple transcription tasks.  The C<turbo> model
(a distilled Whisper v3 variant) offers a good speed/quality trade-off.

On Apple Silicon Macs, C<whisper-cpp> delivers significantly faster inference
than CPU-only C<whisper> by offloading computation to the GPU via its built-in
Metal backend.

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
