#!/usr/pkg/bin/perl

#
# Time-stamp: <2026/01/27 13:35:25 (UT+08:00) daisuke>
#

#
# programs
#
$csh    = '/bin/csh';
$perl   = '/usr/pkg/bin/perl';
$python = '/usr/pkg/bin/python3'
$sleep  = '/bin/sleep';

#
# parameters
#
$time_sleep = 1;

#
# files
#
#$datafile  = '/home/daisuke/radio_program_list.txt';
#$recradiko = '/home/daisuke/bin/recradiko_timefree.pl';
$file_program = sprintf ("%s/share/radio/radio_program_list.txt", $ENV{'HOME'});
#$file_command_timefree = sprintf ("%s/bin/radio_rec_timefree.pl", $ENV{'HOME'});
$file_command_timefree = sprintf ("%s/bin/radio_rec_radiko_timefree_202601.py",
				  $ENV{'HOME'});

unless (-e $file_program) {
    print STDERR "Cannot find the file \"$file_program\": $!\n";
    exit (0);
}

unless (-e $file_command_timefree) {
    print STDERR "Cannot find the file \"$file_command_timefree\": $!\n";
    exit (0);
}

#
# parameters
#

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

open (FILE, $file_program) or die "Cannot open file \"$file_program\": $!\n";
while (<FILE>) {
    next unless (/^\d/);
    next unless (/:/);

    chomp;
    #print "$_\n";

    ($dayofweek, $time_start, $time_end, $channel, $program) = split;

    next if ($channel eq "r1");
    next if ($channel eq "r2");
    next if ($channel eq "fm");

    (@dayofweeks) = split (/,/, $dayofweek);

    foreach $wday (@dayofweeks) {
    
	($start_hh, $start_mm) = split (/:/, $time_start);
	($end_hh, $end_mm)     = split (/:/, $time_end);

	$start_mm -= $margin_pre;
	$end_mm   += $margin_post;
	
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
#	    = sprintf ("%s -v -c %-13s -w %s -s %02d:%02d -e %02d:%02d -p %s", 
#		       $file_command_timefree, $channel, $num2wday{$wday}, 
#		       $start_hh, $start_mm, $end_hh, $end_mm, $program);
	($command) 
	    = sprintf ("%s -v -c %s -w %s -s %02d:%02d -e %02d:%02d -p %s", 
		       $file_command_timefree, $channel, $num2wday{$wday}, 
		       $start_hh, $start_mm, $end_hh, $end_mm, $program);

	print "echo \"$python $command\" | $csh\n";
#	print "$sleep $time_sleep\n";
    }
}
close (FILE);
