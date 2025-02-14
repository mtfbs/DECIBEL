from typing import Tuple, List

import librosa
import numpy as np
import mir_eval

from decibel.music_objects.song import Song

def get_audio_features(audio_path: str, sampling_rate: int, hop_length: int, song: Song = None) -> Tuple[np.ndarray, np.ndarray]:
    # Load audio with small sampling rate and convert to mono. Audio is an array with a value per *sample*
    audio, _ = librosa.load(audio_path, sr=sampling_rate, mono=True)

    # Separate harmonics and percussives into two waveforms. We get two arrays, each with one value per *sample*
    audio_harmonic, audio_percussive = librosa.effects.hpss(audio)

    # Beat track on the percussive signal. The result is an array of *frames* which are on a beat
    beat_frames = []
    tempo = None
    if song is not None:
        tempo, beat_frames = librosa.beat.beat_track(y=audio_percussive, sr=sampling_rate, hop_length=hop_length,
                                                     trim=False)
    else:
        _, beat_frames = librosa.beat.beat_track(y=audio_percussive, sr=sampling_rate, hop_length=hop_length,
                                                 trim=False)

    # Compute chroma features from the harmonic signal. We get a 12D array of chroma for each *frame*
    chromagram = librosa.feature.chroma_cqt(y=audio_harmonic, sr=sampling_rate, hop_length=hop_length)

    # Make sure the last beat is not longer than the length of the chromagram
    beat_frames = librosa.util.fix_frames(beat_frames, x_max=chromagram.shape[1])

    # Aggregate chroma features between *beat events*. We use the mean value of each feature between beat frames
    beat_chroma = librosa.util.sync(chromagram, beat_frames)
    beat_chroma = np.transpose(beat_chroma)

    # Translate beats from frames to time domain
    beat_times = librosa.frames_to_time(beat_frames, sr=sampling_rate, hop_length=hop_length)

    if song is not None:
        return tempo, beat_times, beat_chroma
    else:
        return beat_times, beat_chroma


def beat_align_ground_truth_labels(ground_truth_labels_path: str, beat_times: np.ndarray) -> List[str]:
    """
    Beat-synchronize the reference chord annotations, by assigning the chord with the longest duration within that beat

    :param ground_truth_labels_path: Path to the ground truth file
    :param beat_times: Array of beats, measured in seconds
    :return: List of chords within each beat
    """
    # Load chords from ground truth file
    (ref_intervals, ref_labels) = mir_eval.io.load_labeled_intervals(ground_truth_labels_path)

    # Find start and end locations of each beat
    beat_starts = beat_times[:-1]
    beat_ends = beat_times[1:]

    # Create the longest_chords list, which we will fill in the for loop
    longest_chords_per_beat = []
    for i in range(beat_starts.size):
        # Iterate over the beats in this song, keeping the chord with the longest duration
        b_s = beat_starts[i]
        b_e = beat_ends[i]
        longest_chord_duration = 0
        longest_chord = 'N'
        for j in range(ref_intervals.shape[0]):
            # Iterate over the intervals in the reference chord annotations
            r_s = ref_intervals[j][0]  # Start time of reference interval
            r_e = ref_intervals[j][1]  # End time of reference interval
            if r_s < b_e and r_e > b_s:
                # This reference interval overlaps with the current beat
                start_inside_beat = max(r_s, b_s)
                end_inside_beat = min(r_e, b_e)
                duration_inside_beat = end_inside_beat - start_inside_beat
                if duration_inside_beat > longest_chord_duration:
                    longest_chord_duration = duration_inside_beat
                    longest_chord = ref_labels[j]
        # Add the chord with the longest duration to our list
        longest_chords_per_beat.append(longest_chord)

    return longest_chords_per_beat


def get_feature_ground_truth_matrix(full_audio_path: str, ground_truth_labs_path: str) -> np.matrix:
    # First obtain the audio features per beat using librosa.
    beat_times, beat_chroma = get_audio_features(full_audio_path, sampling_rate=22050, hop_length=256)
    # Align the ground truth annotations to the beats.
    longest_chords_per_beat = beat_align_ground_truth_labels(ground_truth_labs_path, beat_times)
    # Combine the beat times, chroma values and chord labels into a matrix with 14 columns and |beats| rows.
    times_features_class = np.c_[beat_times[:-1], beat_chroma, longest_chords_per_beat]
    return times_features_class


def export_audio_features_for_song(song: Song, audio_features_path: str = None) -> None:
    """
    Export the audio features of this song to a file.

    For this purpose, we use the python package librosa. First, we convert the audio file to mono. Then, we use the
    HPSS function to separate the harmonic and percussive elements of the audio. Then, we extract chroma from the
    harmonic part, using constant-Q transform with a sampling rate of 22050 and a hop length of 256 samples. Now we
    have chroma features for each sample, but we expect that the great majority of chord changes occurs on a beat.
    Therefore, we beat-synchronize the features: we run a beat-extraction function on the percussive part of the audio
    and average the chroma features between the consecutive beat positions. The chord annotations need to be
    beat-synchronized as well. We do this by taking the most prevalent chord label between beats. Each mean feature
    vector with the corresponding beat-synchronized chord label is regarded as one frame.

    :param song: Song for which we export the audio features
    :param audio_features_path: path to where the audio_features.npy internally used file should be written
    """
    if song.full_ground_truth_chord_labs_path != '':
        # There are chord labels for this song
        does_file_exist = True
        write_path = ""
        if audio_features_path is not None:
            write_path = audio_features_path
        elif audio_features_path is None:
            from decibel.import_export import filehandler
            write_path = filehandler.get_full_audio_features_path(song.key)
            does_file_exist = filehandler.file_exists(write_path)
        if does_file_exist:
            # We already extracted the audio features
            song.audio_features_path = write_path
        else:
            # We still need to extract the audio features.
            times_features_class = get_feature_ground_truth_matrix(song.full_audio_path,
                                                                   song.full_ground_truth_chord_labs_path)

            # Export the beat, feature and class matrix to the write_path (a binary .npy file)
            song.audio_features_path = write_path
            np.save(write_path, times_features_class)
