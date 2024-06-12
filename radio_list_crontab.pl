#!/usr/pkg/bin/perl

# Time-stamp: <2024/06/12 09:32:06 (UT+8) daisuke>

use Getopt::Std;

#
# files
#
#$datafile  = '/home/daisuke/radio_program_list.txt';
#$recradiko = '/home/daisuke/bin/recradiko_timefree.pl';
#$recradio  = '/home/daisuke/bin/recradio.pl';
#$recnhk    = '/home/daisuke/bin/recnhkradio.pl';

$file_program = sprintf ("%s/share/radio/radio_program_list.txt", $ENV{'HOME'});
#$file_command_radiko = sprintf ("%s/bin/radio_rec_radiko.pl", $ENV{'HOME'});
$file_command_timefree = sprintf ("%s/bin/radio_rec_timefree.pl", $ENV{'HOME'});
#$file_command_nhk = sprintf ("%s/bin/radio_rec_nhk.pl", $ENV{'HOME'});
$file_command_nhk = sprintf ("%s/bin/radio_rec_nhk_now.py", $ENV{'HOME'});

unless (-e $file_program) {
    print STDERR "Cannot find the file \"$file_program\": $!\n";
    exit (0);
}

#unless (-e $file_command_radiko) {
#    print STDERR "Cannot find the file \"$file_command_radiko\": $!\n";
#    exit (0);
#}

unless (-e $file_command_timefree) {
    print STDERR "Cannot find the file \"$file_command_timefree\": $!\n";
    exit (0);
}

unless (-e $file_command_nhk) {
    print STDERR "Cannot find the file \"$file_command_nhk\": $!\n";
    exit (0);
}

#
# parameters
#

#@list_channel_kanto  = ('FMT', 'FMJ', 'BAYFM78', 'YFM', 'INT', 'TBS', 'LFR', 'QRR', 'RN1');
#@list_channel_kansai = ('MBS', 'CCL', 'ALPHA-STATION', 'KISSFMKOBE', 'RN1');
#@list_channel_others = ('FMFUKUOKA', 'FMK', 'FM_OKINAWA', 'ROK', 'RN1');
#@list_channel_nhk    = ('r1', 'r2', 'fm');

@list_channel_kanto    = ('FMT', 'FMJ', 'BAYFM78', 'YFM', 'INT', 'TBS', 'LFR', 'QRR', 'RN1');
@list_channel_kansai   = ('MBS', 'CCL', 'ALPHA-STATION', 'KISSFMKOBE', 'RN1');
@list_channel_others   = ('RN1');
@list_channel_ryukyu   = ('FM_OKINAWA', 'ROK', 'RN1');
@list_channel_fukuoka  = ('FMFUKUOKA', 'RN1');
@list_channel_kumamoto = ('FMK', 'RN1');
@list_channel_nhk      = ('r1', 'r2', 'fm');

# margin in minute
$margin_pre  = 3;
$margin_post = 3;

%daybefore = (
    1 => "7",
    2 => "1",
    3 => "2",
    4 => "3",
    5 => "4",
    6 => "5",
    7 => "6",
    );

%dayafter = (
    1 => "2",
    2 => "3",
    3 => "4",
    4 => "5",
    5 => "6",
    6 => "7",
    7 => "1",
    );

%wday2num = (
    Mon => 1,
    Tue => 2,
    Wed => 3,
    Thu => 4,
    Fri => 5,
    Sat => 6,
    Sun => 7,
    );

%num2wday = (
    0 => "Sun",
    1 => "Mon",
    2 => "Tue",
    3 => "Wed",
    4 => "Thu",
    5 => "Fri",
    6 => "Sat",
    7 => "Sun",
    );

###########################################################################

getopts ('r:h');

sub PrintUsage {
    print
	"\n",
	"radio_list_crontab.pl\n",
	"\n",
	"    (c) Kinoshita Daisuke, 2016, 2017, 2018\n",
	"\n",
	"  -r : region\n",
	"       kanto or kansai or ryukyu or fukuoka or kumamoto\n",
	"  -h : help message\n",
	"\n",
	"\n";

    exit (0);
}

&OptionAnalysis;

if ($opt_h) {
    PrintUsage;
}

sub OptionAnalysis {
    if ($opt_r) {
	$region = $opt_r;
    } else {
	$region = 'none';
    }

    unless ( ($region eq 'kanto') or ($region eq 'kansai') 
	     or ($region eq 'ryukyu') 
	     or ($region eq 'fukuoka') or ($region eq 'kumamoto') ) {
	#print STDERR "The choices for the option -r are \"kanto\" or \"kansai\" or \"ryukyu\" or \"fukuoka\" or \"kumamoto\"!\n";
	PrintUsage;
	exit (0);
    }
}

###########################################################################

open (FILE, $file_program) or die "Cannot open file \"$file_program\": $!\n";
while (<FILE>) {
    next unless (/^\d/);
    next unless (/:/);

    chomp;
    #print "$_\n";

    ($dayofweek, $time_start, $time_end, $channel, $program) = split;

    (@dayofweeks) = split (/,/, $dayofweek);

    foreach $wday (@dayofweeks) {
    
	($start_hh, $start_mm) = split (/:/, $time_start);
	($end_hh, $end_mm)     = split (/:/, $time_end);

	#($start_hhmm) = sprintf ("%02d%02d", $start_hh, $start_mm);
	
	$duration = $end_hh * 60.0 + $end_mm - $start_hh * 60.0 - $start_mm;
	if ($duration < 0.0) {
	    $duration += 1440.0;
	}
	$duration += $margin_pre;
	$duration += $margin_post;

	$start_mm -= $margin_pre;
	$end_mm   += $margin_post;

	# timezone difference between Japan and Taiwan
	#$start_hh -= 1;
	$start_hh -= 0;
	
	if ($start_mm < 0) {
	    $start_mm += 60;
	    $start_hh -= 1;
	}

	if ($end_mm > 59) {
	    $end_mm -= 60;
	    $end_hh += 1;
	}

	if ($start_hh < 0) {
	    $start_hh += 24;
	    $wday = %daybefore{$wday};
	}

	if ($end_hh > 23) {
	    $start_hh -= 24;
	    $wday = %dayafter{$wday};
	}

#	($command) 
#	    = sprintf ("%s -v -c %-7s -w %s -s %02d:%02d -e %02d:%02d -p %s", 
#		       $recradiko, $channel, $num2wday{$wday}, 
#		       $start_hh, $start_mm, $end_hh, $end_mm, $program);

#	($command)
#	    = sprintf ("%02d %02d * * %01d %s -c %-7s -d %3d -p %s",
#		       $start_mm, $start_hh, $wday, $recradio, $channel, 
#		       $duration, $program);

	$print = 'NO';
	if ( ($channel eq "fm") or ($channel eq "r1") or ($channel eq "r2") ) {
	    $print = 'YES';
#	    ($command)
#		= sprintf ("%02d %02d * * %01d %-32s -c %2s -d %3d -p %s",
#			   $start_mm, $start_hh, $wday, 
#			   $file_command_nhk, $channel, 
#			   $duration, $program);
	    ($command)
		= sprintf ("%02d %02d * * %01d %-32s -c %2s -d %3d -p %s -t %s",
			   $start_mm, $start_hh, $wday, 
			   $file_command_nhk, $channel, 
			   $duration, $program, $time_start);
#	} else {
#	    if ($region eq 'kanto') {
#		foreach (@list_channel_kanto) {
#		    if ($channel eq $_) {
#			$print = 'YES';
#		    }
#		}
#	    } elsif ($region eq 'kansai') {
#		foreach (@list_channel_kansai) {
#		    if ($channel eq $_) {
#			$print = 'YES';
#		    }
#		}
#	    } elsif ($region eq 'ryukyu') {
#		foreach (@list_channel_ryukyu) {
#		    if ($channel eq $_) {
#			$print = 'YES';
#		    }
#		}
#	    } elsif ($region eq 'fukuoka') {
#		foreach (@list_channel_fukuoka) {
#		    if ($channel eq $_) {
#			$print = 'YES';
#		    }
#		}
#	    } elsif ($region eq 'kumamoto') {
#		foreach (@list_channel_kumamoto) {
#		    if ($channel eq $_) {
#			$print = 'YES';
#		    }
#		}
#	    }
#	    ($command)
#		= sprintf ("%02d %02d * * %01d %-32s -c %-13s -d %3d -p %s",
#			   $start_mm, $start_hh, $wday, 
#			   $file_command_radiko, $channel, 
#			   $duration, $program);
#	    ($command)
#		= sprintf ("%02d %02d * * %01d %-32s -c %-13s -t %3d -p %s",
#			   $start_mm, $start_hh, $wday, 
#			   $file_command_radiko, $channel, 
#			   $duration, $program);
	}
	
	if ($print eq 'YES') {
	    print "$command\n";
	}
	
    }
}
close (FILE);
