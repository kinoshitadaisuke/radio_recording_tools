#!/usr/pkg/bin/perl

#
# Time-stamp: <2024/08/16 19:13:12 (UT+8) daisuke>
#

use Getopt::Std;

#print "$#ARGV\n";

@list_channel_kanto    = ('FMT', 'FMJ', 'BAYFM78', 'YFM', 'INT', 'TBS', 'LFR', 'QRR', 'RN1');
@list_channel_kansai   = ('MBS', 'CCL', 'ALPHA-STATION', 'KISSFMKOBE', 'RN1');
@list_channel_others   = ('RN1');
@list_channel_ryukyu   = ('FM_OKINAWA', 'ROK', 'RN1');
@list_channel_fukuoka  = ('FMFUKUOKA', 'RN1');
@list_channel_kumamoto = ('FMK', 'RN1');
@list_channel_nhk      = ('r1', 'r2', 'fm');

#
# commands
#
$hostname = '/bin/hostname';

#$radio_program_list = '/home/daisuke/radio_program_list.txt';
$file_program = sprintf ("%s/share/radio/radio_program_list.txt", $ENV{'HOME'});

unless (-e $file_program) {
    print STDERR "Cannot find the file \"$file_program\": $!\n";
    exit (0);
}

$name = `$hostname -s`;
if ($name =~ /^n\d+$/) {
    ($n) = ($name =~ /^n(\d+)$/);
} elsif ($name =~ /^nb\d+$/) {
    ($n) = ($name =~ /^nb(\d+)$/);
    while ($n >= 10) {
	$n -= 10;
    }
} else {
    $n = 0;
}

$recording_margin = 3;
#$restart_margin   = 5;
$restart_margin   = 3 + $n;

for ($wday = 1; $wday < 8; $wday++) {
    for ($hh = 0; $hh < 24; $hh++) {
	for ($mm = 0; $mm < 60; $mm++) {
	    ($whhmm) = sprintf ("%01d_%02d:%02d", $wday, $hh, $mm);
	    $data{$whhmm} = 0;
	}
    }
}

###########################################################################

getopts ('r:h');

sub PrintUsage {
    print
	"\n",
	"radio_search_reboottime.pl\n",
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

if ($region eq "kanto") {
    #@channel_list = (@list_channel_kanto, @list_channel_nhk);
    @channel_list = (@list_channel_nhk);
} elsif ($region eq "kansai") {
    #@channel_list = (@list_channel_kansai, @list_channel_nhk);
    @channel_list = (@list_channel_nhk);
} elsif ($region eq "ryukyu") {
    #@channel_list = (@list_channel_ryukyu, @list_channel_nhk);
    @channel_list = (@list_channel_nhk);
} elsif ($region eq "fukuoka") {
    #@channel_list = (@list_channel_fukuoka, @list_channel_nhk);
    @channel_list = (@list_channel_nhk);
} elsif ($region eq "kumamoto") {
    #@channel_list = (@list_channel_kumamoto, @list_channel_nhk);
    @channel_list = (@list_channel_nhk);
} else {
    PrintUsage;
    
    exit (0);
}

###########################################################################

open (FILE, "$file_program") 
    or die "Cannot open file \"$file_program\": $!\n";

while (<FILE>) {
    next if (/^#/);
    next unless (/^\d/);
    next unless (/:/);

    ($wday, $start, $end, $channel, $program) = split;

    if ($wday =~ /,/) {
	(@wday) = split (/,/, $wday);
    } else {
	(@wday) = $wday;
    }

    foreach $dayofweek (@wday) {
	($start_hh, $start_mm) = split (/:/, $start);
	($end_hh,   $end_mm)   = split (/:/, $end);

	$start_min = $dayofweek * 1440 + $start_hh * 60 + $start_mm 
	    - $recording_margin;
	$end_min   = $dayofweek * 1440 + $end_hh * 60 + $end_mm 
	    + $recording_margin;

	if ($end_min < $start_min) {
	    $end_min += 1440;
	}

#	if ($start_min < 0) {
#	    $start_min += 1440;
#	    $dayofweek -= 1;
#	}
#	if ($end_min > 1439) {
#	    $end_min -= 1440;
#	    $dayofweek += 1;
#	}

	for ($min = $start_min; $min <= $end_min; $min++) {
	    $wday = int ( $min / 1440.0 );
	    $hh = int ( ( $min - $wday * 1440 ) / 60.0 );
	    $mm = $min - $wday * 1440 - $hh * 60;

	    $whhmm = sprintf ("%01d_%02d:%02d", $wday, $hh, $mm);

	    $region = 0;
	    foreach (@channel_list) {
		if ($channel eq $_) {
		    $region = 1;
		}
	    }
	    
	    $data{$whhmm} = 1 if ($region == 1);
	}
	
    }
}

foreach (sort keys %data) {
    next if ($data{$_} == 0);

    (@data_current) = ($_    =~ /(\d+)_(\d+):(\d+)/);
    (@data_prev)    = ($prev =~ /(\d+)_(\d+):(\d+)/);

    $time_current 
	= $data_current[0] * 1440 + $data_current[1] * 60 + $data_current[2];
    $time_prev
	= $data_prev[0] * 1440 + $data_prev[1] * 60 + $data_prev[2];

    $time_restart = $time_current - $restart_margin;
    $restart_wday = int ( $time_restart / 1440.0 );
    $restart_hh   = int ( ($time_restart - $restart_wday * 1440) / 60.0 );
    $restart_mm   = $time_restart - $restart_wday * 1440 - $restart_hh * 60;

    $restart_whhmm 
	= sprintf ("%01d_%02d:%02d", $restart_wday, $restart_hh, $restart_mm);
    
    if ( ($time_current - $time_prev == 1) or ($prev == "") ) {
	#print "### $_\n";
    } else {
	if ($data{$restart_whhmm} == 0) {
	    #print "\n$restart_whhmm\n\n### $_\n";
	    #printf ("%02d %02d * * %01d /root/bin/vpngate_restart_openvpn.pl\n", $restart_mm, $restart_hh, $restart_wday);
	    printf ("%02d %02d * * %01d /sbin/shutdown -r now\n", $restart_mm, $restart_hh, $restart_wday);
	}
    }
    
    $prev = $_;
}

close (FILE);
