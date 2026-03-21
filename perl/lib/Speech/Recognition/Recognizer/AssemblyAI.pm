package Speech::Recognition::Recognizer::AssemblyAI;

use v5.36;
use HTTP::Request         ();
use Speech::Recognition::Recognizer::_Base qw();

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Recognizer::AssemblyAI - AssemblyAI speech recognition backend

=head1 SYNOPSIS

    # Step 1: Submit audio and get a job ID back via TranscriptionNotReady
    eval { $r->recognize_assemblyai($audio, api_token => $token) };
    if (ref $@ && $@->isa('Speech::Recognition::Exception::TranscriptionNotReady')) {
        my $job_id = $@->job_name;

        # Step 2: Poll until done (pass undef audio + job_name)
        my $text = eval {
            $r->recognize_assemblyai(undef,
                api_token => $token,
                job_name  => $job_id,
            );
        };
    }

=head1 DESCRIPTION

Uses the AssemblyAI Speech-to-Text API.  Because transcription is
asynchronous, the first call (with an C<AudioData> object) uploads the audio
and immediately throws a
C<Speech::Recognition::Exception::TranscriptionNotReady> exception whose
C<job_name> attribute holds the transcription ID.

Subsequent calls with C<audio_data =E<gt> undef> and C<job_name =E<gt> $id>
poll the job status:

=over 4

=item * Still processing — throws C<TranscriptionNotReady> again.

=item * Error — throws C<TranscriptionFailed>.

=item * Complete — returns the transcript string (or the full JSON hash when
C<show_all> is true).

=back

This matches the behaviour of the Python C<recognize_assemblyai> method.

=head1 ARGUMENTS

=over 4

=item * C<api_token> (required) — AssemblyAI API token.

=item * C<job_name> — Transcription ID from a previous call.  When provided,
C<audio_data> should be C<undef>.

=item * C<show_all> — Return the full JSON response hash instead of just the
transcript string.

=back

=cut

use constant {
    _UPLOAD_URL     => 'https://api.assemblyai.com/v2/upload',
    _TRANSCRIPT_URL => 'https://api.assemblyai.com/v2/transcript',
};

sub recognize ( $self, $audio_data, %args ) {
    require Speech::Recognition::Exception;

    my $api_token = $args{api_token}
        or Speech::Recognition::Recognizer::_Base::throw_setup(
            'AssemblyAI API token is required (api_token => ...)');
    my $job_name  = $args{job_name};
    my $show_all  = $args{show_all} // 0;

    my $ua = Speech::Recognition::Recognizer::_Base::make_ua(
        $self->{operation_timeout} // 60
    );

    # -----------------------------------------------------------------------
    # Poll an existing job when audio_data is undef and job_name is provided.
    # -----------------------------------------------------------------------
    if ( !defined $audio_data && defined $job_name ) {
        my $url = _TRANSCRIPT_URL . "/$job_name";
        my $req = HTTP::Request->new(
            GET => $url,
            [ 'authorization' => $api_token ],
        );

        my $res = $ua->request($req);
        unless ( $res->is_success ) {
            Speech::Recognition::Recognizer::_Base::throw_request(
                'AssemblyAI status request failed: ' . $res->status_line
            );
        }

        my $data   = Speech::Recognition::Recognizer::_Base::decode_json( $res->content );
        my $status = $data->{status} // '';

        if ( $status eq 'error' ) {
            die Speech::Recognition::Exception::TranscriptionFailed->new(
                $data->{error} // 'AssemblyAI transcription failed',
            );
        }

        if ( $status eq 'completed' ) {
            return $data if $show_all;
            return $data->{text};
        }

        # queued or processing — keep waiting
        die Speech::Recognition::Exception::TranscriptionNotReady->new(
            'AssemblyAI transcription not yet ready',
            job_name => $job_name,
        );
    }

    # -----------------------------------------------------------------------
    # New job: validate audio, upload, and submit for transcription.
    # -----------------------------------------------------------------------
    Speech::Recognition::Recognizer::_Base::assert_audio($audio_data);

    my $wav = $audio_data->get_wav_data;

    # Upload the audio
    my $upload_req = HTTP::Request->new(
        POST => _UPLOAD_URL,
        [
            'authorization' => $api_token,
            'Content-Type'  => 'audio/wav',
        ],
        $wav,
    );

    my $upload_res = $ua->request($upload_req);
    unless ( $upload_res->is_success ) {
        Speech::Recognition::Recognizer::_Base::throw_request(
            'AssemblyAI upload failed: ' . $upload_res->status_line
        );
    }

    my $upload_data = Speech::Recognition::Recognizer::_Base::decode_json(
        $upload_res->content
    );
    my $upload_url = $upload_data->{upload_url}
        or Speech::Recognition::Recognizer::_Base::throw_request(
            'AssemblyAI upload response missing upload_url'
        );

    # Submit transcription request
    my $body = Speech::Recognition::Recognizer::_Base::encode_json(
        { audio_url => $upload_url }
    );
    my $transcript_req = HTTP::Request->new(
        POST => _TRANSCRIPT_URL,
        [
            'authorization' => $api_token,
            'Content-Type'  => 'application/json',
        ],
        $body,
    );

    my $transcript_res = $ua->request($transcript_req);
    unless ( $transcript_res->is_success ) {
        Speech::Recognition::Recognizer::_Base::throw_request(
            'AssemblyAI transcript request failed: ' . $transcript_res->status_line
        );
    }

    my $transcript_data = Speech::Recognition::Recognizer::_Base::decode_json(
        $transcript_res->content
    );
    my $transcription_id = $transcript_data->{id}
        or Speech::Recognition::Recognizer::_Base::throw_request(
            'AssemblyAI response missing transcription id'
        );

    # Raise TranscriptionNotReady with the job ID so the caller can poll later
    die Speech::Recognition::Exception::TranscriptionNotReady->new(
        'AssemblyAI transcription submitted; poll with job_name => ' . $transcription_id,
        job_name => $transcription_id,
    );
}

1;

__END__

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
