from decibel.interface.analyze_song_with_tabs import analyze_song_with_tabs
from decibel.import_export.change_or_read_Data_path import change_Data_path, read_Data_path

import os


def interface(
        interface_mode=None,
        data_path: str = None,
        song_title: str = None,
        song_album: str = None,
        song_artist: str = None,
        visualize=False,
        splits=2,
        multithreading=False
):
    data_dir = None
    # path
    if data_path == ".":
        data_dir = os.path.dirname(os.path.realpath(__file__))
    else:
        data_dir = data_path

    # mode
    if interface_mode == "analyze":
        analyze_song_with_tabs(
            song_title=song_title,
            song_album=song_album,
            song_artist=song_artist,
            input_song_audio_path=data_dir + "input_song.mp3",
            input_song_tab_path=data_dir + "input_tab.txt",
            input_hmm_parameters_path=data_dir + "input_HMMParameters.json",
            input_ground_truth_chord_labels_path=data_dir + "input_ground_truth_chord_"
                                                            "labels.lab",
            input_ground_truth_segmentation_labels_path=data_dir + "input_ground_truth"
                                                                   "_segmentation.lab",
            intermediate_parsed_chords_path=data_dir + "intermediate_parsed_chords.txt",
            intermediate_audio_features_write_path=data_dir + "intermediate_song_audio_"
                                                              "features.npy",
            output_aligned_tab_write_path=data_dir + "output_aligned_tab.lab",
            output_visualization_path=data_dir + "output_visualization.png",
            visualize=visualize)
    elif interface_mode == "train":
        # change Data path
        change_Data_path(data_dir)

        # call for training
        from decibel.interface.train_hmm import train_HMM
        train_HMM(splits=splits, multithreading=multithreading)
