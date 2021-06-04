import multiprocessing as mp
import sys

from decibel.audio_tab_aligner import feature_extractor, jump_alignment
from decibel.import_export import filehandler, hmm_parameter_io
from decibel.music_objects.chord_vocabulary import ChordVocabulary
from decibel.music_objects.song import Song
from sklearn.model_selection import KFold
from decibel.music_objects.pitch_class import PitchClass
from decibel.utils.get_chord_vocabulary import get_chord_vocabulary

from decibel.tab_chord_parser import tab_parser

NR_CPU = max(mp.cpu_count() - 1, 1)


def train_HMM(splits=2, multithreading=False, chord_vocabulary=None):
    ########################
    # DATA SET PREPARATION #
    ########################
    print('Preparing dataset...', end='')
    # Make sure the file structure is ready
    # filehandler.init_folders()

    # Collect all songs and paths to their audio, MIDI and tab files, chord annotations and ground truth labels
    all_songs = filehandler.get_all_songs()

    # TODO - DECIDE TO IMPLEMENT OR REMOVE BELOW CODE
    # Decides what chord vocabulary to use based on dataset tabs
    # song = all_songs[1]
    # print("song title --> " + str(song.title))
    # chords = []
    # if len(song.full_tab_paths) > 1:
    #     untimed_chord_sequence = tab_parser.classify_tabs_from_file(song.full_tab_paths[0])
    #     for chord in untimed_chord_sequence.untimed_chord_sequence_item_items:
    #         chords.append(chord.chord_str)
    # print("song chords --> " + str(chords))

    # choose chord_vocabulary
    if chord_vocabulary is None:
        chord_vocabulary = "MajorMinor"

    chord_vocabulary = get_chord_vocabulary(chord_vocabulary)

    # Retrieve the chord vocabulary from the templates.

    print(" OK")

    # TODO - DECIDE TO IMPLEMENT OR REMOVE BELOW CODE
    # remove chords from the chord vocabulary that aren't in any song.
    # for chord_template in chord_vocabulary.chord_templates:
    #     key = chord_template.key
    #     chord_str = str(PitchClass(key))
    #     print(f"{chord_str}{chord_template.mode}")

    ###############################
    #    AUDIO PRE-PROCESSING    #
    ###############################
    print('Extracting features from audio and pre-processing files...', end='')

    def prepare_song(s: Song):
        feature_extractor.export_audio_features_for_song(song=s)

    if multithreading is True:
        # Pre-process songs for (training) jump alignment
        pool = mp.Pool(NR_CPU)
        for song_key in all_songs:
            pool.apply_async(prepare_song, args=(all_songs[song_key],), callback=print)
        pool.close()
        pool.join()
    else:
        for song_key in all_songs:
            prepare_song(all_songs[song_key])

    print(" OK")

    ###############################
    # TRAINING JUMP ALIGNMENT HMM #
    ###############################
    print('Training HMM parameters...', end='')

    # Train HMM parameters for jump alignment
    kf = KFold(n_splits=splits, shuffle=True, random_state=42)
    hmm_parameter_dict = {}
    song_keys = list(all_songs.keys())
    for train_indices, test_indices in kf.split(all_songs):
        hmm_parameters_path = filehandler.get_hmm_parameters_path(train_indices)
        if filehandler.file_exists(hmm_parameters_path):
            hmm_parameters = hmm_parameter_io.read_hmm_parameters_file(hmm_parameters_path)
        else:
            hmm_parameters = jump_alignment.train(chord_vocabulary,
                                                  {song_keys[i]: all_songs[song_keys[i]] for i in list(train_indices)})
            hmm_parameter_io.write_hmm_parameters_file(hmm_parameters, hmm_parameters_path)

        for test_index in test_indices:
            song_key = song_keys[test_index]
            hmm_parameter_dict[song_key] = hmm_parameters

    print(' OK')
    print('HMM training finished!')
