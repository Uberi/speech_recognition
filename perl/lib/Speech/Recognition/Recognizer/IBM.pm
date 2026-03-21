package Speech::Recognition::Recognizer::IBM;

use v5.36;
use HTTP::Request ();
use MIME::Base64  qw(encode_base64);
use Speech::Recognition::Recognizer::_Base qw();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer::IBM - IBM Speech to Text recognition backend

=head1 SYNOPSIS

    my $text = $r->recognize_ibm($audio,
        key      => $api_key,
        language => 'en-US',
    );

=head1 DESCRIPTION

Uses the IBM Watson Speech to Text API.  An IBM API key is required; create
one at L<https://cloud.ibm.com/>.

=head1 ARGUMENTS

=over 4

=item * C<key> (required) - IBM API key

=item * C<language> - language model code, default C<en-US_BroadbandModel>

=item * C<endpoint> - IBM Watson service URL (default is the C<us-south> URL
C<https://api.us-south.speech-to-text.watson.cloud.ibm.com>).  Override this
with the instance URL shown in your IBM Cloud service credentials.

=item * C<show_all> - return the raw JSON response instead of the transcript

=back

=cut

sub recognize ( $self, $audio_data, %args ) {
    Speech::Recognition::Recognizer::_Base::assert_audio($audio_data);

    my $key      = $args{key}      or Speech::Recognition::Recognizer::_Base::throw_setup('IBM API key is required (key => ...)');
    my $language = $args{language} // 'en-US';
    my $show_all = $args{show_all} // 0;
    my $endpoint = $args{endpoint} // 'https://api.us-south.speech-to-text.watson.cloud.ibm.com';

    my $flac = $audio_data->get_flac_data(
        $audio_data->sample_rate < 16000 ? ( convert_rate  => 16000 ) : (),
        $audio_data->sample_width < 2    ? ( convert_width => 2     ) : (),
    );

    # IBM uses a <language>_BroadbandModel naming convention
    my $model = $language =~ /_/ ? $language : "${language}_BroadbandModel";

    my $url = "$endpoint/v1/recognize?model=$model";

    my $auth = encode_base64( "apikey:$key", '' );    # no newline

    my $ua  = Speech::Recognition::Recognizer::_Base::make_ua(
        $self->{operation_timeout} // 30
    );
    my $req = HTTP::Request->new(
        POST => $url,
        [
            'Content-Type'  => 'audio/x-flac',
            'Authorization' => "Basic $auth",
        ],
        $flac,
    );

    my $res = $ua->request($req);
    unless ( $res->is_success ) {
        Speech::Recognition::Recognizer::_Base::throw_request(
            'IBM Speech request failed: ' . $res->status_line
        );
    }

    my $result = Speech::Recognition::Recognizer::_Base::decode_json( $res->content );
    return $result if $show_all;

    unless (
        exists $result->{results}
        && ref $result->{results} eq 'ARRAY'
        && @{ $result->{results} }
        && exists $result->{results}[0]{alternatives}
    ) {
        Speech::Recognition::Recognizer::_Base::throw_unknown();
    }

    my @transcripts;
    for my $utterance ( @{ $result->{results} } ) {
        unless ( exists $utterance->{alternatives} ) {
            Speech::Recognition::Recognizer::_Base::throw_unknown();
        }
        for my $hyp ( @{ $utterance->{alternatives} } ) {
            push @transcripts, $hyp->{transcript}
                if exists $hyp->{transcript};
        }
    }

    return join ' ', @transcripts;
}

1;

__END__

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
