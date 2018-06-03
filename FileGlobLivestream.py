#!/usr/bin/env python
"""
LIVE STREAM using FFMPEG -- Globbed input file list

NOTE: most video streaming sites REQUIRE you have to a video feed,
     so try the `-image` option with a favorite .JPG or whatever.

https://www.scivision.co/youtube-live-ffmpeg-livestream/
https://support.google.com/youtube/answer/2853702
"""
from pathlib import Path
from typing import List, Union
import PyLivestream as pls
import random
try:
    from tinytag import TinyTag
except ImportError:
    TinyTag = None


def playonce(flist: List[Path], image: Path, site: str, inifn: Path,
             shuffle: bool, usemeta: bool, yes: bool):

    if shuffle:
        random.shuffle(flist)

    caption: Union[str, None]

    for f in flist:
        if usemeta and TinyTag:
            try:
                caption = pls.utils.meta_caption(TinyTag.get(str(f)))
                print(caption)
            except LookupError:
                caption = None
        else:
            caption = None

        s = pls.FileIn(inifn, site, infn=f, loop=False, image=image,
                       caption=caption, yes=yes)

        s.golive()


if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    from argparse import ArgumentParser
    p = ArgumentParser(description="Livestream a globbed input file list")
    p.add_argument('site',
                   help='site to stream: [youtube,periscope,facebook,twitch]',
                   nargs='?', default='localhost')
    p.add_argument('path', help='path to discover files from')
    p.add_argument('glob', help='file glob pattern to stream.')
    p.add_argument('-i', '--ini', help='*.ini file with stream parameters',
                   default='stream.ini')
    p.add_argument('-image',
                   help='static image to display, for audio-only files.')
    p.add_argument('-shuffle', help='shuffle the globbed file list',
                   action='store_true')
    p.add_argument('-loop', help='repeat the globbed file list endlessly',
                   action='store_true')
    p.add_argument('-y', '--yes', help='no confirmation dialog',
                   action='store_true')
    p.add_argument('-nometa', help='do not add metadata caption to video',
                   action='store_false')
    P = p.parse_args()

    path = Path(P.path).expanduser()
    site = P.site.split()
    flist = list(path.glob(P.glob))

    if not flist:
        raise FileNotFoundError(f'did not find files with {path} {P.glob}')

    print('streaming these files. Be sure list is correct! \n')
    print('\n'.join(map(str, flist)))
    print()

    if P.yes:
        print('going live on', site)
    else:
        input(f"Press Enter to go live on {site}.    Or Ctrl C to abort.")

    inifn = Path(P.ini).expanduser()

    usemeta = P.nometa

    if P.loop:
        while True:
            playonce(flist, P.image, site, inifn, P.shuffle, usemeta, P.yes)
    else:
        playonce(flist, P.image, site, inifn, P.shuffle, usemeta, P.yes)
