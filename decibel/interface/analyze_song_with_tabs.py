import warnings
import math
import numpy
import json
import sys

# DECIBEL+ imports
from decibel.audio_tab_aligner import feature_extractor, jump_alignment
from decibel.data_fusion import data_fusion
from decibel.import_export import hmm_parameter_io
from decibel.music_objects.chord_vocabulary import ChordVocabulary
from decibel.music_objects.song import Song
from decibel.tab_chord_parser import tab_parser
from decibel.evaluator import chord_label_visualiser
from decibel.music_objects.chord_alphabet import ChordAlphabet
from decibel.evaluator import evaluator
from decibel.utils.get_chord_vocabulary import get_chord_vocabulary


def analyze_song_with_tabs(
        song_title=None,
        song_album=None,
        song_artist=None,
        input_song_audio_path=None,
        input_song_tab_path=None,
        input_hmm_parameters_path=None,
        input_ground_truth_chord_labels_path=None,
        input_ground_truth_segmentation_labels_path=None,
        intermediate_parsed_chords_path=None,
        intermediate_audio_features_write_path=None,
        output_aligned_tab_write_path=None,
        output_visualization_path=None,
        visualize=False):
    # if at least one of the essential parameters is not provided, raise Exception#
    if input_song_tab_path is None:
        raise Exception(".mp3 path not provided. (param: input_song_audio_path)")
    if input_song_tab_path is None:
        raise Exception("Tab/chords path not provided. (param: input_song_tab_path)")
    if input_hmm_parameters_path is None:
        raise Exception("HMM parameters not provided. (param: input_hmm_parameters_path")
    if song_title is None:
        raise Exception("Song title not provided.")
    if song_album is None:
        raise Exception("Song album not provided.")
    if song_artist is None:
        raise Exception("Song artist not provided.")

    # Data prep #
    # creates the song class and get passed parameters
    if visualize is False:
        song = Song(title=song_title,
                    album=song_album,
                    artist=song_artist,
                    full_audio_path=input_song_audio_path)
    else:
        song = Song(title=song_title,
                    album=song_album,
                    artist=song_artist,
                    full_audio_path=input_song_audio_path,
                    full_ground_truth_chord_labs_path=input_ground_truth_chord_labels_path,
                    full_segmentation_labs_path=input_ground_truth_segmentation_labels_path)

    # add input song tab path to the song object
    song.add_tab_path(input_song_tab_path)

    # Classification of tabs #
    untimed_chord_sequence = tab_parser.classify_all_tabs_of_song(
        song,
        intermediate_parsed_chords_path,
        input_song_tab_path).untimed_chord_sequence_item_items

    # Get hmm_parameters from an already trained HMM #
    # find best-fit hmm_parameters TODO
    # load the parameters
    hmm_parameters = hmm_parameter_io.read_hmm_parameters_file(input_hmm_parameters_path)

    # jump alignment and generation of tables and figures #
    with warnings.catch_warnings():
        # this will suppress al warnings in this block
        """libsndfile does not support mp3 format by design, so Librosa tries to use libsndfile first, and if it
        fails, it will fall back on the audioread package, which is a bit slower and more brittle, but supports more
        formats. https://github.com/librosa/librosa/issues/1015 """
        # Jump alignment #
        # Run viterbi algorithm on an already trained HMM model to predict time of chords
        warnings.simplefilter("ignore")

        # align chords with sound
        jump_alignment.jump_align(
            intermediate_parsed_chords_path,
            song.full_audio_path,
            output_aligned_tab_write_path,
            hmm_parameters,
            song=song)

        # generate .json with_current_beat, current_beat_time and estimated_chord #
        json_dic = {}
        chord_index = 0
        beat_index = 0
        json_complete_string = "[\n  "
        for time in song.beat_times:
            # change of chord
            if time == song.chords_times[chord_index]:
                chord_index += 1
                if chord_index == len(song.chords_order):
                    chord_index -= 1
            json_dic["current_beat"] = beat_index
            beat_index += 1
            json_dic["current_beat_time"] = time
            json_dic["estimated_chord"] = song.chords_order[chord_index]

            json_item_string = json.dumps(json_dic, indent=3)
            json_complete_string += json_item_string
            json_complete_string = json_complete_string[:-2]
            json_complete_string += "\n  }"
            json_complete_string += ",\n  "

        #   finishes the json string
        json_complete_string = json_complete_string[:-4]
        json_complete_string += "\n]"
        #   writes the final json to a file
        aux_str = output_aligned_tab_write_path[:-4]
        with open(aux_str + "_final.json", "w+") as file:
            file.write(json_complete_string)

        # takes care of evaluation and visualization when ground truth is provided as parameters #
        if visualize is True:
            chord_vocabulary =  get_chord_vocabulary(hmm_parameters.alphabet.chord_vocabulary_name)
            # Generate tables and figures #
            nr_of_samples = int(math.ceil(song.duration * 100))
            alphabet = ChordAlphabet(chord_vocabulary)
            label_data = [{'name': 'Ground truth',
                           'lab_path': song.full_ground_truth_chord_labs_path,
                           'csr': 1.0, 'ovs': 1.0, 'uns': 1.0, 'seg': 1.0}]
            # evaluate song
            csr, ovs, uns, seg = evaluator.evaluate(ground_truth_lab_path=input_ground_truth_chord_labels_path,
                                                    my_lab_path=output_aligned_tab_write_path)
            # print the MIR-eval params
            print(f"""
                CSR: {csr}
                Ovs: {ovs}
                UnS: {uns}
                Seg: {seg}
            """)
            # save evaluation values to label_data
            label_data.append({'name': 'scalabeDECIBEL output',
                               'lab_path': output_aligned_tab_write_path,
                               'csr': csr, 'ovs': ovs, 'uns': uns, 'seg': seg})

            # fill a numpy array with chord labels for each of the lab files
            chord_matrix = numpy.zeros((len(label_data), nr_of_samples), dtype=int)
            for lab_nr in range(len(label_data)):
                data_fusion.load_lab_file_into_chord_matrix(label_data[lab_nr]['lab_path'], lab_nr, chord_matrix,
                                                            alphabet, nr_of_samples)
            all_chords = [chord_matrix[x] for x in range(len(label_data))]

            # Find names
            names = [label_dict['name'] for label_dict in label_data]

            # Find results
            results = ['CSR Ovs UnS Seg']
            for label_dict in label_data[1:]:
                results.append(' '.join([str(round(label_dict[measure], 2)).ljust(4, '0')
                                         for measure in ['csr', 'ovs', 'uns', 'seg']]))

            # Show results
            plt1 = chord_label_visualiser._show_chord_sequences(song, all_chords, [0], names, results, alphabet)

            plt1.savefig(output_visualization_path, bbox_inches="tight")
