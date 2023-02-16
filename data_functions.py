import os
import glob
import pandas as pd
import json
import re
import datetime
from loguru import logger


def is_csv_file(file):
    _, file_ext = os.path.splitext(file)
    return file_ext.lower() == '.csv'


def delete_files(root, file_pattern):
    """
    Deletes all files in the specified root directory and its subdirectories that match the given file pattern.

    Parameters:
    - root (str): The root directory to search for files.
    - file_pattern (str): The file pattern to match. Can include wildcards (e.g. '*.csv').

    Returns:
    - None
    """
    files = glob.glob(os.path.join(root, '**', file_pattern), recursive=True)
    if not files:
        logger.info(f'No files found matching pattern "{file_pattern}"')
    else:
        for file in files:
            try:
                os.remove(file)
                logger.success(f'Deleted file {file}')
            except FileNotFoundError:
                logger.info(f'No files found matching pattern "{file_pattern}"')


def extract_last_four_digits(base_name):
    """
    Extracts the four digits after the word 'Chase' from a base name string.

    Parameters:
    - base_name (str): The base name string from which to extract the digits.

    Returns:
    - str: The four digits after the word 'Chase' in the base name string, or an empty string if the four digits are not
           found.
    """
    # Use a regular expression to extract the four digits after the word "Chase" in the base name
    match = re.search(r'Chase(\d{4})', base_name)
    if match:
        last_four_digits = match.group(1)
        return last_four_digits
    return base_name


def get_financial_id(base_name):
    """
    Given a base name, returns the corresponding 'Financial account ID' from the 'bank_codes.json' file, or the original
    base name if no matching 'Financial account ID' is found.

    Parameters:
    - basename (str): The base name to be searched in the 'bank_codes.json' file.

    Returns:
    - str: The 'Financial account ID' corresponding to the base name, or the original base name if no matching
           'Financial account ID' is found.
    """
    with open('variables/bank_codes.json', 'r') as f:
        bank_codes = json.load(f)
    last_four_digits = extract_last_four_digits(base_name)
    for code in bank_codes:
        if code['Last Four Digits'] == last_four_digits:
            return code['Financial account ID']
    logger.info(f'Base name "{base_name}" not found in bank codes data. Using base name as financial ID.')
    return base_name


def read_csv_with_headers_in_row(filename, row_number):
    """
    Reads a CSV file and returns a data frame. The specified row number is used as the header.

    Parameters:
    - filename (str): The name of the CSV file to read.
    - row_number (int): The row number to use as the header.

    Returns:
    - df (pandas.DataFrame): The data frame created from the CSV file.

    Exceptions:
    - pd.errors.EmptyDataError: If the file is empty or has no data.
    - UnicodeDecodeError: If there is a problem with the encoding of the file.
    """
    try:
        df = pd.read_csv(filename, header=row_number - 1)
    except pd.errors.EmptyDataError:
        logger.error("Error: The file is empty or has no data.")
    except UnicodeDecodeError:
        logger.error("Error: There is a problem with the encoding of the file.")
    return df


def read_csv_files(root_path):
    """
    Reads all CSV files in the directories and subdirectories of the specified root path, and returns a list of the data
    frames and a list of the new columns found in the files.

    Parameters:
    - root_path (str): The root directory to search for CSV files.

    Returns:
    - tuple: A tuple containing two lists:
        - df_list (list): A list of data frames, where each data frame corresponds to a CSV file that was read.
        - new_columns_list (list): A list of data frames containing the new columns found in each CSV file. Each data
          frame contains a 'Location' column indicating the base name of the file in which the new columns were found.
    """
    # Create a list to hold the data frames and used as placeholder to reset the data for every folder
    df_list = []
    new_columns_list = []

    # Iterate over the directories in root_path and its subdirectories
    for root, dirs, files in os.walk(root_path):
        # Reset df_list and new_columns_list for each folder
        df_list = []
        new_columns_list = []

        # Delete the 'New Columns *.csv' and 'Combined Transactions Data *.csv' files before reading the CSV files
        delete_files(root, 'New Columns.csv')
        delete_files(root, 'Combined Transactions Data.csv')

        # Find all CSV files in the current directory
        file_pattern = os.path.join(root, '*.csv')
        for file in glob.glob(file_pattern):
            logger.info(f'Reading file {file}...')
            try:
                df = pd.read_csv(file, index_col=False)
            except pd.errors.ParserError:
                logger.warning(f'File {file} is not a valid CSV file. Trying again with headers in row 3...')
                df = read_csv_with_headers_in_row(file, 3)
            base_name = os.path.splitext(os.path.basename(file))[0]  # Get the base name of the file (without the
            # extension)
            df['Location'] = get_financial_id(base_name)  # Add a new column to the data frame
            new_columns = set(df.columns) - set(df_list[0].columns) if df_list else set()
            if new_columns:
                logger.info(f'Found new columns {new_columns} in file {file}')
                new_columns_df = df[list(new_columns)].copy()
                new_columns_df.loc[:, 'Location'] = base_name  # Use .loc to set the value of the 'filename' column
                new_columns_list.append(new_columns_df)
            df_list.append(df.drop(columns=list(new_columns)))
            root = os.path.dirname(file)  # Get the directory of the current file
            save_combined_csv(df_list, root,
                              'Combined Transactions Data.csv')  # Save the combined CSV file to the current directory
            save_new_columns_csv(new_columns_list, root,
                                 'New Columns.csv')  # Save the new columns CSV file to the current directory
    return df_list, new_columns_list


def save_combined_csv(df_list, root, filename):
    """
    Saves a combined data frame, which is the concatenation of all data frames in the df_list, to a CSV file with the
    specified filename in the specified root directory.

    Parameters:
    - df_list (list): A list of data frames to be concatenated.
    - root (str): The root directory to save the CSV file in.
    - filename (str): The name of the CSV file to save.

    Returns:
    - None
    """
    try:
        df = pd.concat(df_list, ignore_index=True)
        file_path = os.path.join(root, filename)  # Construct the full file path
        logger.info(f'Saving combined data frame to file {filename}...')
        df.to_csv(file_path, index=False)
        logger.success(f'Saved combined data frame to file {filename} successfully.')
    except ValueError as e:
        if str(e) == "No objects to concatenate":
            logger.error("Error on Combined Transactions Data: No objects to concatenate")
        else:
            raise e


def save_new_columns_csv(new_columns_list, root, filename):
    """
    Saves a data frame containing new columns found in the CSV files to a CSV file with the specified filename in the
    specified root directory.

    Parameters:
    - new_columns_list (list): A list of data frames containing the new columns found in each CSV file. Each data
      frame contains a 'Location' column indicating the base name of the file in which the new columns were found.
    - root (str): The root directory to save the CSV file in.
    - filename (str): The name of the CSV file to save.

    Returns:
    - None
    """
    try:
        new_columns_df = pd.concat(new_columns_list, ignore_index=True)
        if not new_columns_df.empty:
            file_path = os.path.join(root, filename)  # Construct the full file path
            logger.info(f'Saving new columns data frame to file {filename}...')
            new_columns_df.to_csv(file_path)
    except ValueError as e:
        if str(e) == "No objects to concatenate":
            logger.error("Error on New Columns: No objects to concatenate")
        else:
            raise e
