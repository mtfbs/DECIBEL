from __future__ import unicode_literals

import youtube_dl


def dowload_mp3_from_youtube(url):

    ydl_opts = {'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}]}

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])