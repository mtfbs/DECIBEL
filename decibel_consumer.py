import os
from decibel.web_integration.spotify_api import search_song
from decibel.interface.interface import interface
from decibel.file_scraper.tab_scraper import search_tabs
from decibel.file_scraper.tab_scraper import download_tab
from decibel.file_scraper.audio_scraper import dowload_mp3_from_youtube
from youtube_search import YoutubeSearch
from decibel.utils.deezer_spleeter_wrappers import spleet_and_replace_all_songs_from_directory
import shutil



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
        print("song id (from spotify): " + str(song_id))
        clear()
        current_dir = os.path.dirname(os.path.realpath(__file__))
        print("Searching for tabs online...")
        url_list = search_tabs(song_title=song_title, absolute_write_path=current_dir, artist_name=artist_name, limit=6)
        print("Which url looks more correct?")
        for i in range(0, len(url_list)):
            print(f"{i} --->  {url_list[i]}")
        input_number = int(input())
        print("Downloading tab from the internet...")
        download_tab(
            tab_url=url_list[input_number],
            tab_directory=current_dir,
            tab_name=f"input_tab.txt"
        )
        # search song from youtube
        results = YoutubeSearch(song_title + ' ' + artist_name, max_results=5).to_dict()
        print("Which title looks more correct?")
        for i in range(0, len(results)):
            print(f"{i} --->  {results[i]['title']}")
        input_number = int(input())
        print("Downloading song from the internet...")
        video_url = results[input_number]['id']
        dowload_mp3_from_youtube(video_url)
        # os.rename(f"{current_dir}/")
        # Process song normally
        interface(interface_mode="analyze", song_title=song_title, song_album='', song_artist=artist_name,data_path=current_dir, hmm_param_number=0)

        # Show final result


        # TODO - show results (final json file)



    else:
        print(" ### Train HMM ### ")
        print("Enter the absolute path to your 'Data' folder:")
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
                    spleet_and_replace_all_songs_from_directory(
                        working_directory_absolute_path=f"{data_folder_path}/Input/Audio",
                        number_of_stems=2)
                elif spleeter_input == 3:
                    spleet_and_replace_all_songs_from_directory(
                        working_directory_absolute_path=f"{data_folder_path}/Input/Audio",
                        number_of_stems=4)
        # Train HMM
        interface(
            interface_mode='train',
            data_path=data_folder_path,
            splits=n_splits_input,
            multithreading=True if multithreading_input == 1 else False,
            chord_vocabulary="MajorMinor" if chord_vocabulary_input == 0 else "MajorMinorSevenths")


        current_dir = os.path.dirname(os.path.realpath(__file__))


        # move the trained models to the current folder (so it can be used for processing songs later)
        # trazer os HMM Parâmetros gerados a este diretório e dar a opção de escolher qual deles rodar
        hmmparameters_folder = data_folder_path + "/Files/HMMParameters/"
        i = 0
        for filename in os.listdir(hmmparameters_folder):
            shutil.move(f"{hmmparameters_folder}/{filename}", f"{current_dir}/input_HMMParameters_{i}.json")
            i += 1

        # TODO - GOOGLE COLAB



decibel_CLI()
