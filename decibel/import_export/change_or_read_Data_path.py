from os import path


def read_Data_path():
    # read the current set path for the example_input_files folder
    with open(path.join(path.dirname(__file__), 'data_path.txt'), 'r') as file:
        data_path = file.readline()
    return data_path


def change_Data_path(new_path):
    # change the path for the example_input_files folder
    with open(path.join(path.dirname(__file__), 'data_path.txt'), 'w+') as file:
        file.write(new_path)
    print("Data folder changed to: " + read_Data_path())
