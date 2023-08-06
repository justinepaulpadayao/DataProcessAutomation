# import necessary modules
from loguru import logger
from data_functions import read_csv_files, save_combined_csv, save_new_columns_csv


def main():
    """
    Entry point of the program. Configures logger, reads the CSV files in the root path and its subdirectories, and
    saves the combined data frame and new columns data frame to CSV files.

    Parameters:
    - None

    Returns:
    - None
    """
    logger.add("log_files/{time}_main.log", rotation="1 week", retention="1 month", level="INFO")
    root_path1 = r"G:\.shortcut-targets-by-id\1DcqaOLF_6OUJ0Ttaglh4tYvvqAcUZ0M5\Bank Downloads\2023\Daily"
    root_path2 = r"G:\.shortcut-targets-by-id\1DcqaOLF_6OUJ0Ttaglh4tYvvqAcUZ0M5\Bank Downloads\2023\Weekly BOW"
    try:
        logger.info(f"Reading CSV files in {root_path1} and its subdirectories...")
        read_csv_files(root_path1)
        logger.info(f"Reading CSV files in {root_path2} and its subdirectories...")
        read_csv_files(root_path2)
        logger.success('Code ran successfully and without errors')  # Log a message if the code ran successfully
    except Exception as e:
        logger.error(e)  # Log the exception if an error occurred


if __name__ == '__main__':
    main()
