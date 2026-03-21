use strict;
use warnings;
use v5.36;
use Test::More;
use lib 'lib';

use HTTP::Response ();
use HTTP::Headers  ();
use Test::LWP::UserAgent;

use Speech::Recognition::AudioData;
use Speech::Recognition::Exception;
use Speech::Recognition::Recognizer;

# Pre-load all backend modules so that the local-typeglob mock for make_ua
# works correctly.  (Perl's local() is reliable on pre-compiled code; if a
# backend module were first compiled while a local() is active the wrong
# CODE ref could be captured.)
require Speech::Recognition::Recognizer::Google;
require Speech::Recognition::Recognizer::Wit;
require Speech::Recognition::Recognizer::IBM;
require Speech::Recognition::Recognizer::OpenAI;
require Speech::Recognition::Recognizer::Groq;
require Speech::Recognition::Recognizer::AssemblyAI;

# ---------------------------------------------------------------------------
# Helper: generate a short PCM sine wave for testing
# ---------------------------------------------------------------------------

my $PI = 4 * atan2( 1, 1 );

sub make_audio ($n = 1600) {    # 0.1 s at 16 kHz
    my @s;
    for my $i ( 0 .. $n - 1 ) {
        my $v = sin( 2 * $PI * 440 * $i / 16000 );
        push @s, int( $v * 32767 ) & 0xFFFF;
    }
    return Speech::Recognition::AudioData->new(
        frame_data   => pack( 'v*', @s ),
        sample_rate  => 16000,
        sample_width => 2,
    );
}

# ---------------------------------------------------------------------------
# Helper: create a mock UA that returns a canned response for any request
# ---------------------------------------------------------------------------

sub make_mock_ua ($status, $body) {
    my $ua = Test::LWP::UserAgent->new( network_fallback => 0 );
    $ua->map_response(
        sub { 1 },    # match every request
        HTTP::Response->new(
            $status, 'OK',
            HTTP::Headers->new( 'Content-Type' => 'application/json' ),
            $body,
        ),
    );
    return $ua;
}

# Temporarily replace Speech::Recognition::Recognizer::_Base::make_ua
# with a stub returning a fixed mock UA, run $code, then restore.
sub with_mock_ua ($code, $mock_ua) {
    no warnings 'redefine';
    local *Speech::Recognition::Recognizer::_Base::make_ua = sub { $mock_ua };
    $code->();
}

my $r = Speech::Recognition::Recognizer->new;

# ===========================================================================
# 1. Google (free) backend
# ===========================================================================

subtest 'Google backend - successful transcription' => sub {
    my $body = qq|{"result":[]}\n|
             . qq|{"result":[{"alternative":[{"transcript":"hello world","confidence":0.95}],"final":true}]}\n|;
    my $ua   = make_mock_ua( 200, $body );

    my $audio = make_audio();
    my $text;
    with_mock_ua( sub { $text = $r->recognize_google($audio) }, $ua );
    is $text, 'hello world', 'Google returns first transcript';
};

subtest 'Google backend - show_all' => sub {
    my $body = qq|{"result":[]}\n|
             . qq|{"result":[{"alternative":[{"transcript":"hi"}],"final":true}]}\n|;
    my $ua   = make_mock_ua( 200, $body );

    my $audio = make_audio();
    my $all;
    with_mock_ua( sub { $all = $r->recognize_google( $audio, show_all => 1 ) }, $ua );
    is ref $all, 'ARRAY', 'show_all returns arrayref';
    is $all->[0]{alternative}[0]{transcript}, 'hi', 'show_all transcript accessible';
};

subtest 'Google backend - request error' => sub {
    my $ua = make_mock_ua( 403, '{}' );
    my $audio = make_audio();
    eval { with_mock_ua( sub { $r->recognize_google($audio) }, $ua ) };
    my $e = $@;
    ok ref $e && $e->isa('Speech::Recognition::Exception::RequestError'),
        'HTTP error becomes RequestError';
};

subtest 'Google backend - unknown value (empty result)' => sub {
    my $ua = make_mock_ua( 200, qq|{"result":[]}\n| );
    my $audio = make_audio();
    eval { with_mock_ua( sub { $r->recognize_google($audio) }, $ua ) };
    my $e = $@;
    ok ref $e && $e->isa('Speech::Recognition::Exception::UnknownValueError'),
        'empty result becomes UnknownValueError';
};

# ===========================================================================
# 2. Wit.ai backend
# ===========================================================================

subtest 'Wit backend - successful transcription' => sub {
    my $body = '{"_text":"hello wit","entities":{}}';
    my $ua   = make_mock_ua( 200, $body );

    my $audio = make_audio();
    my $text;
    with_mock_ua(
        sub { $text = $r->recognize_wit( $audio, key => 'FAKE_WIT_KEY_32CHARS_PADDING_XX' ) },
        $ua
    );
    is $text, 'hello wit', 'Wit returns _text field';
};

subtest 'Wit backend - request error' => sub {
    my $ua = make_mock_ua( 401, '{}' );
    my $audio = make_audio();
    eval {
        with_mock_ua(
            sub { $r->recognize_wit( $audio, key => 'FAKE_WIT_KEY_32CHARS_PADDING_XX' ) },
            $ua
        );
    };
    my $e = $@;
    ok ref $e && $e->isa('Speech::Recognition::Exception::RequestError'),
        '401 becomes RequestError';
};

# ===========================================================================
# 3. IBM Watson backend
# ===========================================================================

subtest 'IBM backend - successful transcription' => sub {
    my $body = '{"results":[{"alternatives":[{"transcript":"ibm result","confidence":0.9}],"final":true}],"result_index":0}';
    my $ua   = make_mock_ua( 200, $body );

    my $audio = make_audio();
    my $text;
    with_mock_ua( sub { $text = $r->recognize_ibm( $audio, key => 'fake-ibm-key' ) }, $ua );
    is $text, 'ibm result', 'IBM returns first transcript';
};

subtest 'IBM backend - custom endpoint URL' => sub {
    my $body = '{"results":[{"alternatives":[{"transcript":"eu result"}],"final":true}],"result_index":0}';
    my $captured_url;

    no warnings 'redefine';
    local *Speech::Recognition::Recognizer::_Base::make_ua = sub {
        my $mock = Test::LWP::UserAgent->new( network_fallback => 0 );
        $mock->map_response(
            sub { $captured_url = $_[0]->uri->as_string; 1 },
            HTTP::Response->new( 200, 'OK',
                HTTP::Headers->new( 'Content-Type' => 'application/json' ),
                $body ),
        );
        return $mock;
    };

    my $audio = make_audio();
    $r->recognize_ibm(
        $audio,
        key      => 'fake-ibm-key',
        endpoint => 'https://api.eu-de.speech-to-text.watson.cloud.ibm.com',
    );
    like $captured_url, qr|eu-de|, 'custom endpoint used in request URL';
};

subtest 'IBM backend - show_all' => sub {
    my $body = '{"results":[{"alternatives":[{"transcript":"raw"}],"final":true}],"result_index":0}';
    my $ua   = make_mock_ua( 200, $body );

    my $audio = make_audio();
    my $all;
    with_mock_ua(
        sub { $all = $r->recognize_ibm( $audio, key => 'fake-ibm-key', show_all => 1 ) },
        $ua
    );
    is ref $all, 'HASH', 'show_all returns hash';
    is $all->{results}[0]{alternatives}[0]{transcript}, 'raw', 'raw JSON accessible';
};

# ===========================================================================
# 4. OpenAI Whisper backend
# ===========================================================================

subtest 'OpenAI backend - successful transcription' => sub {
    my $body = '{"text":"openai result"}';
    my $ua   = make_mock_ua( 200, $body );

    my $audio = make_audio();
    my $text;
    with_mock_ua(
        sub { $text = $r->recognize_openai( $audio, api_key => 'sk-fake' ) },
        $ua
    );
    is $text, 'openai result', 'OpenAI returns text field';
};

subtest 'OpenAI backend - invalid model name' => sub {
    my $audio = make_audio();
    eval { $r->recognize_openai( $audio, api_key => 'sk-fake', model => 'no-such-model' ) };
    my $e = $@;
    ok ref $e && $e->isa('Speech::Recognition::Exception::SetupError'),
        'bad model name becomes SetupError';
};

# ===========================================================================
# 5. AssemblyAI backend
# ===========================================================================

subtest 'AssemblyAI backend - submit job returns TranscriptionNotReady' => sub {
    # Two sequential responses: upload then transcript submit
    my @responses = (
        HTTP::Response->new( 200, 'OK',
            HTTP::Headers->new( 'Content-Type' => 'application/json' ),
            '{"upload_url":"https://cdn.assemblyai.com/upload/abc123"}' ),
        HTTP::Response->new( 200, 'OK',
            HTTP::Headers->new( 'Content-Type' => 'application/json' ),
            '{"id":"job-xyz","status":"queued"}' ),
    );
    my $call_num = 0;
    my $ua = Test::LWP::UserAgent->new( network_fallback => 0 );
    $ua->map_response(
        sub { 1 },
        sub { $responses[ $call_num++ ] },
    );

    my $audio = make_audio();
    my $exc;
    with_mock_ua(
        sub {
            eval { $r->recognize_assemblyai( $audio, api_token => 'fake-token' ) };
            $exc = $@;
        },
        $ua
    );

    ok ref $exc && $exc->isa('Speech::Recognition::Exception::TranscriptionNotReady'),
        'first call throws TranscriptionNotReady';
    is $exc->job_name, 'job-xyz', 'job_name holds the transcription id';
};

subtest 'AssemblyAI backend - poll completed job' => sub {
    my $body = '{"id":"job-xyz","status":"completed","text":"assembly result","confidence":0.95}';
    my $ua   = make_mock_ua( 200, $body );

    my $text;
    with_mock_ua(
        sub {
            $text = $r->recognize_assemblyai(
                undef,
                api_token => 'fake-token',
                job_name  => 'job-xyz',
            );
        },
        $ua
    );
    is $text, 'assembly result', 'polling a completed job returns transcript text';
};

subtest 'AssemblyAI backend - poll still processing' => sub {
    my $ua = make_mock_ua( 200, '{"id":"job-xyz","status":"processing"}' );

    my $exc;
    with_mock_ua(
        sub {
            eval {
                $r->recognize_assemblyai(
                    undef,
                    api_token => 'fake-token',
                    job_name  => 'job-xyz',
                );
            };
            $exc = $@;
        },
        $ua
    );
    ok ref $exc && $exc->isa('Speech::Recognition::Exception::TranscriptionNotReady'),
        'processing status re-throws TranscriptionNotReady';
    is $exc->job_name, 'job-xyz', 'job_name preserved in re-thrown exception';
};

subtest 'AssemblyAI backend - poll error status' => sub {
    my $ua = make_mock_ua( 200, '{"id":"job-xyz","status":"error","error":"bad audio"}' );

    my $exc;
    with_mock_ua(
        sub {
            eval {
                $r->recognize_assemblyai(
                    undef,
                    api_token => 'fake-token',
                    job_name  => 'job-xyz',
                );
            };
            $exc = $@;
        },
        $ua
    );
    ok ref $exc && $exc->isa('Speech::Recognition::Exception::TranscriptionFailed'),
        'error status throws TranscriptionFailed';
};

subtest 'AssemblyAI backend - show_all on completed job' => sub {
    my $body = '{"id":"job-xyz","status":"completed","text":"full result","confidence":0.9}';
    my $ua   = make_mock_ua( 200, $body );

    my $all;
    with_mock_ua(
        sub {
            $all = $r->recognize_assemblyai(
                undef,
                api_token => 'fake-token',
                job_name  => 'job-xyz',
                show_all  => 1,
            );
        },
        $ua
    );
    is ref $all, 'HASH',             'show_all returns hash';
    is $all->{text}, 'full result',  'text field accessible in show_all result';
};

# ===========================================================================
# 6. Groq backend
# ===========================================================================

subtest 'Groq backend - successful transcription' => sub {
    my $body = '{"text":"groq result"}';
    my $ua   = make_mock_ua( 200, $body );

    my $audio = make_audio();
    my $text;
    with_mock_ua(
        sub { $text = $r->recognize_groq( $audio, api_key => 'gsk_fake' ) },
        $ua
    );
    is $text, 'groq result', 'Groq returns text field';
};

done_testing();
