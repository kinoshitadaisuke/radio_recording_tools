#!/usr/pkg/bin/python3.12

#
# Time-stamp: <2024/08/16 21:14:56 (UT+8) daisuke>
#

###########################################################################

#
# importing modules
#

# importing argparse module
import argparse

# importing datetime module
import datetime

# importing os module
import os

# importing sys module
import sys

# importing pathlib module
import pathlib

# importing subprocess module
import subprocess

# importing re module
import re

# importing shutil module
import shutil

# importing time module
import time

###########################################################################

#
# functions
#

def cal2mjd (year, month, day):
    if (month < 3):
        year  -= 1
        month += 12
    mjd = int (365.25 * (year + 4716) ) + int (30.6001 * (month + 1) ) + day \
        + ( 2 - int (year / 100) + int ( int (year / 100) / 4 ) ) \
        - 2401525.0
    return (mjd)

def mjd2cal (mjd):
    jd = mjd + 2400000.5 + 0.5
    Z  = int (jd)
    F  = jd - Z
    if (Z >= 2291161):
        alpha = int ( (Z - 1867216.25) / 36524.25 )
        A     = Z + 1 + alpha - int (alpha / 4)
    B = A + 1524
    C = int ( (B - 122.1) / 365.25 )
    D = int (365.25 * C)
    E = int ( (B - D) / 30.6001 )
    Day = B - D - int (30.6001 * E) + F
    if (E < 14):
        Month = E - 1
    else:
        Month = E - 13
    if (Month > 2):
        Year = C - 4716
    else:
        Year = C - 4715
    return (Year, Month, Day)

###########################################################################

#
# parameters and constants
#

# sleep time in second
sleep_time = 1

# time zone (it should be +9.0 = Japan)
timezone = +9.0

# day of week
num2dow = [ 'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' ]
dow2num = {
    'Sun': 0,
    'Mon': 1,
    'Tue': 2,
    'Wed': 3,
    'Thu': 4,
    'Fri': 5,
    'Sat': 6,
    }

# commands
command_dd     = '/bin/dd'
command_base64 = '/usr/pkg/bin/base64'
command_curl   = '/usr/pkg/bin/curl'
opt_curl       = '--insecure'
command_ffmpeg = '/usr/pkg/bin/ffmpeg6'

# list of commands for this script
list_command = [ command_base64, command_curl, command_ffmpeg ]

# existence check of commands
for command in list_command:
    path_command = pathlib.Path (command)
    if not ( path_command.exists () ):
        print ("#")
        print ("# ERROR: command %s does not exist!" % (command) )
        print ("#")
        sys.exit ()

# URLs
url_player   = 'https://radiko.jp/apps/js/playerCommon.js'
url_auth1    = 'https://radiko.jp/v2/api/auth1'
url_auth2    = 'https://radiko.jp/v2/api/auth2?radiko_session='
url_playlist = 'https://radiko.jp/v2/api/ts/playlist.m3u8'

###########################################################################

#
# command-line argument analysis
#

# initialising a parser
parser = argparse.ArgumentParser (description='recording radiko radio program')

# default values
default_channel   = 'FMT'
default_program   = 'lifestylemuseum'
default_dayofweek = 'Fri'
default_start     = '18:30'
default_end       = '19:00'
default_verbose   = 0

# help message
help_channel   = 'radio channel code (default: FMT)'
help_program   = 'radio program name (default: lifestylemuseum)'
help_dayofweek = 'day-of-week of program (default: Fri)'
help_start     = 'start time (JST) of program in HH:MM format (default: 18:30)'
help_end       = 'end time (JST) of program in HH:MM format (default: 19:00)'
help_verbose   = 'verbosity level (default: 0)'

# adding arguments
parser.add_argument ('-c', '--channel', default=default_channel, \
                     help=help_channel)
parser.add_argument ('-p', '--program', default=default_program, \
                     help=help_program)
parser.add_argument ('-w', '--dayofweek', default=default_dayofweek, \
                     help=help_dayofweek)
parser.add_argument ('-s', '--start', default=default_start, \
                     help=help_start)
parser.add_argument ('-e', '--end', default=default_end, \
                     help=help_end)
parser.add_argument ('-v', '--verbose', action='count', \
                     default=default_verbose, help=help_verbose)

# parsing arguments
args = parser.parse_args ()

# input parameters
channel    = args.channel
program    = args.program
dayofweek  = args.dayofweek
time_start = args.start
time_end   = args.end
verbosity  = args.verbose

###########################################################################

if (verbosity):
    print ("#")
    print ("# Input parameters")
    print ("#")
    print ("#  channel    = %s" % (channel) )
    print ("#  program    = %s" % (program) )
    print ("#  dayofweek  = %s" % (dayofweek) )
    print ("#  time_start = %s" % (time_start) )
    print ("#  time_end   = %s" % (time_end) )
    print ("#")

###########################################################################

#
# date/time
#

# getting current date/time
datetime_now = datetime.datetime.now ()

YYYY = datetime_now.year
MM   = datetime_now.month
DD   = datetime_now.day
hh   = datetime_now.hour
mm   = datetime_now.minute
ss   = datetime_now.second + datetime_now.microsecond * 10**-6
fday = hh / 24.0 + mm / 1440.0 + ss / 86400.0
mjd_ut0 = cal2mjd (YYYY, MM, DD)
mjd_lt  = mjd_ut0 + fday
mjd_now = mjd_ut0 + fday - timezone / 24.0
#dayofweek_now = (int (mjd_now) + 3) % 7
dayofweek_now = (int (mjd_lt) + 3) % 7
datetime_str = "%04d%02d%02dT%02d%02d%02d" % (YYYY, MM, DD, hh, mm, int (ss) )

(time_start_hh, time_start_mm) = time_start.split (':')
(time_end_hh, time_end_mm)     = time_end.split (':')
start_fday = int (time_start_hh) / 24.0 + int (time_start_mm) / 1440.0
end_fday   = int (time_end_hh) / 24.0 + int (time_end_mm) / 1440.0

if (start_fday < end_fday):
    program_length_day = end_fday - start_fday
else:
    program_length_day = end_fday - start_fday + 1.0

if (dow2num[dayofweek] == dayofweek_now):
    if (start_fday > fday):
        target_day_offset = -7
    else:
        if (fday > end_fday):
            target_day_offset = 0
        else:
            target_day_offset = -7
else:
    target_day_offset = dow2num[dayofweek] - dayofweek_now
    if (target_day_offset > 0):
        target_day_offset -= 7

#start_mjd = int (mjd_now + target_day_offset)
start_mjd = int (mjd_lt + target_day_offset)
(start_YYYY, start_MM, start_DD) = mjd2cal (start_mjd)

if (start_fday < end_fday):
    end_mjd = start_mjd
else:
    end_mjd = start_mjd + 1
(end_YYYY, end_MM, end_DD) = mjd2cal (end_mjd)

start_date_str = "%04d%02d%02d" % (start_YYYY, start_MM, start_DD)
start_hhmm_str = "%02d%02d" % (int (time_start_hh), int (time_start_mm) )

datetime_start = "%04d%02d%02d%02d%02d%02d" \
    % (start_YYYY, start_MM, start_DD, \
       int (time_start_hh), int (time_start_mm), 0)
datetime_end = "%04d%02d%02d%02d%02d%02d" \
    % (end_YYYY, end_MM, end_DD, \
       int (time_end_hh), int (time_end_mm), 0)

if (verbosity):
    print ("#")
    print ("# date/time now")
    print ("#")
    print ("#  date/time now (local) = %04d/%02d/%02dT%02d:%02d:%09.6f" \
           % (YYYY, MM, DD, hh, mm, ss) )
    print ("#  MJD (at UT 00:00)     = %f" % (mjd_ut0) )
    print ("#  MJD now               = %f" % (mjd_now) )
    print ("#  day-of-week now       = %d = %s" \
           % (dayofweek_now, num2dow[dayofweek_now]) )
    print ("#")
    print ("#  start_fday = %f" % (start_fday) )
    print ("#  end_fday   = %f" % (end_fday) )
    print ("#")
    print ("#  MJD_start = %d" % (start_mjd) )
    print ("#  MJD_end   = %d" % (end_mjd) )
    print ("#")
    print ("# target date/time")
    print ("#")
    print ("#  target MJD  = %f" % (start_mjd) )
    print ("#  target date = %04d/%02d/%02d" \
           % (start_YYYY, start_MM, start_DD) )
    print ("#  datetime_start = %s" % (datetime_start) )
    print ("#  datetime_end   = %s" % (datetime_end) )
    print ("#")

###########################################################################

#
# directories and files
#

# process ID
pid = os.getpid ()

# directories
dir_home = os.environ['HOME']
dir_data = "%s/audio/radio" % (dir_home)
dir_tmp  = "/tmp/r%s_%06d" % (datetime_str, pid)

# making directory if not exist
path_data = pathlib.Path (dir_data)
if not ( path_data.exists () ):
    path_data.mkdir (parents=True, exist_ok=True)
path_tmp = pathlib.Path (dir_tmp)
if not ( path_tmp.exists () ):
    path_tmp.mkdir (parents=True, exist_ok=True)

# files
file_player     = "%s/player.js" % (dir_tmp)
file_authkey    = "%s/authkey.data" % (dir_tmp)
file_auth1      = "%s/auth1.data" % (dir_tmp)
file_auth2      = "%s/auth2.data" % (dir_tmp)
file_partialkey = "%s/partial_key.data" % (dir_tmp)
file_playlist   = "%s/playlist.data" % (dir_tmp)
file_m3u        = "%s/%s_%s_%s.m3u" \
    % (dir_tmp, program, start_date_str, start_hhmm_str)
file_aaclist    = "%s/aac.list" % (dir_tmp)
file_aac_tmp    = "%s/%s_%s_%s.aac" \
    % (dir_tmp, program, start_date_str, start_hhmm_str)
file_aac        = "%s/%s_%s_%s.aac" \
    % (dir_data, program, start_date_str, start_hhmm_str)

if (verbosity):
    print ("#")
    print ("# directories and files")
    print ("#")
    print ("#  dir_home = %s" % (dir_home) )
    print ("#  dir_data = %s" % (dir_data) )
    print ("#  dir_tmp  = %s" % (dir_tmp) )
    print ("#")
    print ("#  file_player     = %s" % (file_player) )
    print ("#  file_authkey    = %s" % (file_authkey) )
    print ("#  file_auth1      = %s" % (file_auth1) )
    print ("#  file_auth2      = %s" % (file_auth2) )
    print ("#  file_partialkey = %s" % (file_partialkey) )
    print ("#  file_playlist   = %s" % (file_playlist) )
    print ("#")
    print ("#  file_m3u     = %s" % (file_m3u) )
    print ("#  file_aaclist = %s" % (file_aaclist) )
    print ("#  file_aac_tmp = %s" % (file_aac_tmp) )
    print ("#  file_aac     = %s" % (file_aac) )
    print ("#")

###########################################################################

#
# fetching data
#

# fetching radiko player

command_fetch_player = "%s %s -o %s %s" \
    % (command_curl, opt_curl, file_player, url_player)

if (verbosity):
    print ("#")
    print ("# Now, fetching Radiko player...")
    print ("#")
    print ("#  COMMAND: %s" % (command_fetch_player) )
    print ("#")

time.sleep (sleep_time)
subprocess.run (command_fetch_player, shell=True)

if (verbosity):
    print ("#")
    print ("# Finished fetching Radiko player!")
    print ("#")
    print ("#  COMMAND: %s" % (command_fetch_player) )
    print ("#")

# scanning Radiko JS player
    
if (verbosity):
    print ("#")
    print ("# Now, scanning Radiko JS player...")
    print ("#")
    
# player = new RadikoJSPlayer($audio[0], 'pc_html5', 'bcd151073c03b352e1ef2fd66c32209da9ca0afa', {
pattern_authkey \
    = re.compile ('player = new RadikoJSPlayer\(\S+,\s+\'(\S+)\',\s+\'(\S+)\',')
    
path_player = pathlib.Path (file_player)
if not ( path_player.exists () ):
    print ("#")
    print ("# ERROR: radiko player could not be downloaded!")
    print ("#")
    sys.exit ()
else:
    with open (file_player, 'r') as fh:
        for line in fh:
            match_authkey = re.search (pattern_authkey, line)
            if (match_authkey):
                radiko_app     = match_authkey.group (1)
                radiko_authkey = match_authkey.group (2)

if (verbosity):
    print ("#")
    print ("# Following information was obtained from radiko JS player")
    print ("#")
    print ("#  radiko_app     = %s" % (radiko_app) )
    print ("#  radiko_authkey = %s" % (radiko_authkey) )
    print ("#")

# writing authkey to file
    
if (verbosity):
    print ("#")
    print ("# Now, writing value of authkey into a file...")
    print ("#")

with open (file_authkey, 'w') as fh:
    fh.write (radiko_authkey)

if (verbosity):
    print ("#")
    print ("# Finished writing value of authkey into a file!")
    print ("#")

# fetching auth1

opt_curl_header1 = '--header "pragma: no-cache"'
opt_curl_header2 = "--header \"X-Radiko-App: %s\"" % (radiko_app)
opt_curl_header3 = '--header "X-Radiko-App-Version: 0.0.1"'
opt_curl_header4 = '--header "X-Radiko-User: dummy_user"'
opt_curl_header5 = '--header "X-Radiko-Device: pc"'
opt_curl_header6 = '--header "X-Radiko-AuthToken: ___AUTHTOKEN___"'
opt_curl_header7 = '--header "X-Radiko-PartialKey: ___PARTIALKEY___"'
opt_curl_header8 = '--header "Content-Type: application/x-www-form-urlencoded"'
opt_curl_header9 = '--header "Referer: https://radiko.jp/"'
opt_curl_include = '--include'
opt_curl_flash   = '--data "flash=1"'

opt_curl_auth1 = "%s %s %s %s %s %s %s" \
    % (opt_curl, opt_curl_header1, opt_curl_header2, opt_curl_header3, \
       opt_curl_header4, opt_curl_header5, opt_curl_include)

command_fetch_auth1 = "%s %s -o %s %s" \
    % (command_curl, opt_curl_auth1, file_auth1, url_auth1)

if (verbosity):
    print ("#")
    print ("# Now, fetching auth1...")
    print ("#")
    print ("#  COMMAND: %s" % (command_fetch_auth1) )
    print ("#")

time.sleep (sleep_time)
subprocess.run (command_fetch_auth1, shell=True)

if (verbosity):
    print ("#")
    print ("# Finished fetching auth1!")
    print ("#")
    print ("#  COMMAND: %s" % (command_fetch_auth1) )
    print ("#")

# scanning auth1 data
    
# X-Radiko-AuthToken: oZSYOkBPCEYafLfqPexZiA
# X-Radiko-KeyLength: 16
# X-Radiko-KeyOffset: 13
pattern_authtoken = re.compile ('X-Radiko-AuthToken:\s+(\S+)', re.IGNORECASE)
pattern_keylength = re.compile ('X-Radiko-KeyLength:\s+(\S+)', re.IGNORECASE)
pattern_keyoffset = re.compile ('X-Radiko-KeyOffset:\s+(\S+)', re.IGNORECASE)

path_auth1 = pathlib.Path (file_auth1)
if not ( path_auth1.exists () ):
    print ("#")
    print ("# ERROR: auth1 file could not be downloaded!")
    print ("#")
    sys.exit ()
else:
    with open (file_auth1, 'r') as fh:
        for line in fh:
            match_authtoken = re.search (pattern_authtoken, line)
            if (match_authtoken):
                authtoken = match_authtoken.group (1)
            match_keylength = re.search (pattern_keylength, line)
            if (match_keylength):
                keylength = int ( match_keylength.group (1) )
            match_keyoffset = re.search (pattern_keyoffset, line)
            if (match_keyoffset):
                keyoffset = int ( match_keyoffset.group (1) )

if (verbosity):
    print ("#")
    print ("# Information extracted from auth1 file")
    print ("#")
    print ("#  authtoken = %s" % (authtoken) )
    print ("#  keylength = %d" % (keylength) )
    print ("#  keyoffset = %d" % (keyoffset) )
    print ("#")
    
# extracting partial key

command_extract_partial_key = "%s if=%s of=%s bs=1 skip=%d count=%d" \
    % (command_dd, file_authkey, file_partialkey, keyoffset, keylength)

if (verbosity):
    print ("#")
    print ("# Now, extracting partial key...")
    print ("#")
    print ("#  COMMAND: %s" % (command_extract_partial_key) )
    print ("#")

time.sleep (sleep_time)
subprocess.run (command_extract_partial_key, shell=True)

if (verbosity):
    print ("#")
    print ("# Finished extracting partial key!")
    print ("#")
    print ("#  COMMAND: %s" % (command_extract_partial_key) )
    print ("#")

# encoding partial key using base64

command_encode_partial_key = "%s < %s" % (command_base64, file_partialkey)

if (verbosity):
    print ("#")
    print ("# Now, encoding partial key using base64...")
    print ("#")
    print ("#  COMMAND: %s" % (command_encode_partial_key) )
    print ("#")

time.sleep (sleep_time)
result_encode_partial_key = subprocess.run (command_encode_partial_key, \
                                            shell=True, capture_output=True)

partialkey_value = result_encode_partial_key.stdout.decode ('utf-8')

if (verbosity):
    print ("#")
    print ("# Finished encoding partial key using base64!")
    print ("#")
    print ("#  partial key = %s" % (partialkey_value) )
    print ("#")

# fetching auth2 data

pattern_authtoken_value  = re.compile ('___AUTHTOKEN___')
pattern_partialkey_value = re.compile ('___PARTIALKEY___')

opt_curl_header6 = re.sub (pattern_authtoken_value, authtoken, \
                           opt_curl_header6)
opt_curl_header7 = re.sub (pattern_partialkey_value, partialkey_value, \
                           opt_curl_header7)

opt_curl_auth2 = "%s %s %s %s %s %s %s %s" \
    % (opt_curl, opt_curl_header1, opt_curl_header2, opt_curl_header3, \
       opt_curl_header4, opt_curl_header5, opt_curl_header6, opt_curl_header7)

command_fetch_auth2 = "%s %s -o %s '%s'" \
    % (command_curl, opt_curl_auth2, file_auth2, url_auth2)

if (verbosity):
    print ("#")
    print ("# Now, fetching auth2...")
    print ("#")
    print ("#  COMMAND: %s" % (command_fetch_auth2) )
    print ("#")

time.sleep (sleep_time)
subprocess.run (command_fetch_auth2, shell=True)

if (verbosity):
    print ("#")
    print ("# Finished fetching auth2!")
    print ("#")
    print ("#  COMMAND: %s" % (command_fetch_auth2) )
    print ("#")

# fetching play list

opt_curl_playlist = "%s %s %s %s %s %s" \
    % (opt_curl, opt_curl_header1, opt_curl_header6, opt_curl_header8, \
       opt_curl_header9, opt_curl_flash)

command_fetch_playlist = "%s %s -o %s '%s?l=15&station_id=%s&ft=%s&to=%s'" \
    % (command_curl, opt_curl_playlist, file_playlist, url_playlist, \
       channel, datetime_start, datetime_end)

if (verbosity):
    print ("#")
    print ("# Now, fetching playlist...")
    print ("#")
    print ("#  COMMAND: %s" % (command_fetch_playlist) )
    print ("#")

time.sleep (sleep_time)
subprocess.run (command_fetch_playlist, shell=True)

if (verbosity):
    print ("#")
    print ("# Finished fetching playlist!")
    print ("#")
    print ("#  COMMAND: %s" % (command_fetch_playlist) )
    print ("#")

# extract stream URL from playlist

path_playlist = pathlib.Path (file_playlist)
if not ( path_playlist.exists () ):
    print ("#")
    print ("# ERROR: playlist file could not be downloaded!")
    print ("#")
    sys.exit ()
else:
    with open (file_playlist, 'r') as fh:
        for line in fh:
            if (line[0] == '#'):
                continue
            if (line[0:18] == 'https://radiko.jp/'):
                url_m3u = line.rstrip ()

# fetching m3u file

user_agent \
    = 'Mozilla/5.0 (X11; NetBSD amd64; rv:109.0) Gecko/20100101 Firefox/115.0'
#    = 'Mozilla/5.0 (X11; NetBSD amd64; rv:91.0) Gecko/20100101 Firefox/91.0'

if (url_m3u):
    command_fetch_m3u = "%s %s --user-agent '%s' -o %s %s" \
        % (command_curl, opt_curl, user_agent, file_m3u, url_m3u)
else:
    print ("#")
    print ("# ERROR: could not fetch m3u8 URL!")
    print ("#")
    sys.exit ()

print (command_fetch_m3u)

if (verbosity):
    print ("#")
    print ("# Now, fetching m3u8 file...")
    print ("#")
    print ("#  COMMAND: %s" % (command_fetch_m3u) )
    print ("#")

time.sleep (sleep_time)
subprocess.run (command_fetch_m3u, shell=True)

if (verbosity):
    print ("#")
    print ("# Finished fetching m3u8 file!")
    print ("#")
    print ("#  COMMAND: %s" % (command_fetch_m3u) )
    print ("#")

# extracting URLs of AAC files

path_m3u = pathlib.Path (file_m3u)
if not ( path_m3u.exists () ):
    print ("#")
    print ("# ERROR: m3u file could not be downloaded!")
    print ("#")
    sys.exit ()
else:
    with open (file_aaclist, 'w') as aaclist:
        with open (file_m3u, 'r') as fh:
            #command_fetch_aac = "%s %s" % (command_curl, opt_curl)
            for line in fh:
                if (line[0] == '#'):
                    continue
                if (line[0:5] == 'https'):
                    pattern_YYYYMMDD_hhmmss \
                        = re.compile ('(\d{8}_\d{6})')
                    match_YYYYMMDD_hhmmss \
                        = re.search (pattern_YYYYMMDD_hhmmss, line)
                    if (match_YYYYMMDD_hhmmss):
                        segment_name = match_YYYYMMDD_hhmmss.group (1)
                        file_segment = "%s/%s.aac" % (dir_tmp, segment_name)
                        #command_fetch_aac = "%s -o %s %s" \
                        #    % (command_fetch_aac, file_segment, line.rstrip() )
                        #time.sleep (sleep_time)
                        command_fetch_aac = "%s %s -o %s %s" \
                            % (command_curl, opt_curl, file_segment, \
                               line.rstrip () )
                        subprocess.run (command_fetch_aac, shell=True)
                        filename = "file '%s'\n" % (file_segment)
                        aaclist.write (filename)
        aaclist.flush ()
    #print (command_fetch_aac)
    #subprocess.run (command_fetch_aac, shell=True)

# concatenate AAC files

command_concatenate_aac = "%s -f concat -safe 0 -i %s -vn -acodec copy %s" \
    % (command_ffmpeg, file_aaclist, file_aac_tmp)

print (command_concatenate_aac)

if (verbosity):
    print ("#")
    print ("# Now, concatenating AAC files...")
    print ("#")
    print ("#  COMMAND: %s" % (command_concatenate_aac) )
    print ("#")

time.sleep (sleep_time)
subprocess.run (command_concatenate_aac, shell=True)

if (verbosity):
    print ("#")
    print ("# Finished concatenating AAC files!")
    print ("#")
    print ("#  COMMAND: %s" % (command_concatenate_aac) )
    print ("#")

# copying AAC file

path_aac_tmp = pathlib.Path (file_aac_tmp)
path_aac     = pathlib.Path (file_aac)

if not ( path_aac.exists () ):
    size_old = 0
else:
    size_old = path_aac.stat ().st_size

if not ( path_aac_tmp.exists () ):
    size_new = 0
else:
    size_new = path_aac_tmp.stat ().st_size

if (verbosity):
    print ("#")
    print ("# Sizes of AAC files")
    print ("#")
    print ("# old file: %10d byte" % size_old)
    print ("# new file: %10d byte" % size_new)
    print ("#")
    
if not ( ( path_aac.exists () ) and (size_old >= size_new) ):
    if (verbosity):
        print ("#")
        print ("# Now, copying AAC file...")
        print ("#")
        print ("#  %s ==> %s" % (file_aac_tmp, file_aac) )
        print ("#")
    shutil.copy2 (path_aac_tmp, path_aac)
    if (verbosity):
        print ("#")
        print ("# Finished copying AAC file!")
        print ("#")

# deleting AAC files
list_aac_files = path_tmp.glob ('*.aac')
for path_aac_for_delete in list_aac_files:
    if (path_aac_for_delete.exists ()):
        path_aac_for_delete.unlink ()
