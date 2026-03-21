use strict;
use warnings;
use v5.36;
use Test::More;
use lib 'lib';

use Speech::Recognition::AudioData;
use Speech::Recognition::AudioFile;
use Speech::Recognition::Recognizer;

use File::Basename qw(dirname);
use File::Spec     ();
my $t_dir    = dirname( File::Spec->rel2abs(__FILE__) );
my $examples = File::Spec->catdir( $t_dir, '..', '..', 'examples' );
unless ( -d $examples ) {
    plan skip_all => 'examples/ directory not found relative to perl/t/';
}

my $english_wav  = "$examples/english.wav";
my $chinese_flac = "$examples/chinese.flac";
my $french_aiff  = "$examples/french.aiff";

my $have_flac = do {
    my $found = 0;
    for my $dir ( split /:/, ( $ENV{PATH} // '/usr/local/bin:/usr/bin:/bin' ) ) {
        if ( -f "$dir/flac" && -x "$dir/flac" ) { $found = 1; last }
    }
    $found;
};

my $r = Speech::Recognition::Recognizer->new;

subtest 'english.wav - basic loading' => sub {
    unless ( -f $english_wav ) {
        plan skip_all => 'english.wav not found';
        return;
    }

    my $audio;
    Speech::Recognition::AudioFile->new( filename => $english_wav )->with(
        sub ($src) { $audio = $r->record($src) }
    );

    ok defined $audio,                           'audio object created';
    is $audio->sample_rate,  44100,              'english.wav sample_rate is 44100 Hz';
    is $audio->sample_width, 2,                  'english.wav sample_width is 2 (16-bit)';
    ok length( $audio->frame_data ) > 0,         'frame_data is non-empty';
};

subtest 'english.wav - AudioData properties' => sub {
    unless ( -f $english_wav ) {
        plan skip_all => 'english.wav not found';
        return;
    }

    my $audio;
    Speech::Recognition::AudioFile->new( filename => $english_wav )->with(
        sub ($src) { $audio = $r->record($src) }
    );

    my $expected_bytes = $audio->sample_rate * $audio->sample_width;
    ok $expected_bytes > 0, 'sample_rate * sample_width > 0';
    ok length( $audio->frame_data ) % $audio->sample_width == 0,
        'frame_data length is a multiple of sample_width';
};

subtest 'english.wav - get_wav_data roundtrip' => sub {
    unless ( -f $english_wav ) {
        plan skip_all => 'english.wav not found';
        return;
    }

    my $audio;
    Speech::Recognition::AudioFile->new( filename => $english_wav )->with(
        sub ($src) { $audio = $r->record($src) }
    );

    my $wav = $audio->get_wav_data;
    ok defined $wav,                   'get_wav_data returns data';
    ok length($wav) > 44,              'WAV data is longer than just the header';
    is substr( $wav, 0, 4 ), 'RIFF',   'WAV starts with RIFF';
    is substr( $wav, 8, 4 ), 'WAVE',   'WAV has WAVE marker';
    ok index( $wav, 'data' ) >= 0,     'WAV has data chunk';

    my $wav_16k = $audio->get_wav_data( convert_rate => 16000 );
    ok length($wav_16k) < length($wav), 'downsampled WAV is smaller';
};

subtest 'english.wav - get_raw_data' => sub {
    unless ( -f $english_wav ) {
        plan skip_all => 'english.wav not found';
        return;
    }

    my $audio;
    Speech::Recognition::AudioFile->new( filename => $english_wav )->with(
        sub ($src) { $audio = $r->record($src) }
    );

    my $raw = $audio->get_raw_data;
    ok defined $raw,                        'get_raw_data returns data';
    is length($raw), length( $audio->frame_data ), 'raw data same length as frame_data (no conversion)';

    my $raw8 = $audio->get_raw_data( convert_width => 1 );
    is length($raw8), length($raw) / 2, '8-bit conversion halves byte count';
};

subtest 'french.aiff - basic loading' => sub {
    unless ( -f $french_aiff ) {
        plan skip_all => 'french.aiff not found';
        return;
    }

    my $audio;
    Speech::Recognition::AudioFile->new( filename => $french_aiff )->with(
        sub ($src) { $audio = $r->record($src) }
    );

    ok defined $audio,                     'AIFF audio object created';
    ok $audio->sample_rate > 0,            'AIFF sample_rate > 0';
    ok $audio->sample_width >= 1,          'AIFF sample_width >= 1';
    ok length( $audio->frame_data ) > 0,   'AIFF frame_data is non-empty';
};

subtest 'french.aiff - get_wav_data' => sub {
    unless ( -f $french_aiff ) {
        plan skip_all => 'french.aiff not found';
        return;
    }

    my $audio;
    Speech::Recognition::AudioFile->new( filename => $french_aiff )->with(
        sub ($src) { $audio = $r->record($src) }
    );

    my $wav = $audio->get_wav_data;
    is substr( $wav, 0, 4 ), 'RIFF', 'AIFF->WAV starts with RIFF';
    is substr( $wav, 8, 4 ), 'WAVE', 'AIFF->WAV has WAVE marker';
};

subtest 'chinese.flac - basic loading' => sub {
    unless ( $have_flac ) {
        plan skip_all => 'flac command not found on PATH - install flac to enable this test';
        return;
    }
    unless ( -f $chinese_flac ) {
        plan skip_all => 'chinese.flac not found';
        return;
    }

    my $audio;
    Speech::Recognition::AudioFile->new( filename => $chinese_flac )->with(
        sub ($src) { $audio = $r->record($src) }
    );

    ok defined $audio,                      'FLAC audio object created';
    is $audio->sample_rate,  48000,         'chinese.flac sample_rate is 48000 Hz';
    is $audio->sample_width, 2,             'chinese.flac sample_width is 2 (16-bit)';
    ok length( $audio->frame_data ) > 0,    'FLAC frame_data is non-empty';
};

subtest 'chinese.flac - get_wav_data and get_flac_data' => sub {
    unless ( $have_flac ) {
        plan skip_all => 'flac command not found on PATH';
        return;
    }
    unless ( -f $chinese_flac ) {
        plan skip_all => 'chinese.flac not found';
        return;
    }

    my $audio;
    Speech::Recognition::AudioFile->new( filename => $chinese_flac )->with(
        sub ($src) { $audio = $r->record($src) }
    );

    my $wav = $audio->get_wav_data;
    is substr( $wav, 0, 4 ), 'RIFF', 'FLAC->WAV starts with RIFF';

    my $flac_out = $audio->get_flac_data;
    is substr( $flac_out, 0, 4 ), 'fLaC', 'get_flac_data output starts with fLaC magic';
    ok length($flac_out) > 0, 'FLAC output is non-empty';
};

subtest 'AudioData - 24-bit (width=3) support' => sub {
    my $n_samples = 100;
    my @vals = map { int( sin( $_ / 10.0 ) * 8000000 ) } 0 .. $n_samples - 1;
    my $pcm = Speech::Recognition::AudioData::_pack24(
        map { my $v = $_ + 2**23; $v < 0 ? 0 : $v > 0xFFFFFF ? 0xFFFFFF : $v } @vals
    );

    my $audio = Speech::Recognition::AudioData->new(
        frame_data   => $pcm,
        sample_rate  => 44100,
        sample_width => 3,
    );

    is $audio->sample_width, 3,                     '24-bit audio created';
    is length( $audio->frame_data ), $n_samples * 3, '24-bit frame_data has correct byte count';

    my $raw16 = $audio->get_raw_data( convert_width => 2 );
    is length($raw16), $n_samples * 2, '24-bit -> 16-bit has correct byte count';

    my $raw8 = $audio->get_raw_data( convert_width => 1 );
    is length($raw8), $n_samples, '24-bit -> 8-bit has correct byte count';

    my $wav = $audio->get_wav_data;
    is substr( $wav, 0, 4 ), 'RIFF', '24-bit audio produces valid WAV';
};

done_testing();
