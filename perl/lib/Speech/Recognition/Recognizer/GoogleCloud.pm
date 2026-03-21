package Speech::Recognition::Recognizer::GoogleCloud;

use v5.36;
use HTTP::Request         ();
use MIME::Base64          qw(encode_base64);
use URI::Escape           qw(uri_escape);
use Speech::Recognition::Recognizer::_Base qw();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer::GoogleCloud - Google Cloud Speech-to-Text backend

=head1 SYNOPSIS

    my $text = $r->recognize_google_cloud($audio,
        credentials_json => '/path/to/service-account.json',
        language         => 'en-US',
    );

    # Or pass the JSON content directly
    my $text = $r->recognize_google_cloud($audio,
        credentials_json => $json_string,
        language         => 'en-US',
    );

=head1 DESCRIPTION

Uses the Google Cloud Speech-to-Text V1 REST API.  Requires a Google Cloud
Platform service-account JSON key with the Cloud Speech API enabled.

Authentication is performed via a JWT-based OAuth2 access token request, using
the private key embedded in the service-account JSON.  Requires the
L<Crypt::OpenSSL::RSA> module.

=head1 ARGUMENTS

=over 4

=item * C<credentials_json> (required) - Path to a service-account JSON file,
B<or> the raw JSON string content of such a file.

=item * C<language> - BCP-47 language code, default C<en-US>.

=item * C<preferred_phrases> - Arrayref of phrases to boost recognition of.

=item * C<show_all> - Return the full JSON response hash instead of the
transcript string.

=item * C<model> - Recognition model (e.g. C<latest_long>, C<video>,
C<phone_call>).  Defaults to the API default.

=item * C<use_enhanced> - Boolean; request an enhanced model.

=back

=cut

use constant {
    _TOKEN_URL  => 'https://oauth2.googleapis.com/token',
    _SPEECH_URL => 'https://speech.googleapis.com/v1/speech:recognize',
    _SCOPE      => 'https://www.googleapis.com/auth/cloud-platform',
};

# ---------------------------------------------------------------------------
# JWT / OAuth2 helpers
# ---------------------------------------------------------------------------

sub _base64url ($data) {
    my $b64 = encode_base64($data, '');
    $b64 =~ tr|+/=|-_|d;
    return $b64;
}

sub _make_jwt ( $email, $private_key_pem ) {
    my $header  = Speech::Recognition::Recognizer::_Base::encode_json(
        { alg => 'RS256', typ => 'JWT' }
    );
    my $now     = time();
    my $payload = Speech::Recognition::Recognizer::_Base::encode_json( {
        iss   => $email,
        scope => _SCOPE,
        aud   => _TOKEN_URL,
        iat   => $now,
        exp   => $now + 3600,
    } );

    my $signing_input = _base64url($header) . '.' . _base64url($payload);

    # Sign with RSA-SHA256 — requires Crypt::OpenSSL::RSA
    eval { require Crypt::OpenSSL::RSA; 1 }
        or Speech::Recognition::Recognizer::_Base::throw_setup(
            'Crypt::OpenSSL::RSA is required for Google Cloud authentication; '
          . 'install it with: cpanm Crypt::OpenSSL::RSA'
        );

    my $rsa = Crypt::OpenSSL::RSA->new_private_key($private_key_pem);
    $rsa->use_sha256_hash;
    my $sig = $rsa->sign($signing_input);

    return $signing_input . '.' . _base64url($sig);
}

sub _fetch_access_token ( $ua, $email, $private_key_pem ) {
    my $jwt = _make_jwt($email, $private_key_pem);

    my $body =
        'grant_type=' . uri_escape('urn:ietf:params:oauth:grant-type:jwt-bearer')
      . '&assertion=' . uri_escape($jwt);

    my $req = HTTP::Request->new(
        POST => _TOKEN_URL,
        [ 'Content-Type' => 'application/x-www-form-urlencoded' ],
        $body,
    );
    my $res = $ua->request($req);
    unless ( $res->is_success ) {
        Speech::Recognition::Recognizer::_Base::throw_request(
            'Google Cloud OAuth2 token request failed: ' . $res->status_line
        );
    }

    my $data  = Speech::Recognition::Recognizer::_Base::decode_json( $res->content );
    my $token = $data->{access_token}
        or Speech::Recognition::Recognizer::_Base::throw_request(
            'Google Cloud OAuth2 response missing access_token'
        );
    return $token;
}

sub _load_credentials ($creds_arg) {
    my $json;
    if ( $creds_arg =~ /\A\s*\{/ ) {
        # Looks like raw JSON content
        $json = $creds_arg;
    }
    else {
        # Treat as a file path
        open my $fh, '<', $creds_arg
            or Speech::Recognition::Recognizer::_Base::throw_setup(
                "Cannot open credentials file '$creds_arg': $!"
            );
        local $/;
        $json = <$fh>;
        close $fh;
    }
    return Speech::Recognition::Recognizer::_Base::decode_json($json);
}

# ---------------------------------------------------------------------------
# Main recognize sub
# ---------------------------------------------------------------------------

sub recognize ( $self, $audio_data, %args ) {
    Speech::Recognition::Recognizer::_Base::assert_audio($audio_data);

    my $creds_arg = $args{credentials_json}
        or Speech::Recognition::Recognizer::_Base::throw_setup(
            'credentials_json is required (path to service-account JSON file or JSON string)'
        );
    my $language          = $args{language}          // 'en-US';
    my $preferred_phrases = $args{preferred_phrases};
    my $show_all          = $args{show_all}           // 0;
    my $model             = $args{model};
    my $use_enhanced      = $args{use_enhanced}       // 0;

    # Load service-account credentials
    my $creds       = _load_credentials($creds_arg);
    my $email       = $creds->{client_email}
        or Speech::Recognition::Recognizer::_Base::throw_setup(
            'credentials JSON missing client_email'
        );
    my $private_key = $creds->{private_key}
        or Speech::Recognition::Recognizer::_Base::throw_setup(
            'credentials JSON missing private_key'
        );

    # Clamp sample rate to 8 kHz – 48 kHz (Cloud Speech requirement)
    my $send_rate = $audio_data->sample_rate;
    $send_rate = 8000  if $send_rate < 8000;
    $send_rate = 48000 if $send_rate > 48000;

    my $flac = $audio_data->get_flac_data(
        convert_rate  => $send_rate,
        convert_width => 2,
    );

    my $ua = Speech::Recognition::Recognizer::_Base::make_ua(
        $self->{operation_timeout} // 60
    );

    # Get OAuth2 access token
    my $access_token = _fetch_access_token($ua, $email, $private_key);

    # Build recognition config
    my %config = (
        encoding         => 'FLAC',
        sampleRateHertz  => $send_rate,
        languageCode     => $language,
    );
    $config{model}       = $model  if defined $model;
    $config{useEnhanced} = \1      if $use_enhanced;
    if ( ref $preferred_phrases eq 'ARRAY' && @$preferred_phrases ) {
        $config{speechContexts} = [ { phrases => $preferred_phrases } ];
    }

    my $body = Speech::Recognition::Recognizer::_Base::encode_json( {
        config => \%config,
        audio  => { content => encode_base64($flac, '') },
    } );

    my $req = HTTP::Request->new(
        POST => _SPEECH_URL,
        [
            'Authorization' => "Bearer $access_token",
            'Content-Type'  => 'application/json',
        ],
        $body,
    );

    my $res = $ua->request($req);
    unless ( $res->is_success ) {
        Speech::Recognition::Recognizer::_Base::throw_request(
            'Google Cloud Speech request failed: ' . $res->status_line
        );
    }

    my $result = Speech::Recognition::Recognizer::_Base::decode_json( $res->content );
    return $result if $show_all;

    my @results = @{ $result->{results} // [] };
    Speech::Recognition::Recognizer::_Base::throw_unknown() unless @results;

    my $transcript = join ' ', map {
        my $alts = $_->{alternatives} // [];
        @$alts ? $alts->[0]{transcript} // '' : ''
    } @results;
    $transcript =~ s/^\s+|\s+$//g;
    return $transcript;
}

1;

__END__

=head1 DEPENDENCIES

Requires L<Crypt::OpenSSL::RSA> for JWT signing.  Install with:

    cpanm Crypt::OpenSSL::RSA

or on Debian/Ubuntu:

    apt-get install libcrypt-openssl-rsa-perl

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
