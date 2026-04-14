# Description: Copy a random X% of files from a folder to a new folder.
# Usage: python select_subset.py <source_folder> <destination_folder>

import argparse
import os
import random
import shutil


def parse_arguments():
    parser = argparse.ArgumentParser(description="Copy a random 20% of files from a folder to a new folder.")
    parser.add_argument("source_folder", help="Path to the source folder")
    parser.add_argument("destination_folder", help="Path to the destination folder")
    return parser.parse_args()


def select_random_files(source_folder, destination_folder, percentage=0.2):
    """
    Selects a random subset of files from a source folder and copies them to a destination folder.

    Parameters:
    - source_folder (str): The path to the source folder containing the files.
    - destination_folder (str): The path to the destination folder where the selected files will be copied.
    - percentage (float): The percentage of files to select from the source folder. Default is 0.2 (20%).

    Example usage:
    select_random_files('/path/to/source_folder', '/path/to/destination_folder', 0.3)
    """
    # List all files in the source folder
    file_list = os.listdir(source_folder)

    # Calculate the number of files to select (percentage)
    num_files_to_select = int(len(file_list) * percentage)
    print("{:d} = {:d} * {:f}".format(num_files_to_select, len(file_list), percentage))

    # Select files randomly
    selected_files = random.sample(file_list, num_files_to_select)

    # Copy the selected files to the destination folder
    for file in selected_files:
        source_path = os.path.join(source_folder, file)
        destination_path = os.path.join(destination_folder, file)
        shutil.copy(source_path, destination_path)


def main():
    args = parse_arguments()

    source_folder = args.source_folder
    destination_folder = args.destination_folder

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    select_random_files(source_folder, destination_folder)
    print("{} files copied to {}".format(len(os.listdir(destination_folder)), destination_folder))


if __name__ == "__main__":
    main()
