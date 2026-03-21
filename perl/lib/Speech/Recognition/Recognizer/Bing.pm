package Speech::Recognition::Recognizer::Bing;

use v5.36;
use HTTP::Request ();
use Speech::Recognition::Recognizer::_Base qw();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer::Bing - Microsoft Bing Speech recognition backend (legacy)

=head1 SYNOPSIS

    my $text = $r->recognize_bing($audio,
        key      => $bing_api_key,
        language => 'en-US',
    );

=head1 DESCRIPTION

Uses the (legacy) Microsoft Bing Speech API.  This API is deprecated; new
projects should use L<Speech::Recognition::Recognizer::Azure> instead.

A Microsoft Cognitive Services subscription key is required.

=head1 ARGUMENTS

=over 4

=item * C<key> (required) - 32-character hex subscription key

=item * C<language> - BCP-47 language tag, default C<en-US>

=item * C<show_all> - return the raw JSON response instead of the transcript

=back

=cut

sub recognize ( $self, $audio_data, %args ) {
    Speech::Recognition::Recognizer::_Base::assert_audio($audio_data);

    my $key      = $args{key}      or Speech::Recognition::Recognizer::_Base::throw_setup('Bing API key is required (key => ...)');
    my $language = $args{language} // 'en-US';
    my $show_all = $args{show_all} // 0;

    my $access_token = _get_access_token( $self, $key );

    my $wav = $audio_data->get_wav_data( convert_rate => 16000, convert_width => 2 );

    require POSIX;
    my $req_id = _uuid4();

    my $query = Speech::Recognition::Recognizer::_Base::urlencode(
        language  => $language,
        locale    => $language,
        requestid => $req_id,
    );
    my $url = "https://speech.platform.bing.com/speech/recognition/interactive"
        . "/cognitiveservices/v1?$query";

    my $ua  = Speech::Recognition::Recognizer::_Base::make_ua(
        $self->{operation_timeout} // 30
    );
    my $req = HTTP::Request->new(
        POST => $url,
        [
            'Authorization' => "Bearer $access_token",
            'Content-type'  => 'audio/wav; codec="audio/pcm"; samplerate=16000',
        ],
        $wav,
    );

    my $res = $ua->request($req);
    unless ( $res->is_success ) {
        Speech::Recognition::Recognizer::_Base::throw_request(
            'Bing Speech request failed: ' . $res->status_line
        );
    }

    my $result = Speech::Recognition::Recognizer::_Base::decode_json( $res->content );
    return $result if $show_all;

    unless (
        exists $result->{RecognitionStatus}
        && $result->{RecognitionStatus} eq 'Success'
        && exists $result->{DisplayText}
    ) {
        Speech::Recognition::Recognizer::_Base::throw_unknown();
    }

    return $result->{DisplayText};
}

sub _get_access_token ( $self, $key ) {
    my $now   = time;
    my $cache = ( $self->{_bing_token_cache} //= {} );

    if ( exists $cache->{$key} && $cache->{$key}{expires} > $now ) {
        return $cache->{$key}{token};
    }

    my $url = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken';
    my $ua  = Speech::Recognition::Recognizer::_Base::make_ua(60);
    my $req = HTTP::Request->new(
        POST => $url,
        [
            'Content-type'              => 'application/x-www-form-urlencoded',
            'Content-Length'            => '0',
            'Ocp-Apim-Subscription-Key' => $key,
        ],
        '',
    );

    my $res = $ua->request($req);
    unless ( $res->is_success ) {
        Speech::Recognition::Recognizer::_Base::throw_request(
            'Bing token request failed: ' . $res->status_line
        );
    }

    my $token = $res->content;
    $cache->{$key} = { token => $token, expires => $now + 540 };
    return $token;
}

sub _uuid4 {
    return sprintf '%04x%04x-%04x-%04x-%04x-%04x%04x%04x',
        map { int( rand(0x10000) ) } 1 .. 8;
}

1;

__END__

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
