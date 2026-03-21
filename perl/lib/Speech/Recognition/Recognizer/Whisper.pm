package Speech::Recognition::Recognizer::Whisper;

use v5.36;
use File::Temp qw(tempfile tempdir);
use IPC::Open3 ();
use Speech::Recognition::Recognizer::_Base qw();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer::Whisper - Local OpenAI Whisper recognition backend

=head1 SYNOPSIS

    my $text = $r->recognize_whisper_local($audio,
        model    => 'base',
        language => 'en',
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

=item * C<show_all> - Return the full JSON result hash instead of just the
transcript string.

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
# Internal: run the located whisper binary and parse its JSON output
# ---------------------------------------------------------------------------

# whisper (openai-whisper) and whisper-mps share the same CLI surface;
# whisper-cpp uses slightly different flags.
sub _run_whisper ( $bin, $name, $wav_file, $model, $language, $task, $out_dir ) {
    my @cmd;

    if ( $name eq 'whisper-cpp' ) {
        # whisper.cpp CLI uses different flag names
        @cmd = (
            $bin,
            '--model'       => $model,
            '--output-json',
            '--output-file' => "$out_dir/output",
        );
        push @cmd, '--language', $language if defined $language;
        push @cmd, '--translate' if defined $task && $task eq 'translate';
        push @cmd, $wav_file;
    }
    else {
        # openai-whisper and whisper-mps share the same CLI interface
        @cmd = (
            $bin,
            '--model'         => $model,
            '--output_format' => 'json',
            '--output_dir'    => $out_dir,
            '--task'          => ( $task // 'transcribe' ),
        );
        push @cmd, '--language', $language if defined $language;
        push @cmd, $wav_file;
    }

    # Run and drain stderr (whisper prints verbose progress there) to prevent
    # the child process from blocking on a full pipe buffer.
    my ( $child_in, $child_out, $child_err );
    my $pid = IPC::Open3::open3( $child_in, $child_err, $child_err, @cmd );
    close $child_in;

    my $err_text = '';
    while ( defined( my $line = <$child_err> ) ) {
        $err_text .= $line;
    }
    waitpid $pid, 0;
    my $exit = $? >> 8;

    if ( $exit != 0 ) {
        Speech::Recognition::Recognizer::_Base::throw_request(
            "whisper failed (exit $exit): $err_text"
        );
    }

    # Locate the output JSON file whisper wrote into $out_dir
    my $json_file;
    if ( $name eq 'whisper-cpp' ) {
        $json_file = "$out_dir/output.json";
    }
    else {
        ( my $basename = $wav_file ) =~ s{.*/}{};
        $basename =~ s/\.[^.]+$//;
        $json_file = "$out_dir/$basename.json";
    }

    open my $fh, '<', $json_file
        or Speech::Recognition::Recognizer::_Base::throw_request(
            "whisper did not write expected output file '$json_file'"
        );
    local $/;
    my $json = <$fh>;
    close $fh;

    return Speech::Recognition::Recognizer::_Base::decode_json($json);
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

sub recognize ( $self, $audio_data, %args ) {
    Speech::Recognition::Recognizer::_Base::assert_audio($audio_data);

    my $model    = $args{model}    // 'base';
    my $language = $args{language};
    my $task     = $args{task}     // 'transcribe';
    my $show_all = $args{show_all} // 0;

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
    my $result  = _run_whisper( $bin, $name, $in_file, $model, $language, $task, $out_dir );

    return $result if $show_all;

    my $text = $result->{text} // '';
    $text =~ s/^\s+|\s+$//g;
    Speech::Recognition::Recognizer::_Base::throw_unknown() unless length $text;
    return $text;
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
