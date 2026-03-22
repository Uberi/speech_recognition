package Speech::Recognition::Recognizer::Yap;

use v5.36;
use File::Temp qw(tempfile);
use Speech::Recognition::Recognizer::_Base qw();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer::Yap - macOS on-device speech recognition via Yap

=head1 SYNOPSIS

    # Plain text (default)
    my $text = $r->recognize_yap($audio);

    # SRT subtitles with timestamps
    my $srt = $r->recognize_yap($audio,
        response_format => 'srt',
        language        => 'en-US',
    );

    # JSON with segment metadata
    my $data = $r->recognize_yap($audio,
        response_format => 'json',
        show_all        => 1,
    );

=head1 DESCRIPTION

Uses L<Yap|https://github.com/finnvoor/yap> to transcribe audio entirely
on-device via Apple's Speech framework.  No API key or internet connection is
required.  Yap is available on macOS only and requires macOS with an up-to-date
Speech framework (macOS Sequoia / Tahoe or later recommended for best results).

Install Yap with Homebrew:

    brew install yap

=head1 ARGUMENTS

=over 4

=item * C<response_format> - Output format.  Default: C<text>.

=over 8

=item C<text> - plain transcript (default)

=item C<srt> - SubRip subtitle file with timestamps

=item C<vtt> - WebVTT subtitle file with timestamps

=item C<json> - JSON with per-segment metadata (see C<show_all>)

=item C<verbose_json> - alias for C<json>

=back

=item * C<language> - BCP-47 locale string (e.g. C<en-US>, C<ja-JP>).
Defaults to the system locale.

=item * C<show_all> - When C<response_format> is C<json> or C<verbose_json>,
return the full decoded JSON hash instead of just the transcript string.
The hash has the shape:

    {
        metadata => { created => '...', language => '...', duration => ... },
        segments => [
            { id => 1, start => 0.0, end => 1.5, text => '...' },
            ...
        ],
    }

Ignored for other formats.

=back

=cut

# ---------------------------------------------------------------------------
# Format map: response_format → yap CLI flag
# ---------------------------------------------------------------------------

my %_FORMAT_FLAG = (
    text         => '--txt',
    srt          => '--srt',
    vtt          => '--vtt',
    json         => '--json',
    verbose_json => '--json',   # yap has no verbose_json; map to --json
);

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

sub _find_yap_bin () {
    return Speech::Recognition::Recognizer::_Base::which('yap');
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

sub recognize ( $self, $audio_data, %args ) {
    Speech::Recognition::Recognizer::_Base::assert_audio($audio_data);

    my $fmt      = $args{response_format} // 'text';
    my $language = $args{language};
    my $show_all = $args{show_all} // 0;

    Speech::Recognition::Recognizer::_Base::throw_setup(
        "Unknown response_format '$fmt'; valid: text srt vtt json verbose_json"
    ) unless exists $_FORMAT_FLAG{$fmt};

    my $bin = _find_yap_bin();
    unless ( defined $bin ) {
        Speech::Recognition::Recognizer::_Base::throw_setup(
            'yap binary not found on PATH.'
          . "\n  Install: brew install yap"
          . "\n  Requires macOS with Apple Speech framework support."
        );
    }

    # Write audio to a temporary WAV file
    my $wav = $audio_data->get_wav_data;
    my ( $in_fh, $in_file ) = tempfile( SUFFIX => '.wav', UNLINK => 1 );
    binmode $in_fh;
    print {$in_fh} $wav;
    close $in_fh;

    # Build the command: yap transcribe [--txt|--srt|--vtt|--json] [--locale L] <file>
    my @cmd = ( $bin, 'transcribe', $_FORMAT_FLAG{$fmt} );
    push @cmd, '--locale', $language if defined $language;
    push @cmd, $in_file;

    # Yap writes output to stdout; run_cmd captures it.
    my ( $out_text ) = Speech::Recognition::Recognizer::_Base::run_cmd(@cmd);

    # JSON formats: decode and return hash or extracted transcript
    if ( $fmt eq 'json' || $fmt eq 'verbose_json' ) {
        my $result = Speech::Recognition::Recognizer::_Base::decode_json($out_text);
        return $result if $show_all;
        my $text = join ' ',
            map  { $_->{text} // '' }
            grep { defined $_->{text} }
            @{ $result->{segments} // [] };
        $text =~ s/^\s+|\s+$//g;
        Speech::Recognition::Recognizer::_Base::throw_unknown() unless length $text;
        return $text;
    }

    # text format: trim and validate
    if ( $fmt eq 'text' ) {
        ( my $text = $out_text ) =~ s/^\s+|\s+$//g;
        Speech::Recognition::Recognizer::_Base::throw_unknown() unless length $text;
        return $text;
    }

    # srt / vtt: return as-is (may be empty for silent audio)
    return $out_text;
}

1;

__END__

=head1 INSTALLATION

    brew install yap

Yap requires macOS.  It uses Apple's on-device Speech framework and does not
send audio to any external server.

=head1 NOTES

Yap leverages Apple's neural speech recognition engine, which runs entirely
on-device using the Neural Engine on Apple Silicon.  It is significantly faster
than Whisper for many workloads and produces high-quality results, especially
for English and other widely-supported locales.

The C<srt> and C<vtt> formats include timestamps that can be used for
paragraph formatting, chapter markers, or subtitle overlays.

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
