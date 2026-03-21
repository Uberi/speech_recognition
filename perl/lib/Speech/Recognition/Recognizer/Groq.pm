package Speech::Recognition::Recognizer::Groq;

use v5.36;
use HTTP::Request ();
use Speech::Recognition::Recognizer::_Base qw();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer::Groq - Groq Whisper API recognition backend

=head1 SYNOPSIS

    # Key from argument or GROQ_API_KEY environment variable
    my $text = $r->recognize_groq($audio,
        api_key => $key,
        model   => 'whisper-large-v3-turbo',
    );

=head1 DESCRIPTION

Uses the L<Groq|https://console.groq.com/> Whisper API to transcribe audio.
Groq provides extremely fast inference for Whisper models.

An API key is required.  It can be provided via:

=over 4

=item 1. The C<api_key> argument.

=item 2. The C<GROQ_API_KEY> environment variable.

=back

=head1 ARGUMENTS

=over 4

=item * C<api_key> - Groq API key (or use C<GROQ_API_KEY> env var)

=item * C<model> - Whisper model.  One of:
C<whisper-large-v3-turbo> (default), C<whisper-large-v3>.

=item * C<language> - ISO 639-1 language code hint (optional)

=item * C<prompt> - optional text prompt to guide the model

=item * C<temperature> - sampling temperature, default 0

=item * C<response_format> - C<json> (default) or C<text>

=item * C<show_all> - return the full JSON response hash ref

=back

=cut

sub recognize ( $self, $audio_data, %args ) {
    state %valid_models = map { $_ => 1 } qw(
        whisper-large-v3-turbo
        whisper-large-v3
    );

    Speech::Recognition::Recognizer::_Base::assert_audio($audio_data);

    my $api_key  = $args{api_key} // $ENV{GROQ_API_KEY}
        or Speech::Recognition::Recognizer::_Base::throw_setup(
            'Groq API key required (api_key arg or GROQ_API_KEY env var)');
    my $model    = $args{model}    // 'whisper-large-v3-turbo';
    my $show_all = $args{show_all} // 0;

    Speech::Recognition::Recognizer::_Base::throw_setup("Unknown Groq model '$model'")
        unless exists $valid_models{$model};

    my $wav = $audio_data->get_wav_data;

    my @fields = ( [ 'model', $model ] );
    push @fields, [ 'language',    $args{language}    ] if defined $args{language};
    push @fields, [ 'prompt',      $args{prompt}      ] if defined $args{prompt};
    push @fields, [ 'temperature', $args{temperature} ] if defined $args{temperature};
    my $fmt = $args{response_format} // 'json';
    push @fields, [ 'response_format', $fmt ];

    my ( $ct, $body ) = Speech::Recognition::Recognizer::_Base::build_multipart(
        \@fields,
        [ [ 'file', 'audio.wav', 'audio/wav', $wav ] ],
    );

    my $url = 'https://api.groq.com/openai/v1/audio/transcriptions';
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
            'Groq Whisper request failed: ' . $res->status_line
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
