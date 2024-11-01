#!/usr/pkg/bin/python3.12

#
# Time-stamp: <2024/11/01 08:50:12 (UT+8) daisuke>
#

###########################################################################

#
# importing modules
#

# importing argparse module
import argparse

# importing os module
import os

# importing sys module
import sys

# importing pathlib module
import pathlib

# importing datetime module
import datetime

# importing ssl module
import ssl

# importing urllib module
import urllib.request

# importing json module
import json

# importing re module
import re

# importing subprocess module
import subprocess

# importing random module
import random

# importing time module
import time

# importing shutil module
import shutil

# setting for SSL
ssl._create_default_https_context = ssl._create_unverified_context

###########################################################################

###########################################################################

#
# come constants and parameters
#

# URL of JSON file
url_json_nhk \
    = 'https://www.nhk.or.jp/radio-api/app/v1/web/ondemand/corners/new_arrivals'

# program names
dic_programs = {
    'adventure': '青春アドベンチャー',
    'asianview': 'Asian View',
    'culture_art': 'カルチャーラジオ　芸術その魅力',
    'culture_chinese': 'カルチャーラジオ　漢詩をよむ',
    'culture_history': 'カルチャーラジオ　歴史再発見',
    'culture_literature': 'カルチャーラジオ　文学の世界',
    'culture_science': 'カルチャーラジオ　科学と人間',
    'culture_showa': 'カルチャーラジオ　保阪正康が語る昭和人物史',
    'culture_sunday': 'カルチャーラジオ　日曜カルチャー',
    'earthradio': 'ちきゅうラジオ',
    'fmcinemasounds': 'ＦＭシネマサウンズ',
    'gendaieigo': 'ニュースで学ぶ「現代英語」',
    'genichiro': '高橋源一郎の飛ぶ教室',
    'hoshizora': 'MISIA 星空のラジオ ～Sunday Sunset～',
    'jikutabi': '音で訪ねる　ニッポン時空旅',
    'learnjapanese': 'Ｌｅａｒｎ　Ｊａｐａｎｅｓｅ　ｆｒｏｍ　ｔｈｅ　Ｎｅｗｓ',
    'meisakuza': '新日曜名作座',
    'nemurenai': '眠れない貴女へ',
    'nhkjournal': 'NHKジャーナル',
    'nhknewswebeasy': 'NHKやさしいことばニュース',
    'roudoku': '朗読',
    'roudokuworld': '朗読の世界',
    'theatre': 'ＦＭシアター',
    'weekendsunshine': 'ウィークエンドサンシャイン',
    'yamacafe': '石丸謙二郎の山カフェ',
}

# environmental variables
dir_home = os.environ['HOME']

# process ID
pid = os.getpid ()

###########################################################################

###########################################################################

#
# date/time
#

# date/time
datetime_now = datetime.datetime.now ()
YYYY         = datetime_now.year
MM           = datetime_now.month
DD           = datetime_now.day
hh           = datetime_now.hour
mm           = datetime_now.minute
ss           = datetime_now.second
date_str     = f'{YYYY:04d}{MM:02d}{DD:02d}'
time_str     = f'{hh:02d}{mm:02d}{ss:02d}'
datetime_str = f'{date_str}_{time_str}'

###########################################################################

###########################################################################

#
# command-line arguments analysis using argparse
#

# default parameters
choices_programs = list (dic_programs.keys ())
default_programs = 'adventure'
help_programs    = f'program names (default: {default_programs})'

default_useragent \
    = 'Mozilla/5.0 (X11; NetBSD amd64; rv:109.0) Gecko/20100101 Firefox/115.0'
#    = 'Mozilla/5.0 (X11; NetBSD amd64; rv:96.0) Gecko/20100101 Firefox/96.0'
help_useragent \
    = f'user agent for HTTP retrieval (default: {default_useragent})'

default_dir_radio = f'{dir_home}/audio/radio'
help_dir_radio \
    = f'directory to store recorded file (default: {default_dir_radio})'

default_dir_tmp = f'/tmp/radio_{datetime_str}_{pid}'
help_dir_tmp \
    = f'directory to store temporary file (default: {default_dir_tmp})'

default_ffmpeg = '/usr/pkg/bin/ffmpeg6'
help_ffmpeg    = f'location of ffmpeg command (default: {default_ffmpeg})'

default_sleep  = 60
help_sleep \
    = f'max sleep time between file retrieval (default: {default_sleep} sec)'

default_verbose = 0
help_verbose    = f'verbosity level (default: {default_verbose})'

# construction of parser object
desc = 'NHK on-demand radio program recording script (2024 version)'
parser = argparse.ArgumentParser (description=desc)

# adding arguments
parser.add_argument ('programs', nargs='+', choices=choices_programs, \
                     help=help_programs)
parser.add_argument ('-r', '--radio-dir', default=default_dir_radio, \
                     help=help_dir_radio)
parser.add_argument ('-t', '--temporary-dir', default=default_dir_tmp, \
                     help=help_dir_tmp)
parser.add_argument ('-u', '--user-agent', default=default_useragent, \
                     help=help_useragent)
parser.add_argument ('-f', '--ffmpeg', default=default_ffmpeg, \
                     help=help_ffmpeg)
parser.add_argument ('-s', '--sleep', default=default_sleep, \
                     help=help_sleep)
parser.add_argument ('-v', '--verbose', action='count', \
                     default=default_verbose, help=help_verbose)

# command-line argument analysis
args = parser.parse_args ()

# parameters
list_programs  = args.programs
dir_radio      = args.radio_dir
dir_tmp        = args.temporary_dir
user_agent     = args.user_agent
command_ffmpeg = args.ffmpeg
max_sleep_time = args.sleep
verbosity      = args.verbose

###########################################################################

###########################################################################

#
# files and directories
#

# files
file_json_nhk = f'{dir_tmp}/index_{datetime_str}.json'
if (verbosity):
    print (f'file_json_nhk = {file_json_nhk}')

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

###########################################################################

###########################################################################

#
# retrieving of JSON file
#

# retrieval of JSON file from NHK website
req_nhk = urllib.request.Request (url=url_json_nhk)
req_nhk.add_header ('User-Agent', user_agent)
with urllib.request.urlopen (req_nhk) as www:
    data_json_nhk = www.read ()

# decoding JSON file content
text_json_nhk = data_json_nhk.decode ('utf8')

# writing JSON data into file
with open (file_json_nhk, 'w') as fh:
    fh.write (text_json_nhk)

# decoding JSON data
dic_nhk = json.loads (text_json_nhk)

#for key in dic_nhk.keys ():
#    for i in range ( len (dic_nhk[key]) ):
#        print (f'ID = {dic_nhk[key][i]["id"]}')
#        print (f'  Channel   = {dic_nhk[key][i]["radio_broadcast"]}')
#        print (f'  Series ID = {dic_nhk[key][i]["series_site_id"]}')
#        print (f'  Corner ID = {dic_nhk[key][i]["corner_site_id"]}')

###########################################################################

###########################################################################

#
# retrieving of audio data
#

# processing each program
for program in list_programs:
    # printing status
    if (verbosity):
        print (f'Now, processing the program "{program}"...')

    # finding channel, series ID, and corner ID
    for key in dic_nhk.keys ():
        for i in range ( len (dic_nhk[key]) ):
            if (dic_nhk[key][i]["title"] == dic_programs[program]):
                channel   = dic_nhk[key][i]["radio_broadcast"]
                series_id = dic_nhk[key][i]["series_site_id"]
                corner_id = dic_nhk[key][i]["corner_site_id"]

    # printing channel, series ID, and cornder ID
    if (verbosity):
        print (f'  Channel   = {channel}')
        print (f'  Series ID = {series_id}')
        print (f'  Corner ID = {corner_id}')
    
    # url of JSON file for given program
    url_json_program \
        = f'https://www.nhk.or.jp/radio-api/app/v1/web/ondemand/series' \
        + f'?site_id={series_id}&corner_site_id={corner_id}'

    # printing status
    if (verbosity):
        print (f'  Now, fetching JSON file...')
        print (f'  {url_json_program}')
    
    # fetching JSON file for the program
    req_program = urllib.request.Request (url=url_json_program)
    req_program.add_header ('User-Agent', user_agent)
    with urllib.request.urlopen (req_program) as www:
        data_json_program = www.read ()

    # printing status
    if (verbosity):
        print (f'  Finished fetching JSON file!')

    # decoding JSON file content
    text_json_program = data_json_program.decode ('utf8')

    # name for JSON file
    file_json_program = f'{dir_tmp}/{series_id}_{corner_id}.json'
    
    # writing JSON file into file
    with open (file_json_program, 'w') as fh:
        fh.write (text_json_program)

    # decoding JSON data
    dic_program = json.loads (text_json_program)
    
    #print (f'{dic_program["episodes"][0]["stream_url"]}')

    # retrieving audio data
    for i in range ( len (dic_program["episodes"]) ):
        # URL of m3u8
        url_m3u8 = dic_program["episodes"][i]["stream_url"]
        # onair date
        contents_id = dic_program["episodes"][i]["aa_contents_id"]
        
        # pattern matching of date/time of start of program
        pattern_datetime \
            = re.compile (r'(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\+09:00_') 
        match_datetime = re.search (pattern_datetime, contents_id)
        if (match_datetime):
            start_YYYY = int (match_datetime.group (1))
            start_MM   = int (match_datetime.group (2))
            start_DD   = int (match_datetime.group (3))
            start_hh   = int (match_datetime.group (4))
            start_mm   = int (match_datetime.group (5))
            start_ss   = int (match_datetime.group (6))
        else:
            if (verbosity):
                print (f'WARNING: pattern matching failed!')
            continue

        # file names
        start_date     = f'{start_YYYY:04d}{start_MM:02d}{start_DD:02d}'
        start_time     = f'{start_hh:02d}{start_mm:02d}'
        start_datetime = f'{start_date}_{start_time}'
        file_aac_tmp   = f'{dir_tmp}/{program}_{start_datetime}.aac'
        file_aac       = f'{dir_radio}/{program}_{start_datetime}.aac'

        # sleeping for a short time
        sleep_time = random.randint (5, max_sleep_time)
        time.sleep (sleep_time)
            
        # command for fetching audio stream using ffmpeg command
        command_fetch = f'{command_ffmpeg} -http_seekable 0 -n' \
            + f' -i {url_m3u8} -vn -acodec aac {file_aac_tmp}'
        if (verbosity):
            print (f'#    {command_fetch}')
        subprocess.run (command_fetch, shell=True)

        # existence check of fetched audio file
        path_aac_tmp = pathlib.Path (file_aac_tmp)
        if not (path_aac_tmp.exists ()):
            # printing message
            print (f'The file "{file_aac_tmp}" does not exist!')
            print (f'Something is wrong with retrieval of data.')
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
            print (f'#    file sizes')
            print (f'#      {file_aac_tmp}: {filesize_aac_tmp} byte')
            print (f'#      {file_aac}: {filesize_aac} byte')
    
        # copying AAC file
        if ( (path_aac.exists ()) and (filesize_aac >= filesize_aac_tmp) ):
            # if file exists and larger than new file, then not copying file
            if (verbosity):
                print (f'#    file "{file_aac_tmp}" is not copied to {dir_radio}')
        else:
            if (verbosity):
                print (f'#    copy: {file_aac_tmp} ==> {file_aac}')
            # copying file
            shutil.copy2 (file_aac_tmp, file_aac)
            if (verbosity):
                print (f'#    file copy finished')

        # deleting AAC files
        list_aac_files = path_dir.glob ('*.aac')
        for path_aac_files_for_delete in list_aac_files:
            if (path_aac_files_for_delete.exists ()):
                path_aac_files_for_delete.unlink ()

###########################################################################
