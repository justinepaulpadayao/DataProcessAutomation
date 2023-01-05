# import necessary modules
import logging
import logging_config
from data_functions import read_csv_files, save_combined_csv, save_new_columns_csv


def main():
    """
    Entry point of the program. Configures logging, reads the CSV files in the root path and its subdirectories, and
    saves the combined data frame and new columns data frame to CSV files.

    Parameters:
    - None

    Returns:
    - None
    """
    logger = logging_config.configure_logging()  # Configure the logging
    root_path = r"I:\Shared drives\Data Analysis\Data\Bank Downloads 2022"
    try:
        read_csv_files(root_path)
        logging.info('Code ran successfully and without errors')  # Log a message if the code ran successfully
    except Exception as e:
        logging.exception(e)  # Log the exception if an error occurred


if __name__ == '__main__':
    main()
