use strict;
use warnings;
use Test::More;

# We test with the perl/ directory in @INC
use lib 'lib';

# ------------------------------------------------------------------
# 1. Main module loads
# ------------------------------------------------------------------
require_ok('Speech::Recognition')
    or BAIL_OUT('Speech::Recognition failed to load');

# ------------------------------------------------------------------
# 2. Submodules load
# ------------------------------------------------------------------
for my $mod (qw(
    Speech::Recognition::Exception
    Speech::Recognition::AudioData
    Speech::Recognition::AudioFile
    Speech::Recognition::Microphone
    Speech::Recognition::Recognizer
)) {
    require_ok($mod);
}

# ------------------------------------------------------------------
# 3. Backend modules load
# ------------------------------------------------------------------
for my $mod (qw(
    Speech::Recognition::Recognizer::Google
    Speech::Recognition::Recognizer::Wit
    Speech::Recognition::Recognizer::Azure
    Speech::Recognition::Recognizer::Bing
    Speech::Recognition::Recognizer::Houndify
    Speech::Recognition::Recognizer::IBM
    Speech::Recognition::Recognizer::OpenAI
    Speech::Recognition::Recognizer::Groq
    Speech::Recognition::Recognizer::AssemblyAI
    Speech::Recognition::Recognizer::GoogleCloud
    Speech::Recognition::Recognizer::Whisper
    Speech::Recognition::Recognizer::Yap
)) {
    require_ok($mod);
}

# ------------------------------------------------------------------
# 4. Version is defined
# ------------------------------------------------------------------
ok( defined $Speech::Recognition::VERSION, 'VERSION is defined' );
diag("Speech::Recognition version: $Speech::Recognition::VERSION");

done_testing();
