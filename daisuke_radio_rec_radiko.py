#!/usr/bin/env python3

#
# Time-stamp: <2026/02/04 21:10:24 (UT+08:00) daisuke>
#

############################################################################
#                                                                          #
# Radiko recording program                                                 #
#                                                                          #
#  author: Kinsohita Daisuke                                               #
#                                                                          #
############################################################################

############################################################################

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

# importing urllib module
import urllib.request

# importing re module
import re

# importing base64 module
import base64

# importing subprocess module
import subprocess

############################################################################

#
# Constants
#

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

# URLs
url_player   = f'https://radiko.jp/apps/js/playerCommon.js'
url_auth1    = f'https://radiko.jp/v2/api/auth1'
url_auth2    = f'https://radiko.jp/v2/api/auth2?radiko_session='
url_playlist = f'https://tf-f-rpaa-radiko.smartstream.ne.jp/tf/playlist.m3u8'

############################################################################

#
# Command-line arguments analysis
#

# initialising a parser object
descr  = f'recording Radiko radio programs'
parser = argparse.ArgumentParser (description=descr)

# default values
default_channel    = f'FMT'
default_program    = f'lifestylemuseum'
default_dayofweek  = f'Fri'
default_starttime  = f'18:30'
default_endtime    = f'19:00'
default_verbose    = 0
default_sleeptime  = 1
default_timezone   = +9.0
default_useragent  = f'Mozilla/5.0 (X11; NetBSD x86_64; rv:140.0) Gecko/20100101 Firefox/140.0'
default_streamtype = f'b'
default_ffmpeg     = f'/usr/pkg/bin/ffmpeg'

# help messages
help_channel    = f'radio channel code (default: FMT)'
help_program    = f'radio program name (default: lifestylemuseum)'
help_dayofweek  = f'day-of-week of program (default: Fri)'
help_starttime  = f'start time (JST) of program in HH:MM format (default: 18:30)'
help_endtime    = f'end time (JST) of program in HH:MM format (default: 19:00)'
help_verbose    = f'versobity level (default: 0)'
help_sleeptime  = f'sleep time before executing shell command (default: 1)'
help_timezone   = f'timezone (default: +9.0)'
help_useragent  = f'user agent name (default: Mozilla/5.0)'
help_streamtype = f'radiko stream type (b or c) (default: b)'
help_ffmpeg     = f'ffmpeg command (default: /usr/pkg/bin/ffmpeg)'

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
parser.add_argument ('-u', '--useragent', \
                     default=default_useragent, \
                     help=help_useragent)
parser.add_argument ('-t', '--streamtype', \
                     default=default_streamtype, \
                     help=help_streamtype)
parser.add_argument ('-f', '--ffmpeg', \
                     default=default_ffmpeg, \
                     help=help_ffmpeg)
parser.add_argument ('-v', '--verbose', action='count', \
                     default=default_verbose, \
                     help=help_verbose)

# parsing arguments
args = parser.parse_args ()

# input parameters
channel        = args.channel
program        = args.program
dayofweek      = args.dayofweek
time_start     = args.start
time_end       = args.end
sleeptime      = args.sleeptime
timezone       = args.timezone
user_agent     = args.useragent
stream_type    = args.streamtype
verbosity      = args.verbose
command_ffmpeg = args.ffmpeg


############################################################################

#
# Functions
#

# function to calculate MJD from given calendar date
def cal2mjd (year, month, day):
    if (month < 3):
        year  -= 1
        month += 12
    mjd = int (365.25 * (year + 4716) ) + int (30.6001 * (month + 1) ) + day \
        + ( 2 - int (year / 100) + int ( int (year / 100) / 4 ) ) \
        - 2401525.0
    return (mjd)

# function to calculate calendar date from given MJD
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

# function to print input parameters
def print_input_parameters ():
    # status parameter
    status = 0
    
    # printing input parameters
    print (f'#')
    print (f'# Input parameters')
    print (f'#')
    print (f'#  channel     = "{channel}"')
    print (f'#  program     = "{program}"')
    print (f'#  dayofweek   = "{dayofweek}"')
    print (f'#  time_start  = "{time_start}"')
    print (f'#  time_end    = "{time_end}"')
    print (f'#  sleeptime   = "{sleeptime}"')
    print (f'#  timezone    = "{timezone}"')
    print (f'#  user_agent  = "{user_agent}"')
    print (f'#  stream_type = "{stream_type}"')
    print (f'#  verbosity   = "{verbosity}"')
    print (f'#')

    # returning status parameter
    return (status)

# function to get current date and time
def get_datetime ():
    # getting current date/time in UTC
    datetime_now = datetime.datetime.now (datetime.timezone.utc)

    # year, month, day, hour, minute, and second
    YYYY = datetime_now.year
    MM   = datetime_now.month
    DD   = datetime_now.day
    hh   = datetime_now.hour
    mm   = datetime_now.minute
    ss   = datetime_now.second + datetime_now.microsecond * 10**-6

    # fractional day
    fday = hh / 24.0 + mm / 1440.0 + ss / 86400.0 + timezone / 24.0
    if (fday > 1.0):
        fday -= 1.0

    # calculation of MJD
    mjd_ut0 = cal2mjd (YYYY, MM, DD)
    mjd_now = mjd_ut0 + fday
    mjd_lt  = mjd_now + timezone / 24.0

    # day of week
    dayofweek_now = (int (mjd_lt) + 3) % 7

    # date and time in string format (Midterms)
    datetime_str  = f'{YYYY:04d}{MM:02d}{DD:02d}T{hh:02d}{mm:02d}{int (ss):02d}'

    # start and end time
    (time_start_hh, time_start_mm) = time_start.split (':')
    (time_end_hh, time_end_mm)     = time_end.split (':')

    # fractional day of start and end time
    start_fday = int (time_start_hh) / 24.0 + int (time_start_mm) / 1440.0
    end_fday   = int (time_end_hh) / 24.0 + int (time_end_mm) / 1440.0

    # length of radio program in day
    if (start_fday < end_fday):
        program_length_day = end_fday - start_fday
    else:
        program_length_day = end_fday - start_fday + 1.0

    # recording today's program or recording a program a week ago
    if ( (dow2num[dayofweek] == dayofweek_now) and (fday < end_fday) ):
        target_day_offset = -7
    else:
        target_day_offset = 0

    # getting starting year, month, and day
    start_mjd = int (mjd_lt + target_day_offset)
    (start_YYYY, start_MM, start_DD) = mjd2cal (start_mjd)

    # getting ending year, month, and days
    if (start_fday < end_fday):
        end_mjd = start_mjd
    else:
        end_mjd = start_mjd + 1
    (end_YYYY, end_MM, end_DD) = mjd2cal (end_mjd)

    # start and end date/time
    start_date_str = f'{start_YYYY:04d}{start_MM:02d}{int (start_DD):02d}'
    start_hhmm_str = f'{int (time_start_hh):02d}{int (time_start_mm):02d}'
    end_date_str   = f'{end_YYYY:04d}{end_MM:02d}{int (end_DD):02d}'
    end_hhmm_str   = f'{int (time_end_hh):02d}{int (time_end_mm):02d}'
    datetime_start = f'{start_date_str}{start_hhmm_str}'
    datetime_end   = f'{end_date_str}{end_hhmm_str}'

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

    # returning datetime_start and datetime_end
    return (datetime_str, datetime_start, datetime_end, start_date_str, start_hhmm_str)

def make_files_and_directories ():
    # process ID
    pid = os.getpid ()

    # directories
    dir_home = os.environ['HOME']
    dir_data = f'{dir_home}/audio/radio'
    dir_tmp  = f'/tmp/radiko_{datetime_str}_{pid:06d}'

    # making directories 'dir_data' and 'dir_tmp' if not exist
    path_data = pathlib.Path (dir_data)
    if not ( path_data.exists () ):
        path_data.mkdir (parents=True, exist_ok=True)
    path_tmp = pathlib.Path (dir_tmp)
    if not ( path_tmp.exists () ):
        path_tmp.mkdir (parents=True, exist_ok=True)

    # files
    file_player     = f'{dir_tmp}/radiko_player.js'
    file_authkey    = f'{dir_tmp}/radiko_authkey.data'
    file_auth1      = f'{dir_tmp}/radiko_auth1.data'
    file_auth2      = f'{dir_tmp}/radiko_auth2.data'
    file_partialkey = f'{dir_tmp}/radiko_partialkey.data'
    file_playlist   = f'{dir_tmp}/radiko_playlist.data'
    file_m3u        = f'{dir_tmp}/{program}_{start_date_str}_{start_hhmm_str}.m3u'
    file_aaclist    = f'{dir_tmp}/aac.list'
    file_aac_tmp    = f'{dir_tmp}/{program}_{start_date_str}_{start_hhmm_str}.aac'
    file_aac        = f'{dir_data}/{program}_{start_date_str}_{start_hhmm_str}.aac'

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
    
    # returning values
    return (file_player, file_authkey, file_auth1, file_auth2, file_partialkey, \
            file_playlist, file_m3u, file_aaclist, file_aac_tmp, file_aac)

# fetching radiko player
def fetch_radiko_player (url_player, file_player):
    # creating urllib request object
    req = urllib.request.Request (url_player)
    # adding header
    req.add_header ('User-Agent', user_agent)
    # downloading radiko player
    with urllib.request.urlopen (req) as www_player:
        data_player = www_player.read ()
    # writing data into file
    with open (file_player, 'w') as fh_out:
        fh_out.write (data_player.decode ('utf-8'))
    # existing check of downloaded radiko player
    path_player = pathlib.Path (file_player)
    if not ( (path_player.exists ()) and (path_player.stat ().st_size > 0) ):
        # printing a message
        print (f'ERROR:')
        print (f'ERROR: failed to download Radiko player!')
        print (f'ERROR:')
        # stopping the script
        sys.exit (0)
    # returning value
    return (0)

# finding authkey from radiko player
def find_authkey (file_player):
    # regular expression pattern
    pattern_authkey = re.compile ('player = new RadikoJSPlayer\(\S+,\s+\'(\S+)\',\s+\'(\S+)\',')
    # opening radiko player
    with open (file_player, 'r') as fh_in:
        # reading radiko player line-by-line
        for line in fh_in:
            # pattern matching
            match_authkey = re.search (pattern_authkey, line)
            # extracting authkey
            if (match_authkey):
                radiko_app     = match_authkey.group (1)
                radiko_authkey = match_authkey.group (2)
    # printing authkey
    if (verbosity):
        print (f'#')
        print (f'# Following information was obtained from radiko JS player')
        print (f'#')
        print (f'#  radiko_app     = {radiko_app}')
        print (f'#  radiko_authkey = {radiko_authkey}')
        print (f'#')

    # returning value
    return (radiko_app, radiko_authkey)

# function to write radiko authkey into file
def write_authkey (file_authkey, radiko_authkey):
    # opening file for writing
    with open (file_authkey, 'w') as fh_out:
        # writing authkey into file
        fh_out.write (f'{radiko_authkey}\n')
    # returning value
    return (0)

# function to download radiko auth1
def fetch_radiko_auth1 (url_auth1, file_auth1):
    # creating urllib request object
    req = urllib.request.Request (url_auth1)
    # adding header
    req.add_header ('User-Agent', user_agent)
    req.add_header ('pragma', f'no-cache')
    req.add_header ('X-Radiko-App', f'{radiko_app}')
    req.add_header ('X-Radiko-App-Version', f'0.0.1')
    req.add_header ('X-Radiko-User', f'dummy_user')
    req.add_header ('X-Radiko-Device', f'pc')
    # downloading radiko auth1
    with urllib.request.urlopen (req) as www_auth1:
        data_auth1 = www_auth1.read ()
        header_auth1 = www_auth1.headers
    # writing auth1 into file
    with open (file_auth1, 'w') as fh_out:
        fh_out.write (str (header_auth1))
    # making patterns for regular expression
    pattern_requestid = re.compile ('x-request-id:\s+(\S+)', re.IGNORECASE)
    pattern_authtoken = re.compile ('x-radiko-authtoken:\s+(\S+)', re.IGNORECASE)
    pattern_keylength = re.compile ('x-radiko-keylength:\s+(\S+)', re.IGNORECASE)
    pattern_keyoffset = re.compile ('x-radiko-keyoffset:\s+(\S+)', re.IGNORECASE)
    # find request ID, auth token, key length, and key offset
    match_requestid = re.search (pattern_requestid, str (header_auth1))
    match_authtoken = re.search (pattern_authtoken, str (header_auth1))
    match_keylength = re.search (pattern_keylength, str (header_auth1))
    match_keyoffset = re.search (pattern_keyoffset, str (header_auth1))
    if (match_requestid):
        request_id = match_requestid.group (1)
    if (match_authtoken):
        authtoken = match_authtoken.group (1)
    if (match_keylength):
        keylength = match_keylength.group (1)
    if (match_keyoffset):
        keyoffset = match_keyoffset.group (1)
    # printing obtained values
    if (verbosity):
        print (f'#')
        print (f'# Information extracted from auth1 file')
        print (f'#')
        print (f'#  authtoken = {authtoken}')
        print (f'#  keylength = {keylength}')
        print (f'#  keyoffset = {keyoffset}')
        print (f'#  requestid = {request_id}')
        print (f'#')
    # returning values
    return (request_id, authtoken, keylength, keyoffset)

# function to extract partial key
def extract_partial_key (radiko_authkey, keylength, keyoffset):
    key_start   = keyoffset
    key_end     = keyoffset + keylength
    partial_key = radiko_authkey[key_start:key_end].encode ()
    partial_key_encoded = base64.b64encode (partial_key).decode ('ascii')
    # writing partial key into file
    with open (file_partialkey, 'w') as fh_out:
        fh_out.write (f'{partial_key_encoded}\n')
    if (verbosity):
        print (f'#')
        print (f'# Finished encoding partial key using base64!')
        print (f'#')
        print (f'#  partial key = {partial_key}')
        print (f'#  partial key = {partial_key_encoded}')
        print (f'#')
    # returning value
    return (partial_key, partial_key_encoded)

# function to fetch radiko auth2
def fetch_radiko_auth2 (url_auth2, file_auth2, authtoken, partial_key_encoded):
    # creating urllib request object
    req = urllib.request.Request (url_auth2)
    # adding header
    req.add_header ('User-Agent', user_agent)
    req.add_header ('pragma', f'no-cache')
    req.add_header ('X-Radiko-App', f'{radiko_app}')
    req.add_header ('X-Radiko-App-Version', f'0.0.1')
    req.add_header ('X-Radiko-User', f'dummy_user')
    req.add_header ('X-Radiko-Device', f'pc')
    req.add_header ('X-Radiko-AuthToken', f'{authtoken}')
    req.add_header ('X-Radiko-PartialKey', f'{partial_key_encoded}')
    # downloading radiko auth2
    with urllib.request.urlopen (req) as www_auth2:
        data_auth2   = www_auth2.read ()
        header_auth2 = www_auth2.headers
    # writing auth1 into file
    with open (file_auth2, 'w') as fh_out:
        fh_out.write (str (header_auth2))
        fh_out.write (data_auth2.decode ('utf-8'))
    # returning value
    return (0)

# function to fetch m3u file
def fetch_radiko_m3u (url_playlist, channel, datetime_start, datetime_end, \
                      authtoken, request_id, stream_type, file_aac_tmp):
    # URL of playlist
    url_m3u8 = f'{url_playlist}?station_id={channel}&start_at={datetime_start}&ft={datetime_start}&end_at={datetime_end}&to={datetime_end}&preroll=0&l=15&lsid={request_id}&type={stream_type}'
    # options for ffmpeg command
    opt_ffmpeg_1 = f"-http_seekable 0 -seekable 0"
    opt_ffmpeg_2 = f"-headers 'User-Agent: {user_agent}'"
    opt_ffmpeg_3 = f'-acodec copy -bsf:a aac_adtstoasc'
    # command to fetch AAC file
    command_fetch_aac = f"{command_ffmpeg} {opt_ffmpeg_1} {opt_ffmpeg_2} -headers 'X-Radiko-AuthToken: {authtoken}' -f hls -i '{url_m3u8}' {opt_ffmpeg_3} {file_aac_tmp}"
    # executing ffmpeg command to fetch AAC file
    subprocess.run (command_fetch_aac, shell=True)
    # returning value
    return (0)
    
# function to copy AAC file
def copy_aac_file (file_aac_tmp, file_aac):
    # making pathlib objects
    path_aac_tmp = pathlib.Path (file_aac_tmp)
    path_aac     = pathlib.Path (file_aac)

    # checking file size of file_aac_tmp
    if not ( path_aac.exists () ):
        size_old = 0
    else:
        size_old = path_aac.stat ().st_size

    # checking file size of file_aac
    if not ( path_aac_tmp.exists () ):
        size_new = 0
    else:
        size_new = path_aac_tmp.stat ().st_size

    # printing information
    if (verbosity):
        print (f'#')
        print (f'# Sizes of AAC files')
        print (f'#')
        print (f'# old file: {size_old:10d} byte')
        print (f'# new file: {size_new:10d} byte')
        print (f'#')

    # copying file if file_aac_tmp is larger than file_aac
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

    # returning value
    return (0)

############################################################################

# printing input parameters
if (verbosity):
    print_input_parameters ()

# finding date and time of start and end of radio program
(datetime_str, datetime_start, datetime_end, start_date_str, start_hhmm_str) \
    = get_datetime ()

# getting file names
(file_player, file_authkey, file_auth1, file_auth2, file_partialkey, \
            file_playlist, file_m3u, file_aaclist, file_aac_tmp, file_aac) \
            = make_files_and_directories ()

# downloading radiko player
fetch_radiko_player (url_player, file_player)

# extracting authkey
(radiko_app, radiko_authkey) = find_authkey (file_player)

# writing authkey into file
write_authkey (file_authkey, radiko_authkey)

# downloading radiko auth1
(request_id, authtoken, keylength, keyoffset) \
    = fetch_radiko_auth1 (url_auth1, file_auth1)

# extracting radiko partial key
(partial_key, partial_key_encoded) = extract_partial_key (radiko_authkey, \
                                                          int (keylength), \
                                                          int (keyoffset))
# downloading radiko auth2
fetch_radiko_auth2 (url_auth2, file_auth2, authtoken, partial_key_encoded)

# downloading m3u file
fetch_radiko_m3u (url_playlist, channel, datetime_start, datetime_end, \
                  authtoken, request_id, stream_type, file_aac_tmp)

# copying and deleting AAC file
copy_aac_file (file_aac_tmp, file_aac)
