from decibel.interface.interface import interface

# interface(
#     interface_mode='train',
#     data_path='/media/mateus/d327fe54-744e-4ae4-8f16-46173d0ba432/pastas/git/moises_final/scalableDECIBEL/Data',
#     song_title='song-title',
#     song_album='song-album',
#     song_artist='song-artist',
#     visualize=False,
#     splits=2,
#     multithreading=False
# )

interface(
    interface_mode='analyze',
    data_path='/home/mateus/hdd/pastas/git/moises_final/scalableDECIBEL/downloads/input_for_analysis/',
    visualize=True,
    song_title='song-title',
    song_album='song-album',
    song_artist='song-artist',
)
