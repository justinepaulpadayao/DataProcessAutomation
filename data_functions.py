import os
import glob
import pandas as pd
import datetime
import logging

# Get the logger from the main module
logger = logging.getLogger(__name__)


def is_csv_file(file):
    _, file_ext = os.path.splitext(file)
    return file_ext.lower() == '.csv'


def delete_files(root, file_pattern):
    try:
        for file in glob.glob(os.path.join(root, file_pattern)):  # Find all files matching the pattern
            os.remove(file)  # Delete the file if it exists
    except FileNotFoundError:
        logging.info(f'No files found matching pattern "{file_pattern}"')


def read_csv_files(root_path):
    # Delete the 'New Columns *.csv' and 'Combined Transactions Data *.csv' files before reading the CSV files
    delete_files(root_path, 'New Columns *.csv')
    delete_files(root_path, 'Combined Transactions Data *.csv')

    # Continue with the rest of the function
    df_list = []
    new_columns_list = []
    file_pattern = os.path.join(root_path, '**', '*.csv')  # Find all CSV files in the root path and its subdirectories
    for file in glob.glob(file_pattern, recursive=True):
        logging.info(f'Reading file {file}...')
        df = pd.read_csv(file, index_col=False)
        base_name = os.path.splitext(os.path.basename(file))[0]  # Get the base name of the file (without the extension)
        df['Location'] = base_name
        new_columns = set(df.columns) - set(df_list[0].columns) if df_list else set()
        if new_columns:
            logging.info(f'Found new columns {new_columns} in file {file}')
            new_columns_df = df[list(new_columns)].copy()
            new_columns_df.loc[:, 'Location'] = base_name  # Use .loc to set the value of the 'filename' column
            new_columns_list.append(new_columns_df)
        df_list.append(df.drop(columns=list(new_columns)))
    return df_list, new_columns_list, os.path.dirname(file)  # Return the directory of the file as the third element


def save_combined_csv(df_list, root, filename):
    try:
        df = pd.concat(df_list, ignore_index=True)
        file_path = os.path.join(root, filename)  # Construct the full file path
        logging.info(f'Saving combined data frame to file {filename}...')
        df.to_csv(file_path, index=False)
    except ValueError as e:
        if str(e) == "No objects to concatenate":
            logging.error("Error: No objects to concatenate")
        else:
            raise e


def save_new_columns_csv(new_columns_list, root, filename):
    try:
        new_columns_df = pd.concat(new_columns_list, ignore_index=True)
        if not new_columns_df.empty:
            file_path = os.path.join(root, filename)  # Construct the full file path
            logging.info(f'Saving new columns data frame to file {filename}...')
            new_columns_df.to_csv(file_path)
    except ValueError as e:
        if str(e) == "No objects to concatenate":
            logging.error("Error: No objects to concatenate")
        else:
            raise e
