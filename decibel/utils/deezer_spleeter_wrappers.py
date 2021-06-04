# This code assumes that the deezer spleeter is installed as a CLI program

from pydub import AudioSegment
import os
import shutil
from pathlib import Path


def spleet_song(working_directory_absolute_path=None, input_file_name="song.mp3", output_file_name="spleeted_song.mp3",
                number_of_stems=2):
    """
    The output is:       only one file without vocals        --> 2 stems   or
                         only one file without vocals and bass --> 4 stems
    """

    file_absolute_path = working_directory_absolute_path + '/' + input_file_name

    # open file with pydub
    song = AudioSegment.from_mp3(file_absolute_path)
    song_channels = song.split_to_mono()
    song = song_channels[0]

    # create slices of 80 seconds or less
    print("Creating song slices")
    song_slices = []
    duration_ms = song.duration_seconds * 1000
    slice_duration_ms = 80 * 1000
    song_cursor = 0
    last_cursor_position = 0
    while duration_ms > 0:
        if duration_ms > slice_duration_ms:
            duration_ms -= slice_duration_ms
            song_cursor += slice_duration_ms
            song_slices.append(song[last_cursor_position:song_cursor])
            last_cursor_position = song_cursor
        else:
            duration_ms = 0
            song_slices.append(song[last_cursor_position:])

    # write song slices to memory
    number_of_slices = len(song_slices)
    for i in range(0, number_of_slices):
        song_slices[i].export(f"{working_directory_absolute_path}/song_slice_{i}.mp3")

    # call deezer spleeter on each slice
    print("Calling deezer spleeter")
    for i in range(0, number_of_slices):
        os.system(
            f'spleeter separate -p spleeter:{number_of_stems}stems -o {working_directory_absolute_path}/output {working_directory_absolute_path}/song_slice_{i}.mp3')

    # concatenate slices and write final file
    print("Concatenating spleeted files")
    spleeted_song_slices = []
    # 2 stems
    if number_of_stems == 2:
        for i in range(0, number_of_slices):
            spleeted_song_slices.append(
                AudioSegment.from_mp3(f"{working_directory_absolute_path}/output/song_slice_{i}/accompaniment.wav"))
        song_without_vocals = spleeted_song_slices[0]
        if number_of_slices > 0:
            for i in range(1, number_of_slices):
                song_without_vocals += spleeted_song_slices[i]
        # writes
        song = AudioSegment.from_mono_audiosegments(song, song)
        song_without_vocals.export(f"{working_directory_absolute_path}/{output_file_name}")
        # delete residual files
        shutil.rmtree(f'{working_directory_absolute_path}/output')
        for i in range(0, number_of_slices):
            os.remove(f"{working_directory_absolute_path}/song_slice_{i}.mp3")
        print("successs.")
    # 4 stems
    elif number_of_stems == 4:
        spleeted_song_slices_drums = []
        spleeted_song_slices_other = []
        for i in range(0, number_of_slices):
            spleeted_song_slices_drums.append(
                AudioSegment.from_mp3(f"{working_directory_absolute_path}/output/song_slice_{i}/drums.wav"))
            spleeted_song_slices_other.append(
                AudioSegment.from_mp3(f"{working_directory_absolute_path}/output/song_slice_{i}/other.wav"))
        song_with_only_drums = spleeted_song_slices_drums[0]
        song_with_only_other = spleeted_song_slices_other[0]
        if number_of_slices > 0:
            for i in range(1, number_of_slices):
                song_with_only_drums += spleeted_song_slices_drums[i]
                song_with_only_other += spleeted_song_slices_other[i]
        # two channels to one
        song_without_drums_and_bass = song_with_only_drums.overlay(song_with_only_other)
        # writes
        song_without_drums_and_bass.export(f"{working_directory_absolute_path}/{output_file_name}")
        # delete residual files
        shutil.rmtree(f'{working_directory_absolute_path}/output')
        for i in range(0, number_of_slices):
            os.remove(f"song_slice_{i}.mp3")
        print("song_without_vocals_and_base.mp3 was successfully created.")


def spleet_and_replace_all_songs_from_directory(working_directory_absolute_path, number_of_stems=2):
    working_directory_absolute_path = working_directory_absolute_path + '/'
    for filename in os.listdir(working_directory_absolute_path):
        if not os.path.isdir(working_directory_absolute_path + filename):
            spleet_song(
                working_directory_absolute_path=working_directory_absolute_path,
                input_file_name=filename,
                output_file_name=filename,
                number_of_stems=number_of_stems
            )


# spleet_all_songs_from_directory(
#     working_directory_absolute_path="/home/mateus/hdd/pastas/git/moises_final/scalableDECIBEL/decibel/utils/dir/",
#     number_of_stems=2)

# spleet_song(
#     working_directory_absolute_path="/home/mateus/hdd/pastas/git/moises_final/scalableDECIBEL/decibel/utils/dir",
#     input_file_name="2.mp3",
#     output_file_name="output.mp3",
#     number_of_stems=2)
