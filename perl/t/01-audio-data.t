use strict;
use warnings;
use v5.36;
use Test::More;
use lib 'lib';

use Speech::Recognition::AudioData;
use Speech::Recognition::Exception;

my $PI = 4 * atan2( 1, 1 );

# ---------------------------------------------------------------------------
# Helper: generate raw PCM bytes (16-bit LE sine wave at 440 Hz)
# ---------------------------------------------------------------------------

sub make_pcm ( $nsamples, $rate = 16000, $sw = 2 ) {
    my @s;
    for my $i ( 0 .. $nsamples - 1 ) {
        my $v = sin( 2 * $PI * 440 * $i / $rate );
        push @s, int( $v * 32767 ) & 0xFFFF;
    }
    return pack 'v*', @s;
}

# ---------------------------------------------------------------------------
# 1. Constructor validation
# ---------------------------------------------------------------------------

subtest 'constructor - valid' => sub {
    my $pcm = make_pcm(100);
    my $a   = Speech::Recognition::AudioData->new(
        frame_data   => $pcm,
        sample_rate  => 16000,
        sample_width => 2,
    );
    ok defined $a,                      'object created';
    is $a->sample_rate,  16000,         'sample_rate accessor';
    is $a->sample_width, 2,             'sample_width accessor';
    is $a->frame_data,   $pcm,          'frame_data accessor';
};

subtest 'constructor - bad rate' => sub {
    eval {
        Speech::Recognition::AudioData->new(
            frame_data   => '',
            sample_rate  => 0,
            sample_width => 2,
        );
    };
    like $@, qr/positive integer/i, 'dies on zero sample_rate';
};

subtest 'constructor - bad width' => sub {
    eval {
        Speech::Recognition::AudioData->new(
            frame_data   => '',
            sample_rate  => 16000,
            sample_width => 5,
        );
    };
    like $@, qr/between 1 and 4/i, 'dies on sample_width=5';
};

# ---------------------------------------------------------------------------
# 2. get_segment
# ---------------------------------------------------------------------------

subtest 'get_segment' => sub {
    my $pcm = make_pcm(16000);    # 1 second at 16 kHz, 2 bytes/sample
    my $a   = Speech::Recognition::AudioData->new(
        frame_data   => $pcm,
        sample_rate  => 16000,
        sample_width => 2,
    );

    my $half = $a->get_segment( 0, 500 );    # first 500 ms
    is $half->sample_rate,  16000, 'segment sample_rate preserved';
    is $half->sample_width, 2,     'segment sample_width preserved';
    is length( $half->frame_data ), 16000,   # 0.5 s * 16000 Hz * 2 bytes
        'segment length correct (0-500 ms)';

    my $all = $a->get_segment;
    is length( $all->frame_data ), length($pcm), 'full segment == full data';

    my $tail = $a->get_segment(500);
    is length( $tail->frame_data ) + length( $half->frame_data ),
        length($pcm), 'first+last halves cover whole';
};

# ---------------------------------------------------------------------------
# 3. get_raw_data – no conversion
# ---------------------------------------------------------------------------

subtest 'get_raw_data passthrough' => sub {
    my $pcm = make_pcm(100);
    my $a   = Speech::Recognition::AudioData->new(
        frame_data   => $pcm,
        sample_rate  => 16000,
        sample_width => 2,
    );
    # No conversion requested; should return identical data
    # (modulo the signed-unsigned 8-bit dance, which doesn't apply here)
    my $raw = $a->get_raw_data;
    is length($raw), length($pcm), 'raw_data same length as input';
};

# ---------------------------------------------------------------------------
# 4. get_wav_data – round-trip through AudioFile
# ---------------------------------------------------------------------------

subtest 'get_wav_data structure' => sub {
    my $pcm = make_pcm(1600);
    my $a   = Speech::Recognition::AudioData->new(
        frame_data   => $pcm,
        sample_rate  => 16000,
        sample_width => 2,
    );
    my $wav = $a->get_wav_data;

    # Check WAV magic bytes
    is substr( $wav, 0, 4 ), 'RIFF', 'WAV starts with RIFF';
    is substr( $wav, 8, 4 ), 'WAVE', 'WAV has WAVE identifier';

    # Check data chunk is present
    ok $wav =~ /data/, 'WAV contains data chunk';
};

# ---------------------------------------------------------------------------
# 5. get_raw_data – rate conversion
# ---------------------------------------------------------------------------

subtest 'get_raw_data rate conversion' => sub {
    my $pcm = make_pcm(16000);    # 1 s at 16 kHz
    my $a   = Speech::Recognition::AudioData->new(
        frame_data   => $pcm,
        sample_rate  => 16000,
        sample_width => 2,
    );

    my $resampled = $a->get_raw_data( convert_rate => 8000 );
    # Should be approximately half the length (half the samples)
    my $ratio = length($resampled) / length($pcm);
    ok abs( $ratio - 0.5 ) < 0.01, "resampled length ~= input/2 (ratio=$ratio)";
};

# ---------------------------------------------------------------------------
# 6. get_raw_data – width conversion
# ---------------------------------------------------------------------------

subtest 'get_raw_data width conversion 16->8 bit' => sub {
    my $pcm = make_pcm(100);    # 100 samples, 16-bit, 200 bytes
    my $a   = Speech::Recognition::AudioData->new(
        frame_data   => $pcm,
        sample_rate  => 16000,
        sample_width => 2,
    );

    my $raw8 = $a->get_raw_data( convert_width => 1 );
    is length($raw8), 100, '16->8 bit halves the byte count';
};

# ---------------------------------------------------------------------------
# 7. AudioFile round-trip (WAV)
# ---------------------------------------------------------------------------

subtest 'AudioFile WAV round-trip' => sub {
    require Speech::Recognition::AudioFile;
    require Speech::Recognition::Recognizer;
    require File::Temp;

    # Create a temp WAV file
    my ( $fh, $fname ) = File::Temp::tempfile( SUFFIX => '.wav', UNLINK => 1 );
    binmode $fh;

    my $pcm = make_pcm(4800);    # 0.3 s at 16 kHz
    my $original = Speech::Recognition::AudioData->new(
        frame_data   => $pcm,
        sample_rate  => 16000,
        sample_width => 2,
    );
    print $fh $original->get_wav_data;
    close $fh;

    # Read back via AudioFile
    my $r = Speech::Recognition::Recognizer->new;
    my $audio;
    my $src = Speech::Recognition::AudioFile->new( filename => $fname );
    $src->with( sub ($s) { $audio = $r->record($s) } );

    ok defined $audio,                        'audio returned from AudioFile';
    is $audio->sample_rate,  16000,           'sample_rate preserved';
    is $audio->sample_width, 2,               'sample_width preserved';
    ok length( $audio->frame_data ) > 0,      'non-empty frame data';
};

# ---------------------------------------------------------------------------
# 7b. AudioFile round-trip (AIFF)
# ---------------------------------------------------------------------------

subtest 'AudioFile AIFF round-trip' => sub {
    require Speech::Recognition::AudioFile;
    require Speech::Recognition::Recognizer;
    require File::Temp;

    my $pcm = make_pcm(4800);    # 0.3 s at 16 kHz
    my $original = Speech::Recognition::AudioData->new(
        frame_data   => $pcm,
        sample_rate  => 16000,
        sample_width => 2,
    );

    my ( $fh, $fname ) = File::Temp::tempfile( SUFFIX => '.aiff', UNLINK => 1 );
    binmode $fh;
    print $fh $original->get_aiff_data;
    close $fh;

    my $r = Speech::Recognition::Recognizer->new;
    my $audio;
    Speech::Recognition::AudioFile->new( filename => $fname )->with(
        sub ($s) { $audio = $r->record($s) }
    );

    ok defined $audio,                   'AIFF audio returned';
    is $audio->sample_rate,  16000,      'AIFF sample_rate preserved';
    is $audio->sample_width, 2,          'AIFF sample_width preserved';
    ok length( $audio->frame_data ) > 0, 'AIFF non-empty frame data';
};

# ---------------------------------------------------------------------------
# 8. Exception classes
# ---------------------------------------------------------------------------

subtest 'exception classes' => sub {
    my $e = Speech::Recognition::Exception::RequestError->new('boom');
    ok $e->isa('Speech::Recognition::Exception'),              'inherits from base';
    ok $e->isa('Speech::Recognition::Exception::RequestError'), 'isa RequestError';
    is $e->message, 'boom', 'message accessor';
    like "$e", qr/boom/, 'stringification includes message';

    eval { Speech::Recognition::Exception::UnknownValueError->throw };
    ok ref $@ && $@->isa('Speech::Recognition::Exception::UnknownValueError'),
        'throw works for UnknownValueError';

    my $nr = Speech::Recognition::Exception::TranscriptionNotReady->new(
        'waiting', job_name => 'job-123'
    );
    is $nr->job_name, 'job-123', 'TranscriptionNotReady job_name';
};

# ---------------------------------------------------------------------------
# 9. Recognizer defaults
# ---------------------------------------------------------------------------

subtest 'Recognizer defaults' => sub {
    require Speech::Recognition::Recognizer;
    my $r = Speech::Recognition::Recognizer->new;
    is $r->energy_threshold,                  300,  'energy_threshold default';
    is $r->dynamic_energy_threshold,          1,    'dynamic_energy_threshold default';
    ok abs( $r->pause_threshold - 0.8 ) < 1e-9,    'pause_threshold default';
    ok !defined $r->operation_timeout,              'operation_timeout undef by default';
};

done_testing();
