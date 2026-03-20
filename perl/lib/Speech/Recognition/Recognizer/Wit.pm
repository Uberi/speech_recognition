package Speech::Recognition::Recognizer::Wit;

use v5.36;
use HTTP::Request ();
use Speech::Recognition::Recognizer::_Base qw();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer::Wit - Wit.ai speech recognition backend

=head1 SYNOPSIS

    my $text = $r->recognize_wit($audio, key => $wit_api_key);

=head1 DESCRIPTION

Uses the L<Wit.ai|https://wit.ai/> speech API.  A Wit.ai API key is required;
sign up at L<https://wit.ai/> and create an application to obtain one.

=head1 ARGUMENTS

=over 4

=item * C<key> (required) - 32-character uppercase alphanumeric Wit.ai API key

=item * C<show_all> - if true, returns the raw JSON response hash ref instead
of just the transcript string

=back

=cut

sub recognize ( $self, $audio_data, %args ) {
    Speech::Recognition::Recognizer::_Base::assert_audio($audio_data);

    my $key      = $args{key}      or die "Wit.ai API key is required (key => ...)";
    my $show_all = $args{show_all} // 0;

    my $wav = $audio_data->get_wav_data(
        $audio_data->sample_rate < 8000 ? ( convert_rate => 8000 ) : (),
        convert_width => 2,
    );

    my $url = 'https://api.wit.ai/speech?v=20170307';
    my $ua  = Speech::Recognition::Recognizer::_Base::make_ua(
        $self->{operation_timeout} // 30
    );
    my $req = HTTP::Request->new(
        POST => $url,
        [
            'Authorization' => "Bearer $key",
            'Content-Type'  => 'audio/wav',
        ],
        $wav,
    );

    my $res = $ua->request($req);
    unless ( $res->is_success ) {
        Speech::Recognition::Recognizer::_Base::throw_request(
            'Wit.ai request failed: ' . $res->status_line
        );
    }

    my $result = Speech::Recognition::Recognizer::_Base::decode_json( $res->content );
    return $result if $show_all;

    unless ( exists $result->{_text} && defined $result->{_text} ) {
        Speech::Recognition::Recognizer::_Base::throw_unknown();
    }
    return $result->{_text};
}

1;

__END__

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
