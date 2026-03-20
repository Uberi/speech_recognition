use strict;
use warnings;
use ExtUtils::MakeMaker;

WriteMakefile(
    NAME             => 'Speech::Recognition',
    AUTHOR           => 'Perl port of SpeechRecognition by Anthony Zhang (Uberi)',
    VERSION_FROM     => 'lib/Speech/Recognition.pm',
    ABSTRACT_FROM    => 'lib/Speech/Recognition.pm',
    LICENSE          => 'bsd',
    MIN_PERL_VERSION => '5.036',

    PREREQ_PM => {
        # Core modules (always available since the minimum Perl version)
        'Carp'         => 0,
        'POSIX'        => 0,
        'MIME::Base64' => 0,    # core since Perl 5.6
        'Digest::SHA'  => 0,    # core since Perl 5.10
        'File::Temp'   => 0,    # core since Perl 5.6
        'IPC::Open3'   => 0,    # core since Perl 5.0
        'JSON::PP'     => 0,    # core since Perl 5.14

        # LWP is the standard HTTP client; ships with libwww-perl
        'LWP::UserAgent' => '6.00',
        'HTTP::Request'  => '6.00',
    },

    TEST_REQUIRES => {
        'Test::More' => '1.00',
    },

    META_MERGE => {
        'meta-spec' => { version => 2 },
        resources   => {
            repository => {
                type => 'git',
                url  => 'https://github.com/trbutler/speech_recognition.git',
                web  => 'https://github.com/trbutler/speech_recognition',
            },
            bugtracker => {
                web => 'https://github.com/trbutler/speech_recognition/issues',
            },
        },
        x_provides_scripts => {},
    },
);
