package Speech::Recognition::Recognizer::Azure;

use v5.36;
use HTTP::Request ();
use Speech::Recognition::Recognizer::_Base qw();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer::Azure - Microsoft Azure Speech recognition backend

=head1 SYNOPSIS

    my ($text, $confidence) = $r->recognize_azure($audio,
        key      => $subscription_key,
        language => 'en-US',
        location => 'eastus',
    );

=head1 DESCRIPTION

Uses the Microsoft Azure Cognitive Services Speech-to-Text REST API.

An Azure Cognitive Services subscription key is required.  Create one at
L<https://portal.azure.com/>.

=head1 ARGUMENTS

=over 4

=item * C<key> (required) - Azure subscription key

=item * C<language> - BCP-47 language tag, default C<en-US>

=item * C<location> - Azure region, default C<westus>

=item * C<profanity> - profanity handling (C<masked>, C<removed>, or C<raw>), default C<masked>

=item * C<show_all> - return the full JSON response instead of C<($text, $confidence)>

=back

=cut

sub recognize ( $self, $audio_data, %args ) {
    Speech::Recognition::Recognizer::_Base::assert_audio($audio_data);

    my $key       = $args{key}       or die 'Azure subscription key is required (key => ...)';
    my $language  = $args{language}  // 'en-US';
    my $location  = $args{location}  // 'westus';
    my $profanity = $args{profanity} // 'masked';
    my $show_all  = $args{show_all}  // 0;

    # Obtain an access token (cached for 10 minutes)
    my $access_token = _get_access_token( $self, $key, $location );

    my $wav = $audio_data->get_wav_data( convert_rate => 16000, convert_width => 2 );

    my $query = _urlencode(
        language => $language,
        format   => 'detailed',
        profanity => $profanity,
    );
    my $url = "https://$location.stt.speech.microsoft.com"
        . "/speech/recognition/conversation/cognitiveservices/v1?$query";

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
            'Azure Speech request failed: ' . $res->status_line
        );
    }

    my $result = Speech::Recognition::Recognizer::_Base::decode_json( $res->content );
    return $result if $show_all;

    unless (
        exists $result->{RecognitionStatus}
        && $result->{RecognitionStatus} eq 'Success'
        && exists $result->{NBest}
    ) {
        Speech::Recognition::Recognizer::_Base::throw_unknown();
    }

    my $best = $result->{NBest}[0];
    return ( $best->{Display}, $best->{Confidence} );
}

# ---------------------------------------------------------------------------
# OAuth token (cached per recognizer instance, per API key)
# ---------------------------------------------------------------------------

sub _get_access_token ( $self, $key, $location ) {
    my $now = time;

    # Simple per-instance token cache keyed by subscription key
    my $cache = ( $self->{_azure_token_cache} //= {} );
    if (   exists $cache->{$key}
        && $cache->{$key}{expires} > $now )
    {
        return $cache->{$key}{token};
    }

    my $url = "https://$location.api.cognitive.microsoft.com/sts/v1.0/issueToken";
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
            'Azure token request failed: ' . $res->status_line
        );
    }

    my $token = $res->content;
    $cache->{$key} = { token => $token, expires => $now + 540 };  # 10 min - 1 min buffer
    return $token;
}

sub _urlencode (%params) {
    join '&', map {
        _enc($_) . '=' . _enc( $params{$_} )
    } sort keys %params;
}

sub _enc ($s) {
    $s =~ s/([^A-Za-z0-9\-_.~])/sprintf('%%%02X', ord($1))/ge;
    return $s;
}

1;

__END__

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
