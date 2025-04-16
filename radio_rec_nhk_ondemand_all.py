#!/usr/pkg/bin/python3.12

# Time-stamp: <2025/04/16 22:04:59 (UT+08:00) daisuke>

# importing random module
import random

# importing subprocess module
import subprocess

# command for ondemand
command_ondemand = '/home/daisuke/bin/radio_rec_nhk_ondemand.py'

# program names
dic_programs = {
    'adventure': '青春アドベンチャー',
    'announcer100yr': 'アナウンサー百年百話',
    'asianview': 'Asian View',
    'broadcast100yr': '放送100年 保阪正康が語る昭和人物史',
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
    'kotenkyoshitsu': 'おしゃべりな古典教室',
    'ohanashi': 'お話でてこい',
    'oretachi': '弘兼憲史の“俺たちはどう生きるか”',
    'oto': '音の風景',
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

# list of programs
list_programs = list (dic_programs.keys ())

# retrieving audio data
while ( len (list_programs) > 0 ):
    n = len (list_programs)
    i = random.randint (0, n - 1)
    command_fetch = f'{command_ondemand} {list_programs[i]}'
    print (f'{command_fetch}')
    subprocess.run (command_fetch, shell=True)
    list_programs.pop (i)
