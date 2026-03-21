package Speech::Recognition::Recognizer::Houndify;

use v5.36;
use HTTP::Request ();
use MIME::Base64  qw(encode_base64 decode_base64 encode_base64url decode_base64url);
use Digest::SHA   qw(hmac_sha256);
use Speech::Recognition::Recognizer::_Base qw();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer::Houndify - Houndify speech recognition backend

=head1 SYNOPSIS

    my ($text, $confidence) = $r->recognize_houndify($audio,
        client_id  => $client_id,
        client_key => $client_key,
    );

=head1 DESCRIPTION

Uses the L<Houndify|https://www.houndify.com/> speech API.  Client ID and
client key are required; both are Base64-encoded strings obtained from the
Houndify dashboard.

Only English is supported.

=head1 ARGUMENTS

=over 4

=item * C<client_id> (required) - Houndify client ID (Base64)

=item * C<client_key> (required) - Houndify client key (Base64)

=item * C<show_all> - return the raw JSON response instead of C<($text, $confidence)>

=back

=cut

sub recognize ( $self, $audio_data, %args ) {
    Speech::Recognition::Recognizer::_Base::assert_audio($audio_data);

    my $client_id  = $args{client_id}  or die 'Houndify client_id is required';
    my $client_key = $args{client_key} or die 'Houndify client_key is required';
    my $show_all   = $args{show_all}  // 0;

    my $sr  = $audio_data->sample_rate;
    my $wav = $audio_data->get_wav_data(
        ( $sr == 8000 || $sr == 16000 ) ? () : ( convert_rate => 16000 ),
        convert_width => 2,
    );

    # Build HMAC-SHA256 authentication signature
    my $user_id    = _uuid4();
    my $request_id = _uuid4();
    my $req_time   = time;

    my $message = $user_id . ';' . $request_id . $req_time;

    # client_key is URL-safe base64; decode it properly before use as HMAC key
    my $key_bytes = do {
        my $k = $client_key;
        $k =~ tr|-_|+/|;
        decode_base64($k);
    };
    my $sig = encode_base64( hmac_sha256( $message, $key_bytes ), '' );
    # urlsafe base64
    $sig =~ tr|+/|-_|;

    my $url = 'https://api.houndify.com/v1/audio';
    my $ua  = Speech::Recognition::Recognizer::_Base::make_ua(
        $self->{operation_timeout} // 30
    );

    my $req_info = Speech::Recognition::Recognizer::_Base::encode_json(
        { ClientID => $client_id, UserID => $user_id }
    );

    my $req = HTTP::Request->new(
        POST => $url,
        [
            'Content-Type'              => 'application/json',
            'Hound-Request-Info'        => $req_info,
            'Hound-Request-Authentication' => "$user_id;$request_id",
            'Hound-Client-Authentication'  => "$client_id;$req_time;$sig",
        ],
        $wav,
    );

    my $res = $ua->request($req);
    unless ( $res->is_success ) {
        Speech::Recognition::Recognizer::_Base::throw_request(
            'Houndify request failed: ' . $res->status_line
        );
    }

    my $result = Speech::Recognition::Recognizer::_Base::decode_json( $res->content );
    return $result if $show_all;

    unless (
        exists $result->{Disambiguation}
        && defined $result->{Disambiguation}
    ) {
        Speech::Recognition::Recognizer::_Base::throw_unknown();
    }

    my $choices = $result->{Disambiguation}{ChoiceData};
    return (
        $choices->[0]{Transcription},
        $choices->[0]{ConfidenceScore},
    );
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
