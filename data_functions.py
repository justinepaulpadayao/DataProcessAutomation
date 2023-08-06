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


def extract_last_four_digits(base_name):
    match = re.search(r'Chase(\d{4})', base_name)
    if match:
        last_four_digits = match.group(1)
        return last_four_digits
    return base_name


def get_financial_id(base_name):
    with open('variables/bank_codes.json', 'r') as f:
        bank_codes = json.load(f)
    last_four_digits = extract_last_four_digits(base_name)
    for code in bank_codes:
        if code['Last Four Digits'] == last_four_digits:
            return code['Financial account ID']
    logger.info(f'Base name "{base_name}" not found in bank codes data. Using base name as financial ID.')
    return base_name


def read_csv_with_headers_in_row(filename, row_number):
    try:
        df = pd.read_csv(filename, header=row_number - 1)
    except pd.errors.EmptyDataError:
        logger.error("Error: The file is empty or has no data.")
    except UnicodeDecodeError:
        logger.error("Error: There is a problem with the encoding of the file.")
    return df


def read_csv_files(root_path):
    df_list = []
    new_columns_list = []
    for root, dirs, files in os.walk(root_path):
        if 'Combined Transactions Data.csv' in files or 'New Columns.csv' in files:
            logger.info(f'Skipping directory {root} as it contains processed files.')
            continue
        df_list = []
        new_columns_list = []
        file_pattern = os.path.join(root, '*.csv')
        for file in glob.glob(file_pattern):
            logger.info(f'Reading file {file}...')
            try:
                df = pd.read_csv(file, index_col=False)
            except pd.errors.ParserError:
                logger.warning(f'File {file} is not a valid CSV file. Trying again with headers in row 3...')
                df = read_csv_with_headers_in_row(file, 3)
            base_name = os.path.splitext(os.path.basename(file))[0]
            df['Location'] = get_financial_id(base_name)
            new_columns = set(df.columns) - set(df_list[0].columns) if df_list else set()
            if new_columns:
                logger.info(f'Found new columns {new_columns} in file {file}')
                new_columns_df = df[list(new_columns)].copy()
                new_columns_df.loc[:, 'Location'] = base_name
                new_columns_list.append(new_columns_df)
            df_list.append(df.drop(columns=list(new_columns)))
            root = os.path.dirname(file)
            save_combined_csv(df_list, root, 'Combined Transactions Data.csv')
            save_new_columns_csv(new_columns_list, root, 'New Columns.csv')
    return df_list, new_columns_list


def save_combined_csv(df_list, root, filename):
    try:
        df = pd.concat(df_list, ignore_index=True)
        file_path = os.path.join(root, filename)
        logger.info(f'Saving combined data frame to file {filename}...')
        df.to_csv(file_path, index=False)
        logger.success(f'Saved combined data frame to file {filename} successfully.')
    except ValueError as e:
        if str(e) == "No objects to concatenate":
            logger.error("Error on Combined Transactions Data: No objects to concatenate")
        else:
            raise e


def save_new_columns_csv(new_columns_list, root, filename):
    try:
        new_columns_df = pd.concat(new_columns_list, ignore_index=True)
        if not new_columns_df.empty:
            file_path = os.path.join(root, filename)
            logger.info(f'Saving new columns data frame to file {filename}...')
            new_columns_df.to_csv(file_path)
    except ValueError as e:
        if str(e) == "No objects to concatenate":
            logger.error("Error on New Columns: No objects to concatenate")
        else:
            raise e
