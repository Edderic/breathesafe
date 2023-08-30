import re
import pandas as pd
import sys
import os
from pathlib import Path


# - Start a measurement
# - Stop a measurement

# - Make a variation of what already exists

#   - Use a row as a template
#   - Pick a column to update
#   - Suggest a list of things from that column
#   - Be able to add a new entry if the column does not yet exist

def create_list_options(array):
    string = ""
    last_i = 0
    for i, x in enumerate(array):
        string += f"\n {i}: {x}"
        last_i = i

    string += f"\n {last_i + 1}: OTHER\n"
    return string


def get_item_from_index(array, index, column):
    try:
        return array[int(index)]
    except IndexError:
        return input(f"Please type in the value for {column}:\n\n")

def get_item_console(column, experiments_df):

    try:
        array = experiments_df[column].unique()
    except Exception as e:
        import pdb; pdb.set_trace()
    index = input(f"Which {column}?\n\n{create_list_options(array)}")
    return get_item_from_index(array, index, column)

def use_last_row_as_template(df):
    last_row = df.tail(1).iloc[0]
    return input(f"Do you want to use the last row as template? (y/n)\n\nLast row: {last_row}\n")

def column_to_modify(df):
    array = df.columns
    index = input(f"Which column would you like to modify?\n\n{create_list_options(df.columns)}")

    try:
        return array[int(index)]
    except IndexError:
        if input(f"Would you like to create a new column? (y/n)\n") == 'y':
            return input(f"What's the name of the new column?\n")




if __name__ == '__main__':
    collection = []


    cwd = os.getcwd()
    cwd_path = Path(cwd)

    experiments_path = cwd_path / "air_cleaner_data" / "personal-air-cleaner-experiments - Sheet1.csv"
    air_cleaner_data_path = cwd_path / 'air_cleaner_data'

    data_paths = list(air_cleaner_data_path.glob("*"))

    data_paths_sorted = sorted([
        '../air_cleaner_data' + re.search(
            '(?<=air_cleaner_data).*',
             str(path)
         )[0]
        for path in data_paths
    ])

    filepath_index = input(f"Which filepaths contain the data? {create_list_options(data_paths_sorted)}")
    filepath = data_paths_sorted[int(filepath_index)]
    row = {}

    while True:
        experiments_df = pd.read_csv(experiments_path)
        if use_last_row_as_template(experiments_df) == 'y':
            row = experiments_df.tail(1).iloc[0]
            columns = experiments_df.columns

            while input(f"Do you want to change anything in the following columns? (y/n)\n\n{columns}") == 'y':
                column = column_to_modify(experiments_df)

                row[column] = input("What's the value for this column?\n")
        else:
            columns = [
                'Experiment',
                'Fan',
                'shroud',
                'push filters',
                'pull filters',
                'Distance (in)',
            ]

            row = {col: get_item_console(col, experiments_df) for col in columns}

        row['filepath'] = str(filepath)

        start = input("Start? (y/n)\n")
        if start == 'y':
            row['start_time'] = pd.to_datetime('now')
            print(f'Start time: {row["start_time"]}')

        stop = input("Stop? (y/n)\n")
        if start == 'y' and stop == 'y':
            row['end_time'] = pd.to_datetime('now')
            print(f'end time: {row["end_time"]}')

        appended = experiments_df.append(row, ignore_index=True)
        print(f"Saving to {str(experiments_path)}")
        appended.to_csv(str(experiments_path), index=False)
        print(f"Saved to {str(experiments_path)}!")



