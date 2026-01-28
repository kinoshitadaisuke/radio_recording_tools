#!/usr/pkg/bin/python3.12

#
# Time-stamp: <2026/01/29 07:58:55 (UT+08:00) daisuke>
#

######################################################################
#                                                                    #
# Radiko recording                                                   #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
######################################################################

######################################################################
#                                                                    #
# Important notes                                                    #
#                                                                    #
#  system time must be set to JST.                                   #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
#                                                                    #
######################################################################

######################################################################

#
# Importing modules
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

######################################################################

#
# Constants
#

# user agent name
user_agent = 'Mozilla/5.0 (X11; NetBSD x86_64; rv:140.0) Gecko/20100101 Firefox/140.0'

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
opt_curl       = f'--insecure --user-agent "{user_agent}"'
command_ffmpeg = '/usr/pkg/bin/ffmpeg'
opt_ffmpeg_1   = f"-http_seekable 0 -seekable 0 -headers 'User-Agent: {user_agent}'"
opt_ffmpeg_2   = '-acodec copy -bsf:a aac_adtstoasc'

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
#url_playlist = 'https://radiko.jp/v2/api/ts/playlist.m3u8'
url_playlist = 'https://tf-f-rpaa-radiko.smartstream.ne.jp/tf/playlist.m3u8'

######################################################################

#
# Functions
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

######################################################################

#
# Command-line arguments analysis
#

# initialising a parser object
descr  = f'recording Radiko radio programs'
parser = argparse.ArgumentParser (description=descr)

# default values
default_channel   = f'FMT'
default_program   = f'lifestylemuseum'
default_dayofweek = f'Fri'
default_starttime = f'18:30'
default_endtime   = f'19:00'
default_verbose   = 0
default_sleeptime = 1
default_timezone  = +9.0

# help messages
help_channel   = f'radio channel code (default: FMT)'
help_program   = f'radio program name (default: lifestylemuseum)'
help_dayofweek = f'day-of-week of program (default: Fri)'
help_starttime = f'start time (JST) of program in HH:MM format (default: 18:30)'
help_endtime   = f'end time (JST) of program in HH:MM format (default: 19:00)'
help_verbose   = f'versobity level (default: 0)'
help_sleeptime = f'sleep time before executing shell command (default: 1)'
help_timezone  = f'timezone (default: +9.0)'

# adding arguments
parser.add_argument ('-c', '--channel', \
                     default=default_channel, \
                     help=help_channel)
parser.add_argument ('-p', '--program', \
                     default=default_program, \
                     help=help_program)
parser.add_argument ('-w', '--dayofweek', \
                     default=default_dayofweek, \
                     help=help_dayofweek)
parser.add_argument ('-s', '--start', \
                     default=default_starttime, \
                     help=help_starttime)
parser.add_argument ('-e', '--end', \
                     default=default_endtime, \
                     help=help_endtime)
parser.add_argument ('-l', '--sleeptime', \
                     default=default_sleeptime, \
                     help=help_sleeptime)
parser.add_argument ('-z', '--timezone', \
                     default=default_timezone, \
                     help=help_timezone)
parser.add_argument ('-v', '--verbose', action='count', \
                     default=default_verbose, \
                     help=help_verbose)

# parsing arguments
args = parser.parse_args ()

# input parameters
channel    = args.channel
program    = args.program
dayofweek  = args.dayofweek
time_start = args.start
time_end   = args.end
sleeptime  = args.sleeptime
timezone   = args.timezone
verbosity  = args.verbose

######################################################################

#
# Printing input parameters
#

if (verbosity):
    print (f'#')
    print (f'# Input parameters')
    print (f'#')
    print (f'#  channel    = "{channel}"')
    print (f'#  program    = "{program}"')
    print (f'#  dayofweek  = "{dayofweek}"')
    print (f'#  time_start = "{time_start}"')
    print (f'#  time_end   = "{time_end}"')
    print (f'#  sleeptime  = "{sleeptime}"')
    print (f'#  timezone   = "{timezone}"')
    print (f'#  verbosity  = "{verbosity}"')
    print (f'#')

######################################################################

#
# date/time
#

# getting current date/time in UTC
datetime_now = datetime.datetime.now (datetime.timezone.utc)

YYYY = datetime_now.year
MM   = datetime_now.month
DD   = datetime_now.day
hh   = datetime_now.hour
mm   = datetime_now.minute
ss   = datetime_now.second + datetime_now.microsecond * 10**-6

fday = hh / 24.0 + mm / 1440.0 + ss / 86400.0

mjd_ut0 = cal2mjd (YYYY, MM, DD)
mjd_now = mjd_ut0 + fday
mjd_lt  = mjd_now + timezone / 24.0

dayofweek_now = (int (mjd_lt) + 3) % 7
datetime_str  = "%04d%02d%02dT%02d%02d%02d" % (YYYY, MM, DD, hh, mm, int (ss) )

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
    print (f'#')
    print (f'# Date/time now')
    print (f'#')
    print (f'#  date/time now (UTC) = {YYYY:04d}/{MM:02d}/{DD:02d}T{hh:02d}:{mm:02d}:{ss:09.6f}')
    print (f'#  MJD (at UT 00:00)   = {mjd_ut0}')
    print (f'#  MJD now             = {mjd_now}')
    print (f'#  day-of-week now     = {dayofweek_now} ({num2dow[dayofweek_now]})')
    print (f'#')
    print (f'#  start_fday = {start_fday}')
    print (f'#  end_fday   = {end_fday}')
    print (f'#')
    print (f'#  MJD_start = {start_mjd}')
    print (f'#  MJD_end   = {end_mjd}')
    print (f'#')
    print (f'# target date/time')
    print (f'#')
    print (f'#  target MJD     = {start_mjd}')
    print (f'#  target date    = {start_YYYY:04d}/{start_MM:02d}/{int (start_DD):02d}')
    print (f'#  datetime_start = {datetime_start}')
    print (f'#  datetime_end   = {datetime_end}')
    print (f'#')

######################################################################

#
# Directories and files
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
    print (f'#')
    print (f'# Directories and files')
    print (f'#')
    print (f'#  dir_home = {dir_home}')
    print (f'#  dir_data = {dir_data}')
    print (f'#  dir_tmp  = {dir_tmp}')
    print (f'#')
    print (f'#  file_player     = {file_player}')
    print (f'#  file_authkey    = {file_authkey}')
    print (f'#  file_auth1      = {file_auth1}')
    print (f'#  file_auth2      = {file_auth2}')
    print (f'#  file_partialkey = {file_partialkey}')
    print (f'#  file_playlist   = {file_playlist}')
    print (f'#')
    print (f'#  file_m3u     = {file_m3u}')
    print (f'#  file_aaclist = {file_aaclist}')
    print (f'#  file_aac_tmp = {file_aac_tmp}')
    print (f'#  file_aac     = {file_aac}')
    print (f'#')

######################################################################

#
# fetching data
#

# fetching radiko player

command_fetch_player = f'{command_curl} {opt_curl} -o {file_player} {url_player}'

if (verbosity):
    print (f'#')
    print (f'# Now, fetching Radiko player...')
    print (f'#')
    print (f'#  COMMAND: {command_fetch_player}')
    print (f'#')

time.sleep (sleeptime)
subprocess.run (command_fetch_player, shell=True)

if (verbosity):
    print (f'#')
    print (f'# Finished fetching Radiko player!')
    print (f'#')
    print (f'#  COMMAND: {command_fetch_player}')
    print (f'#')

# scanning Radiko JS player
    
if (verbosity):
    print (f'#')
    print (f'# Now, scanning Radiko JS player...')
    print (f'#')
    
# player = new RadikoJSPlayer($audio[0], 'pc_html5', 'bcd151073c03b352e1ef2fd66c32209da9ca0afa', {
pattern_authkey \
    = re.compile ('player = new RadikoJSPlayer\(\S+,\s+\'(\S+)\',\s+\'(\S+)\',')
    
path_player = pathlib.Path (file_player)
if not ( path_player.exists () ):
    print (f'#')
    print (f'# ERROR: radiko player could not be downloaded!')
    print (f'#')
    sys.exit ()
else:
    with open (file_player, 'r') as fh:
        for line in fh:
            match_authkey = re.search (pattern_authkey, line)
            if (match_authkey):
                radiko_app     = match_authkey.group (1)
                radiko_authkey = match_authkey.group (2)

if (verbosity):
    print (f'#')
    print (f'# Following information was obtained from radiko JS player')
    print (f'#')
    print (f'#  radiko_app     = {radiko_app}')
    print (f'#  radiko_authkey = {radiko_authkey}')
    print (f'#')

# writing authkey to file
    
if (verbosity):
    print (f'#')
    print (f'# Now, writing value of authkey into a file...')
    print (f'#')

with open (file_authkey, 'w') as fh:
    fh.write (radiko_authkey)

if (verbosity):
    print (f'#')
    print (f'# Finished writing value of authkey into a file!')
    print (f'#')

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

opt_curl_auth1 = f'{opt_curl} {opt_curl_header1} {opt_curl_header2} {opt_curl_header3} {opt_curl_header4} {opt_curl_header5} {opt_curl_include}'

command_fetch_auth1 = f'{command_curl} {opt_curl_auth1} -o {file_auth1} {url_auth1}'

if (verbosity):
    print (f'#')
    print (f'# Now, fetching auth1...')
    print (f'#')
    print (f'#  COMMAND: {command_fetch_auth1}')
    print (f'#')

time.sleep (sleeptime)
subprocess.run (command_fetch_auth1, shell=True)

if (verbosity):
    print (f'#')
    print (f'# Finished fetching auth1!')
    print (f'#')
    print (f'#  COMMAND: {command_fetch_auth1}')
    print (f'#')

# scanning auth1 data
    
# X-Radiko-AuthToken: oZSYOkBPCEYafLfqPexZiA
# X-Radiko-KeyLength: 16
# X-Radiko-KeyOffset: 13
pattern_authtoken = re.compile ('X-Radiko-AuthToken:\s+(\S+)', re.IGNORECASE)
pattern_keylength = re.compile ('X-Radiko-KeyLength:\s+(\S+)', re.IGNORECASE)
pattern_keyoffset = re.compile ('X-Radiko-KeyOffset:\s+(\S+)', re.IGNORECASE)
pattern_requestid = re.compile ('x-request-id:\s+(\S+)', re.IGNORECASE)

path_auth1 = pathlib.Path (file_auth1)
if not ( path_auth1.exists () ):
    print (f'#')
    print (f'# ERROR: auth1 file could not be downloaded!')
    print (f'#')
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
            match_requestid = re.search (pattern_requestid, line)
            if (match_requestid):
                request_id = match_requestid.group (1)

if (verbosity):
    print (f'#')
    print (f'# Information extracted from auth1 file')
    print (f'#')
    print (f'#  authtoken = {authtoken}')
    print (f'#  keylength = {keylength}')
    print (f'#  keyoffset = {keyoffset}')
    print (f'#  requestid = {request_id}')
    print (f'#')

# extracting partial key

command_extract_partial_key = f'{command_dd} if={file_authkey} of={file_partialkey} bs=1 skip={keyoffset} count={keylength}'

if (verbosity):
    print (f'#')
    print (f'# Now, extracting partial key...')
    print (f'#')
    print (f'#  COMMAND: {command_extract_partial_key}')
    print (f'#')

time.sleep (sleeptime)
subprocess.run (command_extract_partial_key, shell=True)

if (verbosity):
    print (f'#')
    print (f'# Finished extracting partial key!')
    print (f'#')
    print (f'#  COMMAND: {command_extract_partial_key}')
    print (f'#')

# encoding partial key using base64

command_encode_partial_key = f'{command_base64} < {file_partialkey}'

if (verbosity):
    print (f'#')
    print (f'# Now, encoding partial key using base64...')
    print (f'#')
    print (f'#  COMMAND: {command_encode_partial_key}')
    print (f'#')

time.sleep (sleeptime)
result_encode_partial_key = subprocess.run (command_encode_partial_key, \
                                            shell=True, capture_output=True)

partialkey_value = result_encode_partial_key.stdout.decode ('utf-8')

if (verbosity):
    print (f'#')
    print (f'# Finished encoding partial key using base64!')
    print (f'#')
    print (f'#  partial key = {partialkey_value}')
    print (f'#')

# fetching auth2 data

pattern_authtoken_value  = re.compile ('___AUTHTOKEN___')
pattern_partialkey_value = re.compile ('___PARTIALKEY___')

opt_curl_header6 = re.sub (pattern_authtoken_value, authtoken, \
                           opt_curl_header6)
opt_curl_header7 = re.sub (pattern_partialkey_value, partialkey_value, \
                           opt_curl_header7)

opt_curl_auth2 = f'{opt_curl} {opt_curl_header1} {opt_curl_header2} {opt_curl_header3} {opt_curl_header4} {opt_curl_header5} {opt_curl_header6} {opt_curl_header7}'

command_fetch_auth2 = f'{command_curl} {opt_curl_auth2} -o {file_auth2} {url_auth2}'

if (verbosity):
    print (f'#')
    print (f'# Now, fetching auth2...')
    print (f'#')
    print (f'#  COMMAND: {command_fetch_auth2}')
    print (f'#')

time.sleep (sleeptime)
subprocess.run (command_fetch_auth2, shell=True)

if (verbosity):
    print (f'#')
    print (f'# Finished fetching auth2!')
    print (f'#')
    print (f'#  COMMAND: {command_fetch_auth2}')
    print (f'#')

# fetch AAC file

command_fetch_aac = f"{command_ffmpeg} {opt_ffmpeg_1} -headers 'X-Radiko-AuthToken: {authtoken}' -f hls -i '{url_playlist}?station_id={channel}&start_at={datetime_start}&ft={datetime_start}&end_at={datetime_end}&to={datetime_end}&preroll=0&l=15&lsid={request_id}&type=c' {opt_ffmpeg_2} {file_aac_tmp}"

if (verbosity):
    print (f'#')
    print (f'# Now, fetching AAC file...')
    print (f'#')
    print (f'#  COMMAND: {command_fetch_aac}')
    print (f'#')

time.sleep (sleeptime)
subprocess.run (command_fetch_aac, shell=True)

if (verbosity):
    print (f'#')
    print (f'# Finished fetching AAC file!')
    print (f'#')
    print (f'#  COMMAND: {command_fetch_aac}')
    print (f'#')

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
    print (f'#')
    print (f'# Sizes of AAC files')
    print (f'#')
    print (f'# old file: {size_old:10d} byte')
    print (f'# new file: {size_new:10d} byte')
    print (f'#')
    
if not ( ( path_aac.exists () ) and (size_old >= size_new) ):
    if (verbosity):
        print (f'#')
        print (f'# Now, copying AAC file...')
        print (f'#')
        print (f'#  {file_aac_tmp} ==> {file_aac}')
        print (f'#')
    shutil.copy2 (path_aac_tmp, path_aac)
    if (verbosity):
        print (f'#')
        print (f'# Finished copying AAC file!')
        print (f'#')

# deleting AAC files
list_aac_files = path_tmp.glob ('*.aac')
for path_aac_for_delete in list_aac_files:
    if (path_aac_for_delete.exists ()):
        path_aac_for_delete.unlink ()
