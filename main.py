# import necessary modules
import datetime

import logging
import logging_config
from data_functions import read_csv_files, save_combined_csv, save_new_columns_csv


def main():
    logging_config.configure_logging()  # Configure the logging
    root_path = r"I:\Shared drives\Data Analysis\Data\Bank Data"
    try:
        df_list, new_columns_list, root = read_csv_files(root_path)
        save_combined_csv(df_list, root,
                          f'Combined Transactions Data {datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.csv')
        save_new_columns_csv(new_columns_list, root,
                             f'New Columns {datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.csv')
        logging.info('Code ran successfully and without errors')  # Log a message if the code ran successfully
    except Exception as e:
        logging.exception(e)  # Log the exception if an error occurred


if __name__ == '__main__':
    main()
