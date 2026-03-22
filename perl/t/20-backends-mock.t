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
require Speech::Recognition::Recognizer::GoogleCloud;
require Speech::Recognition::Recognizer::Whisper;
require Speech::Recognition::Recognizer::Yap;

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

# ===========================================================================
# 7. Google Cloud Speech-to-Text backend
# ===========================================================================

# Fake service-account credentials JSON (inline, so no file I/O needed).
my $FAKE_CREDS = '{"client_email":"test@project.iam.gserviceaccount.com","private_key":"fake-key"}';

subtest 'GoogleCloud backend - successful transcription' => sub {
    # Mock _make_jwt to bypass Crypt::OpenSSL::RSA
    local *Speech::Recognition::Recognizer::GoogleCloud::_make_jwt
        = sub { 'fake.jwt.signature' };

    my @responses = (
        HTTP::Response->new( 200, 'OK',
            HTTP::Headers->new( 'Content-Type' => 'application/json' ),
            '{"access_token":"fake_token","token_type":"Bearer","expires_in":3600}' ),
        HTTP::Response->new( 200, 'OK',
            HTTP::Headers->new( 'Content-Type' => 'application/json' ),
            '{"results":[{"alternatives":[{"transcript":"hello cloud"}]}]}' ),
    );
    my $call_num = 0;
    my $ua = Test::LWP::UserAgent->new( network_fallback => 0 );
    $ua->map_response( sub {1}, sub { $responses[ $call_num++ ] } );

    my $audio = make_audio();
    my $text;
    with_mock_ua(
        sub {
            $text = $r->recognize_google_cloud( $audio,
                credentials_json => $FAKE_CREDS,
            );
        },
        $ua
    );
    is $text, 'hello cloud', 'GoogleCloud returns transcript';
};

subtest 'GoogleCloud backend - OAuth token failure becomes RequestError' => sub {
    local *Speech::Recognition::Recognizer::GoogleCloud::_make_jwt
        = sub { 'fake.jwt.signature' };

    my $ua = make_mock_ua( 401, '{"error":"invalid_grant"}' );

    my $audio = make_audio();
    eval {
        with_mock_ua(
            sub {
                $r->recognize_google_cloud( $audio,
                    credentials_json => $FAKE_CREDS,
                );
            },
            $ua
        );
    };
    my $e = $@;
    ok ref $e && $e->isa('Speech::Recognition::Exception::RequestError'),
        'OAuth token failure becomes RequestError';
};

subtest 'GoogleCloud backend - empty results become UnknownValueError' => sub {
    local *Speech::Recognition::Recognizer::GoogleCloud::_make_jwt
        = sub { 'fake.jwt.signature' };

    my @responses = (
        HTTP::Response->new( 200, 'OK',
            HTTP::Headers->new( 'Content-Type' => 'application/json' ),
            '{"access_token":"fake_token","token_type":"Bearer","expires_in":3600}' ),
        HTTP::Response->new( 200, 'OK',
            HTTP::Headers->new( 'Content-Type' => 'application/json' ),
            '{"results":[]}' ),
    );
    my $call_num = 0;
    my $ua = Test::LWP::UserAgent->new( network_fallback => 0 );
    $ua->map_response( sub {1}, sub { $responses[ $call_num++ ] } );

    my $audio = make_audio();
    eval {
        with_mock_ua(
            sub {
                $r->recognize_google_cloud( $audio,
                    credentials_json => $FAKE_CREDS,
                );
            },
            $ua
        );
    };
    my $e = $@;
    ok ref $e && $e->isa('Speech::Recognition::Exception::UnknownValueError'),
        'empty results become UnknownValueError';
};

subtest 'GoogleCloud backend - show_all returns full hash' => sub {
    local *Speech::Recognition::Recognizer::GoogleCloud::_make_jwt
        = sub { 'fake.jwt.signature' };

    my @responses = (
        HTTP::Response->new( 200, 'OK',
            HTTP::Headers->new( 'Content-Type' => 'application/json' ),
            '{"access_token":"fake_token","token_type":"Bearer","expires_in":3600}' ),
        HTTP::Response->new( 200, 'OK',
            HTTP::Headers->new( 'Content-Type' => 'application/json' ),
            '{"results":[{"alternatives":[{"transcript":"raw text"}]}]}' ),
    );
    my $call_num = 0;
    my $ua = Test::LWP::UserAgent->new( network_fallback => 0 );
    $ua->map_response( sub {1}, sub { $responses[ $call_num++ ] } );

    my $audio = make_audio();
    my $all;
    with_mock_ua(
        sub {
            $all = $r->recognize_google_cloud( $audio,
                credentials_json => $FAKE_CREDS,
                show_all         => 1,
            );
        },
        $ua
    );
    is ref $all, 'HASH', 'show_all returns hashref';
    is $all->{results}[0]{alternatives}[0]{transcript}, 'raw text',
        'transcript accessible in show_all result';
};

# ===========================================================================
# 8. Local Whisper backend
# ===========================================================================

subtest 'Whisper backend - SetupError when no binary found' => sub {
    no warnings 'once';
    local *Speech::Recognition::Recognizer::_Base::which = sub { undef };
    my $audio = make_audio();
    eval { $r->recognize_whisper_local($audio) };
    my $e = $@;
    ok ref $e && $e->isa('Speech::Recognition::Exception::SetupError'),
        'missing whisper binary throws SetupError';
    like $e->message, qr/whisper/i, 'error message mentions whisper';
};

subtest 'Whisper backend - successful JSON parsing' => sub {
    local *Speech::Recognition::Recognizer::Whisper::_find_whisper_bin
        = sub { ( '/usr/bin/whisper', 'whisper' ) };
    local *Speech::Recognition::Recognizer::Whisper::_run_whisper
        = sub { return '{"text":"  hello whisper  "}' };

    my $audio = make_audio();
    my $text  = $r->recognize_whisper_local($audio);
    is $text, 'hello whisper', 'Whisper trims whitespace and returns transcript';
};

subtest 'Whisper backend - empty transcript becomes UnknownValueError' => sub {
    local *Speech::Recognition::Recognizer::Whisper::_find_whisper_bin
        = sub { ( '/usr/bin/whisper', 'whisper' ) };
    local *Speech::Recognition::Recognizer::Whisper::_run_whisper
        = sub { return '{"text":""}' };

    my $audio = make_audio();
    eval { $r->recognize_whisper_local($audio) };
    my $e = $@;
    ok ref $e && $e->isa('Speech::Recognition::Exception::UnknownValueError'),
        'empty transcript throws UnknownValueError';
};

subtest 'Whisper backend - show_all returns full result hash' => sub {
    local *Speech::Recognition::Recognizer::Whisper::_find_whisper_bin
        = sub { ( '/usr/bin/whisper', 'whisper' ) };
    local *Speech::Recognition::Recognizer::Whisper::_run_whisper
        = sub { return '{"text":"hello","segments":[]}' };

    my $audio  = make_audio();
    my $result = $r->recognize_whisper_local( $audio, show_all => 1 );
    is ref $result, 'HASH',    'show_all returns hashref';
    is $result->{text}, 'hello', 'text field accessible in show_all result';
};

subtest 'Whisper backend - srt response_format returns raw SRT' => sub {
    my $fake_srt = "1\n00:00:00,000 --> 00:00:02,000\nhello whisper\n";
    local *Speech::Recognition::Recognizer::Whisper::_find_whisper_bin
        = sub { ( '/usr/bin/whisper', 'whisper' ) };
    local *Speech::Recognition::Recognizer::Whisper::_run_whisper
        = sub { return $fake_srt };

    my $audio = make_audio();
    my $srt   = $r->recognize_whisper_local( $audio, response_format => 'srt' );
    is $srt, $fake_srt, 'srt format returns raw SRT content';
};

subtest 'Whisper backend - text response_format returns trimmed text' => sub {
    local *Speech::Recognition::Recognizer::Whisper::_find_whisper_bin
        = sub { ( '/usr/bin/whisper', 'whisper' ) };
    local *Speech::Recognition::Recognizer::Whisper::_run_whisper
        = sub { return "  hello whisper\n" };

    my $audio = make_audio();
    my $text  = $r->recognize_whisper_local( $audio, response_format => 'text' );
    is $text, 'hello whisper', 'text format trims whitespace';
};

subtest 'Whisper backend - invalid response_format throws SetupError' => sub {
    local *Speech::Recognition::Recognizer::Whisper::_find_whisper_bin
        = sub { ( '/usr/bin/whisper', 'whisper' ) };

    my $audio = make_audio();
    eval { $r->recognize_whisper_local( $audio, response_format => 'no-such-fmt' ) };
    my $e = $@;
    ok ref $e && $e->isa('Speech::Recognition::Exception::SetupError'),
        'unknown response_format throws SetupError';
};

# ===========================================================================
# 9. Yap (macOS on-device) backend
# ===========================================================================

subtest 'Yap backend - SetupError when yap not found' => sub {
    no warnings 'once';
    local *Speech::Recognition::Recognizer::Yap::_find_yap_bin = sub { undef };
    my $audio = make_audio();
    eval { $r->recognize_yap($audio) };
    my $e = $@;
    ok ref $e && $e->isa('Speech::Recognition::Exception::SetupError'),
        'missing yap binary throws SetupError';
    like $e->message, qr/yap/i, 'error message mentions yap';
};

subtest 'Yap backend - successful plain text transcription' => sub {
    local *Speech::Recognition::Recognizer::Yap::_find_yap_bin
        = sub { '/usr/local/bin/yap' };
    local *Speech::Recognition::Recognizer::_Base::run_cmd
        = sub { return ( "hello yap\n", '' ) };

    my $audio = make_audio();
    my $text  = $r->recognize_yap($audio);
    is $text, 'hello yap', 'Yap returns trimmed plain text';
};

subtest 'Yap backend - srt response_format returns raw SRT' => sub {
    my $fake_srt = "1\n00:00:00,000 --> 00:00:02,000\nhello yap\n";
    local *Speech::Recognition::Recognizer::Yap::_find_yap_bin
        = sub { '/usr/local/bin/yap' };
    local *Speech::Recognition::Recognizer::_Base::run_cmd
        = sub { return ( $fake_srt, '' ) };

    my $audio = make_audio();
    my $srt   = $r->recognize_yap( $audio, response_format => 'srt' );
    is $srt, $fake_srt, 'Yap srt format returns raw SRT content';
};

# Real yap --json shape: { metadata => {...}, segments => [{id,start,end,text,...}] }
my $YAP_JSON = '{"metadata":{"created":"2026-03-22T00:00:00Z","language":"en-US","duration":2.0},'
             . '"segments":[{"id":1,"start":0.0,"end":1.0,"text":"hello"},'
             .              '{"id":2,"start":1.0,"end":2.0,"text":"world"}]}';

subtest 'Yap backend - json response_format extracts transcript' => sub {
    local *Speech::Recognition::Recognizer::Yap::_find_yap_bin
        = sub { '/usr/local/bin/yap' };
    local *Speech::Recognition::Recognizer::_Base::run_cmd
        = sub { return ( $YAP_JSON, '' ) };

    my $audio = make_audio();
    my $text  = $r->recognize_yap( $audio, response_format => 'json' );
    is $text, 'hello world', 'Yap json format joins segment texts';
};

subtest 'Yap backend - json show_all returns full hash' => sub {
    local *Speech::Recognition::Recognizer::Yap::_find_yap_bin
        = sub { '/usr/local/bin/yap' };
    local *Speech::Recognition::Recognizer::_Base::run_cmd
        = sub { return ( $YAP_JSON, '' ) };

    my $audio  = make_audio();
    my $result = $r->recognize_yap( $audio,
        response_format => 'json',
        show_all        => 1,
    );
    is ref $result, 'HASH',                          'show_all returns hashref';
    is $result->{segments}[0]{text}, 'hello',        'first segment text accessible';
    is $result->{metadata}{language}, 'en-US',       'metadata accessible';
};

subtest 'Yap backend - empty text becomes UnknownValueError' => sub {
    local *Speech::Recognition::Recognizer::Yap::_find_yap_bin
        = sub { '/usr/local/bin/yap' };
    local *Speech::Recognition::Recognizer::_Base::run_cmd
        = sub { return ( '', '' ) };

    my $audio = make_audio();
    eval { $r->recognize_yap($audio) };
    my $e = $@;
    ok ref $e && $e->isa('Speech::Recognition::Exception::UnknownValueError'),
        'empty Yap output throws UnknownValueError';
};

subtest 'Yap backend - invalid response_format throws SetupError' => sub {
    local *Speech::Recognition::Recognizer::Yap::_find_yap_bin
        = sub { '/usr/local/bin/yap' };

    my $audio = make_audio();
    eval { $r->recognize_yap( $audio, response_format => 'no-such-fmt' ) };
    my $e = $@;
    ok ref $e && $e->isa('Speech::Recognition::Exception::SetupError'),
        'unknown response_format throws SetupError';
};

done_testing();
