from decibel.music_objects.chord_vocabulary import ChordVocabulary


def get_chord_vocabulary(vocabulary_title: str = None):
    if vocabulary_title == "Major":
        return ChordVocabulary.generate_chroma_major()
    elif vocabulary_title == "Minor":
        return ChordVocabulary.generate_chroma_minor()
    elif vocabulary_title == "Sevenths":
        return ChordVocabulary.generate_chroma_sevenths()
    elif vocabulary_title == "MajorMinor":
        return ChordVocabulary.generate_chroma_major_minor()
    elif vocabulary_title == "MajorMinorSevenths":
        return ChordVocabulary.generate_chroma_major_minor_sevenths()
    elif vocabulary_title == "MajorMinorSuspendedSevenths":
        return ChordVocabulary.generate_chroma_major_minor_suspended_sevenths()
