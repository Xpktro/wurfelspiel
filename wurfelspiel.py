# coding:utf-8
# Copyright 2018 Moisés Cachay
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import random
import re
import subprocess

from dotenv import find_dotenv, load_dotenv, set_key
from twython import Twython

LILYPOND_EXECUTABLE = '/Users/moises/bin/lilypond'
TIMIDITY_EXECUTABLE = '/usr/local/bin/timidity'
FFMPEG_EXECUTABLE = '/usr/local/bin/ffmpeg'


def path(filename):
    return os.path.join(os.path.dirname(__file__), filename)


def get_notes(part):
    return map(lambda i: (i[0], i[-1]),
               re.findall(r'\s+% (\d+(\.\d)?)\s*(.*)', part))


def parse_score(score):
    (header, first_separator, upper, second_separator, lower,
     third_separator, footer) = re.split(
        r'(.*clef treble\n|'
        r'\s*}\n\s*\\new Staff = "down" {\n\s*\\clef bass\n|'
        r'\s*}\n\s*>>.*)',
        score
    )

    notes = {
        number: (upper_notes, lower_notes,)
        for (number, upper_notes,), (_, lower_notes,)
        in zip(get_notes(upper), get_notes(lower))
    }

    spacer = re.findall(r'( +)\\clef', score)[0]

    return (header, first_separator, second_separator, third_separator,
            footer, spacer, notes)


def get_first_half_fragment(measure, part):
    return (
        ('096', '022', '141', '041', '105', '122', '011', '030',),
        ('032', '006', '128', '063', '146', '046', '134', '081',),
        ('069', '095', '158', '013', '153', '055', '110', '024',),
        ('040', '017', '113', '085', '161', '002', '159', '100',),
        ('148', '074', '163', '045', '080', '097', '036', '107',),
        ('104', '157', '027', '167', '154', '068', '118', '091',),
        ('152', '060', '171', '053', '099', '133', '021', '127',),
        ('119', '084', '114', '050', '140', '086', '169', '094',),
        ('098', '142', '042', '156', '075', '129', '062', '123',),
        ('003', '087', '165', '061', '135', '047', '147', '033',),
        ('054', '130', '010', '103', '028', '037', '106', '005',),
    )[part][measure]


def get_second_half_fragment(measure, part):
    return (
        ('070', '121', '026', '009', '112', '049', '109', '014',),
        ('117', '039', '126', '056', '174', '018', '116', '083',),
        ('066', '139', '015', '132', '073', '058', '145', '079',),
        ('090', '176', '007', '034', '067', '160', '052', '170',),
        ('025', '143', '064', '125', '076', '136', '001', '093',),
        ('138', '071', '150', '029', '101', '162', '023', '151',),
        ('016', '155', '057', '175', '043', '168', '089', '172',),
        ('120', '088', '048', '166', '051', '115', '072', '111',),
        ('065', '077', '019', '082', '137', '038', '149', '008',),
        ('102', '004', '031', '164', '144', '059', '173', '078',),
        ('035', '020', '108', '092', '012', '124', '044', '131',),
    )[part][measure]


def get_factors(n):
    if n < 11:
        return [n]
    else:
        return [n % 11] + get_factors(n // 11)


def get_parts(number=None):
    if number is None:
        if not os.path.exists('.current'):
            open('.current', 'w').close()

        with open('.current', 'r+') as f:
            number = int(f.read().strip() or 0)
            f.seek(0)
            f.write(str(number + 1))
            f.truncate()
    factors = get_factors(number)

    if len(factors) > 16:
        factors = factors[:16]
    else:
        factors = factors + [0] * (16 - len(factors))

    return number, factors


def update_header(header, number, parts):
    return header.replace(
        '#id#',
        '{}: {}'.format(number + 1, ', '.join(map(lambda p: str(p + 1), parts)))
    )


def generate_part(first_half, repeat_notes, second_half, half, spacer):
    return \
        '{}\\repeat volta 2 {{\n{}'.format(spacer, spacer) + \
        '\n{}'.format(spacer).join(map(lambda note: note[half], first_half)) + \
        '}}\n{}'.format(spacer) + \
        '\\alternative {{\n{}'.format(spacer) + \
        '    {{ {} | }}'.format(repeat_notes[0][half]) + \
        '\n{}'.format(spacer) + \
        '    {{ {} | }}'.format(repeat_notes[1][half]) + \
        '\n{}'.format(spacer) + \
        '}}'.format(spacer) + \
        '\n{}{}'.format(spacer, '| \mark "Trio"') + \
        '\n{}'.format(spacer) + \
        '\n{}'.format(spacer).join(map(lambda note: note[half], second_half)) + \
        '\n{}\\bar "|."'.format(spacer)


def generate_score(parts=None, number=None):
    if not parts:
        number, parts = get_parts(number)

    with open(path('score.ly'), encoding='utf-8') as s:
        score = s.read()

    (header, first_separator, second_separator, third_separator,
     footer, spacer, first_half) = parse_score(score)

    first_half_notes = list(map(
        lambda part: first_half[get_first_half_fragment(*part)],
        enumerate(parts[:7])
    ))

    repeat_notes = [
        first_half['{}.1'.format(get_first_half_fragment(7, parts[7]))],
        first_half['{}.2'.format(get_first_half_fragment(7, parts[7]))],
    ]

    second_half_notes = list(map(
        lambda part: first_half[get_second_half_fragment(*part)],
        enumerate(parts[8:])
    ))

    generated_score = \
        update_header(header, number, parts) + \
        first_separator + \
        generate_part(first_half_notes, repeat_notes, second_half_notes, 0, spacer) + \
        second_separator + \
        generate_part(first_half_notes, repeat_notes, second_half_notes, 1, spacer) + \
        third_separator + footer

    return generated_score, parts, number


def generate_song(parts=None, number=None):
    score, parts, number = generate_score(parts=parts, number=number)
    subprocess.run(
        [LILYPOND_EXECUTABLE,
         '--png',
         '--output={}'.format(path('out')),
         '-dresolution=175',
         '-'],
        input=score.encode()
    )

    subprocess.run([
        TIMIDITY_EXECUTABLE,
        path('out.midi'),
        '-Ow',
        '-o', path('out.wav')
    ])

    subprocess.run([
        FFMPEG_EXECUTABLE,
        '-y',
        '-loop', '1',
        '-i', path('out.png'),
        '-i', path('out.wav'),
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-pix_fmt', 'yuv420p',
        '-strict', '-2',
        '-shortest',
        '-vf', r'transpose=1,scale=-2:min(1080\,if(mod(ih\,2)\,ih-1\,ih))',
        path('out.mp4')
    ])

    return parts, number


def tweet_generated_song(parts, number):
    load_dotenv(find_dotenv())
    if not (os.environ.get('TWITTER_AUTH_TOKEN')
            or os.environ.get('TWITTER_AUTH_SECRET')):
        twitter = Twython(os.environ.get('TWITTER_CONSUMER_KEY'),
                          os.environ.get('TWITTER_CONSUMER_SECRET'))
        auth = twitter.get_authentication_tokens()
        verifier = input(
            'Please visit {} for authorizing your twitter and type the '
            'verification code here: '.format(auth['auth_url'])
        )
        twitter = Twython(os.environ.get('TWITTER_CONSUMER_KEY'),
                          os.environ.get('TWITTER_CONSUMER_SECRET'),
                          auth['oauth_token'], auth['oauth_token_secret'])
        final_step = twitter.get_authorized_tokens(verifier)
        set_key(find_dotenv(), 'TWITTER_AUTH_TOKEN', final_step['oauth_token'])
        set_key(find_dotenv(), 'TWITTER_AUTH_SECRET', final_step['oauth_token_secret'])
        load_dotenv(find_dotenv())

    twitter = Twython(os.environ.get('TWITTER_CONSUMER_KEY'),
                      os.environ.get('TWITTER_CONSUMER_SECRET'),
                      os.environ.get('TWITTER_AUTH_TOKEN'),
                      os.environ.get('TWITTER_AUTH_SECRET'))

    with open(path('out.mp4'), 'rb') as video:
        response = twitter.upload_video(
            media=video,
            media_type='video/mp4',
            media_category='tweet_video',
            check_progress=True
        )
        twitter.update_status(
            status=update_header('Musikalisches Würfelspiel (K516f) No. #id#', number, parts),
            media_ids=[response['media_id_string']]
        )


if __name__ == '__main__':
    parts, number = generate_song(
        number=random.randint(0, (11**16) - 1)
    )
    tweet_generated_song(parts, number)

