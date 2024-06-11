#!/bin/csh

#
# Time-stamp: <2023/10/21 20:24:48 (CST) daisuke>
#

#
# commands
#
set csh   = "/bin/csh"
set date  = "/bin/date"
set gshuf = "/usr/pkg/bin/gshuf"

#
# date/time
#
set datetime = `$date +%Y%m%d_%H%M%S`

#
# files
#
set check_unrecorded  = "/home/daisuke/bin/radio_check_unrecorded.pl"
#set recording_script1 = "/tmp/recording1_$datetime_$$.csh"
#set recording_script2 = "/tmp/recording2_$datetime_$$.csh"
set recording_script1 = "/tmp/recording1_${datetime}_pid$$.csh"
set recording_script2 = "/tmp/recording2_${datetime}_pid$$.csh"

# counter
set i = 0

# do the radio program recording 10 times
while ($i < 1)
    # checking unrecorded radio programs
    $check_unrecorded >! $recording_script1
    # shuffling
    $gshuf $recording_script1 > $recording_script2
    # executing recording script
    $csh $recording_script2
    # incrementing counter
    @ i ++
end
