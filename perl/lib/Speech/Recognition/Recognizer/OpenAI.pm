package Speech::Recognition::Recognizer::OpenAI;

use v5.36;
use HTTP::Request ();
use Speech::Recognition::Recognizer::_Base qw();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer::OpenAI - OpenAI Whisper API recognition backend

=head1 SYNOPSIS

    # Key from argument or OPENAI_API_KEY environment variable
    my $text = $r->recognize_openai($audio,
        api_key  => $key,
        model    => 'whisper-1',
        language => 'en',
    );

=head1 DESCRIPTION

Uses the L<OpenAI Whisper API|https://platform.openai.com/docs/api-reference/audio>
to transcribe audio.

An API key is required.  It can be provided via:

=over 4

=item 1. The C<api_key> argument.

=item 2. The C<OPENAI_API_KEY> environment variable.

=back

=head1 ARGUMENTS

=over 4

=item * C<api_key> - OpenAI API key (or use C<OPENAI_API_KEY> env var)

=item * C<model> - Whisper model, default C<whisper-1>.  Also accepts
C<gpt-4o-transcribe> and C<gpt-4o-mini-transcribe>.

=item * C<language> - ISO 639-1 language code hint (optional)

=item * C<prompt> - optional text prompt to guide the model

=item * C<temperature> - sampling temperature, default 0

=item * C<response_format> - response format (C<json>, C<text>, etc.), default C<json>

=item * C<show_all> - return the full JSON response hash ref instead of the transcript

=back

=cut

use constant VALID_MODELS => {
    'whisper-1'              => 1,
    'gpt-4o-transcribe'      => 1,
    'gpt-4o-mini-transcribe' => 1,
};

sub recognize ( $self, $audio_data, %args ) {
    Speech::Recognition::Recognizer::_Base::assert_audio($audio_data);

    my $api_key  = $args{api_key} // $ENV{OPENAI_API_KEY}
        or die 'OpenAI API key required (api_key arg or OPENAI_API_KEY env var)';
    my $model    = $args{model}    // 'whisper-1';
    my $show_all = $args{show_all} // 0;

    die "Unknown model '$model'"
        unless exists VALID_MODELS->{$model};

    my $wav = $audio_data->get_wav_data;

    # Build multipart/form-data body
    my @fields = ( [ 'model', $model ] );
    push @fields, [ 'language',    $args{language}        ] if defined $args{language};
    push @fields, [ 'prompt',      $args{prompt}          ] if defined $args{prompt};
    push @fields, [ 'temperature', $args{temperature}     ] if defined $args{temperature};
    my $fmt = $args{response_format} // 'json';
    push @fields, [ 'response_format', $fmt ];

    my ( $ct, $body ) = Speech::Recognition::Recognizer::_Base::build_multipart(
        \@fields,
        [ [ 'file', 'audio.wav', 'audio/wav', $wav ] ],
    );

    my $url = 'https://api.openai.com/v1/audio/transcriptions';
    my $ua  = Speech::Recognition::Recognizer::_Base::make_ua(
        $self->{operation_timeout} // 60
    );
    my $req = HTTP::Request->new(
        POST => $url,
        [
            'Authorization' => "Bearer $api_key",
            'Content-Type'  => $ct,
        ],
        $body,
    );

    my $res = $ua->request($req);
    unless ( $res->is_success ) {
        Speech::Recognition::Recognizer::_Base::throw_request(
            'OpenAI Whisper request failed: ' . $res->status_line
        );
    }

    if ( $fmt eq 'json' || $fmt eq 'verbose_json' ) {
        my $result = Speech::Recognition::Recognizer::_Base::decode_json( $res->content );
        return $result if $show_all;
        return $result->{text};
    }

    return $res->content;
}

1;

__END__

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
