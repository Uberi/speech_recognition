package Speech::Recognition::Exception;

use v5.36;

our $VERSION = '0.01';

=head1 NAME

Speech::Recognition::Exception - Exception classes for Speech::Recognition

=head1 SYNOPSIS

    use Speech::Recognition::Exception;

    eval {
        Speech::Recognition::Exception::RequestError->throw("connection failed");
    };
    if (my $e = $@) {
        if (ref $e && $e->isa('Speech::Recognition::Exception::RequestError')) {
            warn "Request error: " . $e->message;
        }
    }

=head1 DESCRIPTION

Provides exception classes analogous to the Python speech_recognition exception
hierarchy. All exceptions inherit from L<Speech::Recognition::Exception>.

=head1 EXCEPTION CLASSES

=over 4

=item * C<Speech::Recognition::Exception::SetupError>

Raised when there is a setup problem (e.g., missing required library).

=item * C<Speech::Recognition::Exception::WaitTimeoutError>

Raised when listening times out waiting for speech to start.

=item * C<Speech::Recognition::Exception::RequestError>

Raised when an API request fails or there is no internet connection.

=item * C<Speech::Recognition::Exception::UnknownValueError>

Raised when the speech is unintelligible.

=item * C<Speech::Recognition::Exception::TranscriptionNotReady>

Raised by async transcription services when the job is still in progress.

=item * C<Speech::Recognition::Exception::TranscriptionFailed>

Raised by async transcription services when the job has failed.

=back

=cut

sub new ( $class, $message = 'Unknown error' ) {
    return bless { message => $message }, $class;
}

=head2 message

Returns the exception message string.

=cut

sub message ($self) { return $self->{message} }

=head2 throw($message)

Creates and immediately throws (C<die>s with) the exception.

=cut

sub throw ( $class, $message = 'Unknown error' ) {
    die $class->new($message);
}

use overload '""' => sub ($self, @) { ref($self) . ': ' . $self->{message} };

# ---------------------------------------------------------------------------
# Subclasses
# ---------------------------------------------------------------------------

package Speech::Recognition::Exception::SetupError;
use parent -norequire, 'Speech::Recognition::Exception';
our $VERSION = '0.01';

package Speech::Recognition::Exception::WaitTimeoutError;
use parent -norequire, 'Speech::Recognition::Exception';
our $VERSION = '0.01';

package Speech::Recognition::Exception::RequestError;
use parent -norequire, 'Speech::Recognition::Exception';
our $VERSION = '0.01';

package Speech::Recognition::Exception::UnknownValueError;
use parent -norequire, 'Speech::Recognition::Exception';
our $VERSION = '0.01';

sub new ( $class, $message = 'Could not understand audio' ) {
    return $class->SUPER::new($message);
}

package Speech::Recognition::Exception::TranscriptionNotReady;
use parent -norequire, 'Speech::Recognition::Exception';
our $VERSION = '0.01';

=head2 new($message, job_name => $name, file_key => $key)

For async transcription services, C<job_name> and C<file_key> carry the
identifiers needed to poll for the result later.

=cut

sub new ( $class, $message = 'Transcription not ready', %args ) {
    my $self = $class->SUPER::new($message);
    $self->{job_name} = $args{job_name};
    $self->{file_key} = $args{file_key};
    return $self;
}

sub job_name ($self) { return $self->{job_name} }
sub file_key ($self) { return $self->{file_key} }

package Speech::Recognition::Exception::TranscriptionFailed;
use parent -norequire, 'Speech::Recognition::Exception';
our $VERSION = '0.01';

sub new ( $class, $message = 'Transcription failed', %args ) {
    my $self = $class->SUPER::new($message);
    $self->{job_name} = $args{job_name};
    $self->{file_key} = $args{file_key};
    return $self;
}

sub job_name ($self) { return $self->{job_name} }
sub file_key ($self) { return $self->{file_key} }

1;

__END__

=head1 AUTHOR

Perl port of the Python speech_recognition library by Anthony Zhang (Uberi).

=head1 LICENSE

BSD 3-Clause License

=cut
