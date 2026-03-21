#!/usr/bin/env perl
use v5.36;
use open ':std', ':utf8';
use FindBin;
use lib "$FindBin::Bin/lib";

use Speech::Recognition::AudioFile;
use Speech::Recognition::Recognizer;
use Speech::Recognition::Exception;

my $examples = "$FindBin::Bin/../examples";

my @tests = (
    { file => "$examples/english.wav",  lang => 'en-US', label => 'english.wav'  },
    { file => "$examples/french.aiff",  lang => 'fr-FR', label => 'french.aiff'  },
    { file => "$examples/chinese.flac", lang => 'zh-CN', label => 'chinese.flac' },
);

my $r = Speech::Recognition::Recognizer->new;

for my $t (@tests) {
    print "--- $t->{label} ---\n";
    my $audio;
    eval {
        my $src = Speech::Recognition::AudioFile->new(filename => $t->{file});
        $src->open;
        $audio = $r->record($src);
        $src->close;
    };
    if ($@) {
        print "  LOAD ERROR: $@\n";
        next;
    }

    printf "  sample_rate=%d  sample_width=%d  bytes=%d\n",
        $audio->sample_rate, $audio->sample_width, length($audio->frame_data);

    eval {
        my $text = $r->recognize_google($audio, language => $t->{lang});
        print "  Google says: $text\n";
    };
    if (my $e = $@) {
        if (ref $e && $e->isa('Speech::Recognition::Exception::UnknownValueError')) {
            print "  Google: could not understand audio\n";
        } elsif (ref $e && $e->isa('Speech::Recognition::Exception::RequestError')) {
            print "  Google RequestError: $e->{message}\n";
        } else {
            print "  ERROR: $e\n";
        }
    }
}
