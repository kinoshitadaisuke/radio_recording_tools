#!/usr/pkg/bin/perl

#
# Time-stamp: <2024/08/17 19:08:16 (UT+8) daisuke>
#

#
# URLs
#
#$url_radio_index = 'http://140.115.9.226/~daisuke/radio/';
#$url_radio_index = 'http://140.115.9.192/~daisuke/radio/';
#$url_radio_index = 'https://140.115.9.192/~daisuke/radio/';
#$url_radio_index = 'https://140.115.9.192/~daisuke/radio/thisweek.html';
#$url_radio_index = 'https://140.115.9.56/~daisuke/radio/thisweek.html';
#$url_radio_index = 'https://140.115.9.56:8888/~daisuke/radio/thisweek.html';
$url_radio_index = 'https://140.115.9.56:58888/~daisuke/radio/thisweek.html';

#
# directories
#
$dir_tmp       = sprintf ("/tmp/radio_check_%d", $$);

unless (-e $dir_tmp) {
    mkdir $dir_tmp;
}

#
# files
#
#$file_radio_index = sprintf ("%s/index.html", $dir_tmp);
$file_radio_index = sprintf ("%s/thisweek.html", $dir_tmp);

$file_program = sprintf ("%s/share/radio/radio_program_list.txt", $ENV{'HOME'});
#$file_command_timefree = sprintf ("%s/bin/radio_rec_timefree.pl", $ENV{'HOME'});
$file_command_timefree = sprintf ("%s/bin/radio_rec_radiko_timefree.py",
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
# commands
#
$csh        = '/bin/csh';
$dd         = '/bin/dd';
$echo       = '/bin/echo';
$wget       = '/usr/pkg/bin/wget';
$curl       = '/usr/pkg/bin/curl';
$base64     = '/usr/pkg/bin/base64';
$rtmpdump   = '/usr/pkg/bin/rtmpdump';
$ffmpeg1    = '/usr/pkg/bin/ffmpeg1';
$ffmpeg2    = '/usr/pkg/bin/ffmpeg2';
$ffmpeg3    = '/usr/pkg/bin/ffmpeg3';
$ffmpeg4    = '/usr/pkg/bin/ffmpeg4';
$ffmpeg5    = '/usr/pkg/bin/ffmpeg5';
$swfextract = '/usr/pkg/bin/swfextract';

#(@list_commands) = ($dd, $curl, $base64, $rtmpdump, $ffmpeg4, $swfextract);
(@list_commands) = ($curl);

foreach (@list_commands) {
    unless (-e $_) {
	print STDERR "The command \"$_\" does not exist!\n";
	print STDERR "Install the command \"$_\"!\n";
	exit (0);
    }
}

#
# parameters
#

# margin in minute
$margin_pre  = 3;
$margin_post = 3;

# threshold for file size
#$threshold_size = 99.995;
$threshold_size = 99.99;

undef @fetch_list;

@week = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun');

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

#
# Time
#
my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
$year += 1900;
$mon++;

$sec_from_day_start = $hour * 3600.0 + $min * 60.0 + $sec;

#print "day of week = $wday = $week[$wday]\n";

###########################################################################

#$command_fetch_radio_index = sprintf ("%s --insecure --output %s --user mhdf:tw32001taoyuan200308ncu %s", 
#				      $curl, 
#				      $file_radio_index, $url_radio_index);
#$command_fetch_radio_index = sprintf ("%s --insecure --output %s --user d_command:32001s41006c %s",
#				      $curl, $file_radio_index, $url_radio_index);
$command_fetch_radio_index = sprintf ("%s --tlsv1.3 --insecure --output %s --user d_command:32001s41006c %s",
				      $curl, $file_radio_index, $url_radio_index);
#print "$command_fetch_radio_index\n";
system ("$command_fetch_radio_index");

open (RADIO_INDEX, "$file_radio_index") 
    or die "Cannot open the file \"$file_radio_index\": $!\n";
while (<RADIO_INDEX>) {
    chomp;

    if ( (/^<h3>/) and (/<\/h3>$/) ){
	($dayofweek) 
	    = /^<h3>Radio programs recorded on \d{4}-\d{2}-\d{2} \((\w{3})\)<\/h3>$/;
    }
    
    next unless ( (/^<tr><td align=left>/) and (/<\/td><\/tr>$/) );

    if (/<font color=red>/) {
	# <tr><td align=left><font color=red>oto</font></td><td align=left><font color=red>fm</font></td>
	($program, $channel) = /^<tr><td align=left><font color=red>(\S+)<\/font><\/td><td align=left><font color=red>(\S+)<\/font><\/td>/;
    } else {
	($program, $channel) = /^<tr><td align=left>(\S+)<\/td><td align=left>(\S+)<\/td>/;
    }

    next if ( ($channel eq 'fm') or ($channel eq 'r1') or ($channel eq 'r2') );
    
    ($time_start, $time_end) 
	= /(\d{2}:\d{2})<\/td><td align=center>(\d{2}:\d{2})/;
    ($time_start_HH, $time_start_MM) = split (/:/, $time_start);
    $time_start_sec_from_day_start 
	= $time_start_HH * 3600.0 + $time_start_MM * 60.0 - $margin_pre * 60.0;
    ($time_end_HH, $time_end_MM) = split (/:/, $time_end);
    $time_end_sec_from_day_start 
	= $time_end_HH * 3600.0 + $time_end_MM * 60.0 + $margin_post * 60.0;

    $size_percent = -99.9;
    if (/&#37;/) {
	if (/color=red/) {
	    ($size_percent) = /<td align=right><font color=red>\s*([.\d]+)&#37;<\/font><\/td>/;
	} else {
	    ($size_percent) = /<td align=right>\s*([.\d]+)&#37;<\/td>/;
	}
    } else {
	($size_percent) = 0.0;
    }

    #next if ($size_percent >= 100.0);
    #next if ($size_percent > 99.997);
    next if ($size_percent >= $threshold_size);
    
    $fetch = 'NO';

    if ($dayofweek eq $week[$wday]) {
	if ($sec_from_day_start > $time_end_sec_from_day_start) {
	    $fetch = 'YES';
	}
	if ($time_start_sec_from_day_start > $time_end_sec_from_day_start) {
	    $fetch = 'NO';
	}
    } else {
	$fetch = 'YES';
	if ( ($dayofweek eq $week[$wday + 1]) and ($sec_from_day_start > 82800.0) ) {
	    $fetch = 'NO';
	}
    }
    
    if ($fetch eq 'YES') {
#	printf ("%-24s    %14s    %3s    %5s    %5s    %5.1f\n", 
#		$program, $channel, $dayofweek, $time_start, $time_end, $size_percent);
	($program_channel_dayofweek) = sprintf ("%s_____%s_____%s", 
						$program, $channel, $dayofweek);
	push (@fetch_list, $program_channel_dayofweek)
    }
}
close (RADIO_INDEX);

#foreach (@fetch_list) {
#    print "$_\n";
#}

###########################################################################

open (FILE, $file_program) or die "Cannot open file \"$file_program\": $!\n";
while (<FILE>) {
    next unless (/^\d/);
    next unless (/:/);

    chomp;

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

	($command) 
	    = sprintf ("%s -v -c %-13s -w %s -s %02d:%02d -e %02d:%02d -p %s", 
		       $file_command_timefree, $channel, $num2wday{$wday}, 
		       $start_hh, $start_mm, $end_hh, $end_mm, $program);

	foreach (@fetch_list) {
	    ($target_program, $target_channel, $target_dayofweek) 
		= split (/_____/, $_);
	    if ( ($target_program eq $program) 
		 and ($target_channel eq $channel) 
		 and ($target_dayofweek eq $week[$wday]) ) {

		print "$echo \"$command\" | $csh\n";
	    }
	}
    }
}
close (FILE);
