import os
from decibel.web_integration.spotify_api import search_song
from decibel.interface.interface import interface
from decibel.file_scraper.tab_scraper import search_tabs
from decibel.file_scraper.tab_scraper import download_tab


def decibel_CLI():
    clear = lambda: os.system('clear')

    # Main screen
    print(" #### Welcome to DECIBEL CLI #### ", end='\n\n')
    print("What do you want to do?")
    print("1 - Search a song")
    print("2 - Train a new Hidden Markov Model")
    input_number = int(input())
    clear()
    if input_number == 1:
        print(" ### Search song ### ")
        print("Enter the name of the song:")
        song_name_input = input()
        clear()
        search_results = search_song(song_name_input)
        if len(search_results) == 0:
            print("Im sorry, could not find the song :/")
            return 0
        print("Which one?")
        for i in range(0, len(search_results)):
            print(f"{i} --> {search_results[i]['song_title']} - {search_results[i]['artist_name']}")
        print('')
        input_number = int(input('Song number: '))
        song_title = search_results[input_number]['song_title']
        artist_name = search_results[input_number]['artist_name']
        song_id = search_results[input_number]['song_id']
        print(song_id)
        clear()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        print("Searching for tabs online...")
        url_list = search_tabs(song_title=song_title, absolute_write_path=current_dir, artist_name=artist_name, limit=6)
        print("What url looks more correct?")
        for i in range(0, len(url_list)):
            print(f"{i} --->  {url_list[i]}")
        input_number = int(input())
        print("Downloading tab from the internet...")
        download_tab(
            tab_url=url_list[input_number],
            tab_directory=current_dir,
            tab_name=f"{song_title}-{artist_name}"
        )

        # TODO - process the song and tab
        # TODO - show results (final json file)

        # LIST OF TODO'S FOR IMPROVEMENT
        # TODO - improve tabs
        # TODO - grade tabs
        # TODO - edit tabs
        # TODO - edit timing of chords
        # TODO - graphic user interface (frontend (react js?) )

    else:
        print(" ### Train HMM ### ")
        print("Enter the absolute path to you 'Data' folder:")
        data_folder_path = input()
        clear()
        print("How many splits on KFold?")
        n_splits_input = int(input())
        print("With what chord vocabulary?")
        chord_vocabularies = ['MajorMinor', 'MajorMinorSevenths']
        for i in range(0, len(chord_vocabularies)):
            print(f"{i} --> {chord_vocabularies[i]}")
        chord_vocabulary_input = int(input())
        print("Enable multithreading? (it may not work on windows and mac)")
        print(" 1 - Yes")
        print(" 2 - No")
        multithreading_input = int(input())
        clear()
        print("Pre-process dataset songs with Deezer Spleeter? (warning: it will take much longer).")
        print("1 - No\n2 - Yes, with 2 stems (remove vocals)\n3- Yes, with 4 stems (remove vocals and bass)")
        spleeter_input = int(input())
        if spleeter_input == 2 or spleeter_input == 4:
            print("Are you really sure? all files will be replaced with the results of the processing.")
            spleeter_input = int(input())
            if spleeter_input == 2 or spleeter_input == 4:
                if spleeter_input == 2:
                    pass
                elif spleeter_input == 3:
                    pass

        # TODO - GOOGLE COLAB
        # TODO - DOCKER, BACKEND, BANCO DE DADOS
        # TODO - IMPLEMENTAR NOVOS MÉTODOS DE TREINAMENTO (MÉTODO DA SEQUÊNCIA EXATA E/OU BAG DE ACORDES)
        # TODO - IMPLEMENTAR MAIS VOCABULÁRIOS DE ACORDES

        # TODO - RECORD VIDEO showing drawing

        interface(
            interface_mode='train',
            data_path=data_folder_path,
            splits=n_splits_input,
            multithreading=True if multithreading_input == 1 else False,
            chord_vocabulary="MajorMinor" if chord_vocabulary_input == 0 else "MajorMinorSevenths")


decibel_CLI()
