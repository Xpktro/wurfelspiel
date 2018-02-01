# Musikalisches Würfelspiel Bot

This is an implementation of the Musikalisches Würfelspiel (K516f) musical game presumably made by W.A. Mozart. This script is originally intended for running periodically and tweet the songs it generates in [it's own twitter account (@wurfelspielbot)](https://twitter.com/wurfelspielbot). However, the code is organized in a way that can be used for any other purposes that involve generating the sheet music, audio and/or video for such pieces.

This works by having a lilypond master template (`score.ly`) which contains all of the measures from K516f. The wurfelspiel.py script parses this template and implements the rules for generating a new variation based on the original 16-measure tables in the form of a new lilypond score file; such score renders to a PNG image and a MIDI file. By using TiMidity++ and a beautiful 1729 Harpsichord soundfont (which had to be edited to have it set for the first bank and patch with Polyphone and thus included in this project) a PCM waveform is also rendered and both the image and sound are converted into a video using FFmpeg.

Finally, the script includes logic for posting the resulting video (generated using a random variation from all the 45949729863572161 possible ones) to a twitter account.

# Requirements
* Python 3 (latest versions should include pip)
* [Lilypond](http://lilypond.org/)
* [TiMidity++](http://timidity.sourceforge.net/)
* [FFmpeg](https://www.ffmpeg.org/)
* [Soni Musicae Blanchet 1729 Soundfount (included)](http://sonimusicae.free.fr/blanchet1-en.html)
* [Polyphone Soundfont Editor (optional, see above)](http://polyphone-soundfonts.com/)

# Installation

* Clone this repository somewhere you have write permissions.
* Download the soundfont file using [Git LFS](https://git-lfs.github.com/)
* Install this project dependencies following the links provided in requirements. Remember the Soundfont editor is not mandatory since an adequate soundfont is already included. Order is not relevant.
* Install Python dependencies by running:
```
pip install -r requirements.txt
```
* Edit TiMidity++ configuration file `timidity.cfg`. Location depends on your OS but can be `/usr/local/Cellar/timidity/x.x.x/share/timidity/timidity.cfg` on OSX (installed using brew) or `/etc/timidity/timidity.cfg` on linuxes. Replace the contents of such file with the following (unless you know what you're doing) and set you project path accordingly:
```
opt -s 44100
opt -f
opt -EFresamp=L
opt -EFreverb=40,65
opt -EFns=0
opt -m 3500
opt -p 256
opt -EFchorus=2

dir /path/to/wulfespiel/

bank 0
  0 %font Blanchet-1720.sf2  0  0
```
* For using Twitter functionality you must:
    - Go to https://apps.twitter.com/ and create a new application. You'll get a consumer key and secret.
    - Copy `.env.example` and rename it to `.env` and paste the key and secret obtained from the former step. Don't fill `TWITTER_AUTH_TOKEN` nor `TWITTER_AUTH_SECRET`.

# Usage
By default, running the script directly will generate and upload a random variation to Twitter. (You'll be asked to perform an authorization step with Twitter for the first time):
```
python wurfelspiel.py
```

Check the last lines of `wurfelspiel.py` if you want to change this behavior. A sequential generation scenario has also been implemented and can be checked in the `get_parts(number)` function.

If you want to use this script for your own project, you may want to use the `generate_song(parts, number)` and `generate_score(parts, score)` functions.

# License
Copyright 2018 Moisés Cachay

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
