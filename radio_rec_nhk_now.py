#!/usr/pkg/bin/python3.12

#
# Time-stamp: <2024/08/16 21:28:09 (UT+8) daisuke>
#

#
# radio program recording script
#
#    version 1.0: 05/Mar/2022
#    version 1.1: 29/Jul/2022
#    version 1.2: 10/Jun/2024
#

#
# usage:
#
#    recording NHK R1 for 60 min with verbose mode
#    % radio_rec_nhk_now.py -v -c r1 -p nhknews -t 60
#

# importing argparse module
import argparse

# importing time module
import time

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

# importing shutil module
import shutil

# importing re module
import re

# date/time
datetime_now = datetime.datetime.now ()
YYYY         = datetime_now.year
MM           = datetime_now.month
DD           = datetime_now.day
hh           = datetime_now.hour
mm           = datetime_now.minute
ss           = datetime_now.second
datetime_str = "%04d%02d%02d_%02d%02d%02d" % (YYYY, MM, DD, hh, mm, ss)
date_str     = "%04d%02d%02d" % (YYYY, MM, DD)

# environmental variables
dir_home = os.environ['HOME']

# process ID
pid = os.getpid ()

#
# m3u8 addresses can be found at following web page.
#
#  https://www.nhk.or.jp/radio/config/config_web.xml
#

# list of m3u8 URLs
dic_m3u8 = {
    'r1':
    'https://radio-stream.nhk.jp/hls/live/2023229/nhkradiruakr1/master.m3u8',
    'r2':
    'https://radio-stream.nhk.jp/hls/live/2023501/nhkradiruakr2/master.m3u8',
    'fm':
    'https://radio-stream.nhk.jp/hls/live/2023507/nhkradiruakfm/master.m3u8',
}

# default parameters
list_channel      = ['r1', 'r2', 'fm']
channel_default   = 'fm'
channel_help      = "choice of channel (default: %s)" % channel_default
dir_radio_default = "%s/audio/radio" % dir_home
dir_radio_help    = "directory to store recorded file (default: %s)" \
    % dir_radio_default
dir_tmp_default   = "/tmp/radio_%s_%s" % (datetime_str, pid)
dir_tmp_help      = "directory to store temporary file (default: %s)" \
    % dir_tmp_default
ffmpeg_default    = '/usr/pkg/bin/ffmpeg6'
ffmpeg_help       = "location of ffmpeg command (default: %s)" % ffmpeg_default
program_default   = 'test'
program_help      = "radio program name (default: %s)" % program_default
duration_default  = 10
duration_help     = "time duration of recording in minute (default: %d)" \
    % duration_default
verbose_default   = 0
verbose_help      = "verbosity level (default: %d)" % verbose_default
sleep_default     = 3
sleep_help        = "sleep time after fetching stream data (default: %d sec)" \
    % sleep_default

start_default = '00:00'
start_help    = "start time of program in hh:mm format (default: %s)" \
    % start_default

# construction of parser object
desc = 'NHK radio program recording script'
parser = argparse.ArgumentParser (description=desc)

# adding arguments
parser.add_argument ('-c', '--channel', choices=list_channel, \
                     default=channel_default, help=channel_help)
parser.add_argument ('-p', '--program', default=program_default, \
                     help=program_help)
parser.add_argument ('-d', '--duration', type=int, default=duration_default, \
                     help=duration_help)
parser.add_argument ('-s', '--sleep', type=int, default=sleep_default, \
                     help=sleep_help)
parser.add_argument ('-r', '--radio-directory', default=dir_radio_default, \
                     help=dir_radio_help)
parser.add_argument ('-w', '--temporary-directory', default=dir_tmp_default, \
                     help=dir_tmp_help)
parser.add_argument ('-f', '--ffmpeg', default=ffmpeg_default, \
                     help=ffmpeg_help)
parser.add_argument ('-t', '--hhmm', default=start_default, \
                     help=start_help)
parser.add_argument ('-v', '--verbose', action='count', \
                     default=verbose_default, help=verbose_help)

# command-line argument analysis
args = parser.parse_args ()

# parameters
channel        = args.channel
program_name   = args.program
duration_min   = args.duration
sleep_sec      = args.sleep
dir_radio      = args.radio_directory
dir_tmp        = args.temporary_directory
command_ffmpeg = args.ffmpeg
start_hhmm     = args.hhmm
verbosity      = args.verbose

# time duration in second
duration_sec = duration_min * 60

# m3u8 URL
url_m3u8 = dic_m3u8[channel]

# start time hh:mm
pattern_hhmm = re.compile ('(\d+):(\d+)')
match_hhmm   = re.search (pattern_hhmm, start_hhmm)
if (match_hhmm):
    # matched patterns
    start_hh = int (match_hhmm.group (1))
    start_mm = int (match_hhmm.group (2))
    hhmm_str = "%02d%02d" % (start_hh, start_mm)
else:
    # printing message
    print (f'# something is wrong with start time "{start_hhmm}"!')
    # exit
    sys.exit ()

# file names
basename     = "%s_%s_%s" % (program_name, date_str, hhmm_str)
file_aac     = "%s/%s.aac" % (dir_radio, basename)
file_m4a_tmp = "%s/%s_tmp.m4a" % (dir_tmp, basename)
file_aac_tmp = "%s/%s_tmp.aac" % (dir_tmp, basename)

# printing input parameters
if (verbosity):
    print (f'# parameters')
    print (f'#    channel:         {channel}')
    print (f'#    m3u8 URL:        {url_m3u8}')
    print (f'#    program name:    {program_name}')
    print (f'#    time duration:   {duration_min} min')
    print (f'#    time duration:   {duration_sec} sec')
    print (f'#    sleep time       {sleep_sec} sec')
    print (f'#    radio directory: {dir_radio}')
    print (f'#    temp directory:  {dir_tmp}')
    print (f'#    ffmpeg command:  {command_ffmpeg}')
    print (f'#    tmp m4a file:    {file_m4a_tmp}')
    print (f'#    tmp aac file:    {file_aac_tmp}')
    print (f'#    output aac file: {file_aac}')

# existence check of commands
list_commands = [command_ffmpeg]
for command in list_commands:
    # making a pathlib object
    path_command = pathlib.Path (command)
    # if command does not exist, then stop the script
    if not (path_command.exists ()):
        # printing message
        print (f'The command "{command}" does not exist!')
        print (f'Install "{command}" and then run the command again.')
        # exit
        sys.exit ()

# check of time duration
if (duration_min <= 0):
    # printing message
    print (f'Something is wrong with time duration!')
    print (f'  given time duration: {duration_min} min')
    # exit
    sys.exit ()

# existence check of directories
list_dir = [dir_radio, dir_tmp]
for directory in list_dir:
    # making pathlib object
    path_dir = pathlib.Path (directory)
    # if directory does not exist
    if not (path_dir.exists ()):
        # printing message
        if (verbosity):
            print (f'# making directory "{directory}"...')
        # making directory
        path_dir.mkdir (parents=True, exist_ok=True)
        # printing message
        if (verbosity):
            print (f'# finished making directory "{directory}"!')

# command to fetch radio stream data
command_fetch = "%s -http_seekable 0 -i %s -vn -bsf:a aac_adtstoasc -acodec copy -t %ds %s" \
    % (command_ffmpeg, url_m3u8, duration_sec, file_m4a_tmp)

# printing command
if (verbosity):
    print (f'# command for fetching radio stream data')
    print (f'#    {command_fetch}')

# executing fetch command
subprocess.run (command_fetch, shell=True)

# sleeping a short time after fetching stream data
time.sleep (sleep_sec)

# existence check of fetched audio file
path_m4a_tmp = pathlib.Path (file_m4a_tmp)
if not (path_m4a_tmp.exists ()):
    # printing message
    print (f'The file "{file_m4a_tmp}" does not exist!')
    print (f'Something is wrong with fetching stream data.')
    print (f'Exiting...')
    # exit
    sys.exit ()

# command to convert audio file into AAC format
command_convert = "%s -y -i %s -acodec copy %s" \
    % (command_ffmpeg, file_m4a_tmp, file_aac_tmp)

# printing command
if (verbosity):
    print (f'# command for converting audio file format')
    print (f'#    {command_convert}')

# executing convert command
subprocess.run (command_convert, shell=True)

# sleeping a short time after fetching stream data
time.sleep (sleep_sec)

# existence check of fetched audio file
path_aac_tmp = pathlib.Path (file_aac_tmp)
if not (path_aac_tmp.exists ()):
    # printing message
    print (f'The file "{file_aac_tmp}" does not exist!')
    print (f'Something is wrong with converting data.')
    print (f'Exiting...')
    # exit
    sys.exit ()

# file size of file_aac_tmp
filesize_aac_tmp = path_aac_tmp.stat ().st_size

# file size of file_aac
path_aac = pathlib.Path (file_aac)
if (path_aac.exists ()):
    filesize_aac = path_aac.stat ().st_size
else:
    filesize_aac = 0

# printing file sizes
if (verbosity):
    print (f'# file sizes')
    print (f'#    {file_aac_tmp}: {filesize_aac_tmp} byte')
    print (f'#    {file_aac}: {filesize_aac} byte')
    
# copying AAC file
if ( (path_aac.exists ()) and (filesize_aac >= filesize_aac_tmp) ):
    # if file exists and larger than new file, then not copying file
    if (verbosity):
        print (f'# file "{file_aac_tmp}" is not copied to "{dir_radio}"')
else:
    # copying file
    shutil.copy2 (file_aac_tmp, file_aac)

# deleting AAC files
list_aac_files = path_dir.glob ('*.aac')
for path_aac_files_for_delete in list_aac_files:
    if (path_aac_files_for_delete.exists ()):
        path_aac_files_for_delete.unlink ()
    
# printing status
if (verbosity):
    print (f'# finished recording radio program!')
