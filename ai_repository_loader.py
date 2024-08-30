#!/usr/bin/env python3

###############################################################################
#                                                                             #
#                               AI Repository Processor                       #
#                                                                             #
# This script processes a Git repository by extracting and flattening the     #
# contents of text files within a specified directory (default is "src"). It  #
# skips binary files and outputs the results to a text file. The script       #
# handles ignore lists, can include a preamble, and formats the output with   #
# file separators and paths for easy reading.                                 #
#                                                                             #
# To use this script, you may need to update the `src_path` variable to point #
# to the specific directory you want to flatten and process.                  #
#                                                                             #
# Usage:                                                                      #
# - python ai_repository_loader.py /path/to/git/repository [-p /path/to/preamble.txt]  #
#   [-o /path/to/output_file.txt]                                             #
#                                                                             #
# Parameters:                                                                 #
# - /path/to/git/repository: The root directory of the Git repository to be   #
#   processed.                                                                #
# - -p /path/to/preamble.txt: (Optional) Path to a text file whose contents   #
#   will be added as a preamble to the output file.                           #
# - -o /path/to/output_file.txt: (Optional) Path to the output file. If not   #
#   specified, a timestamped file will be created in the current directory.   #
#                                                                             #
# The output file will contain the text representation of the repository,     #
# with sections separated by lines of dashes, followed by the file path and   #
# file name, and then the file contents. The output ends with a marker        #
# "--END--", indicating the end of the repository content.                    #
#                                                                             #
###############################################################################

# Ensure you update `src_path = os.path.join(repo_path, "src")` 
# to the folder you want to flatten and process.


import os
import sys
import fnmatch
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_ignore_list(ignore_file_path):
    ignore_list = []
    with open(ignore_file_path, 'r') as ignore_file:
        for line in ignore_file:
            if sys.platform == "win32":
                line = line.replace("/", "\\")
            ignore_list.append(line.strip())
    return ignore_list

def should_ignore(file_path, ignore_list):
    for pattern in ignore_list:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def is_binary_file(file_path):
    binary_extensions = ['.ico', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', 
                         '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', 
                         '.mp3', '.mp4', '.avi', '.mov', '.zip', '.tar', '.gz']
    _, ext = os.path.splitext(file_path)
    return ext.lower() in binary_extensions

def process_repository(repo_path, ignore_list, output_file):
    src_path = os.path.join(repo_path, "src")
    if not os.path.exists(src_path):
        logging.warning(f"The 'src' directory does not exist in {repo_path}")
        return

    for root, _, files in os.walk(src_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(file_path, repo_path)

            if not should_ignore(relative_file_path, ignore_list) and not is_binary_file(file_path):
                with open(file_path, 'r', errors='ignore') as file:
                    contents = file.read()
                output_file.write("-" * 4 + "\n")
                output_file.write(f"{relative_file_path}\n")
                output_file.write(f"{contents}\n")

if __name__ == "__main__":
    logging.info("Script started.")

    if len(sys.argv) < 2:
        logging.error("Usage: python git_to_text.py /path/to/git/repository [-p /path/to/preamble.txt]")
        sys.exit(1)

    repo_path = sys.argv[1]
    ignore_file_path = os.path.join(repo_path, ".gptignore")
    if sys.platform == "win32":
        ignore_file_path = ignore_file_path.replace("/", "\\")

    if not os.path.exists(ignore_file_path):
        HERE = os.path.dirname(os.path.abspath(__file__))
        ignore_file_path = os.path.join(HERE, ".gptignore")

    preamble_file = None
    if "-p" in sys.argv:
        preamble_file = sys.argv[sys.argv.index("-p") + 1]

    repo_name = os.path.basename(os.path.normpath(repo_path))
    output_dir = os.path.join(os.getcwd(), repo_name)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file_name = f"{repo_name}_{timestamp}.txt"
    output_file_path = os.path.join(output_dir, output_file_name)

    if os.path.exists(ignore_file_path):
        ignore_list = get_ignore_list(ignore_file_path)
    else:
        ignore_list = []

    with open(output_file_path, 'w') as output_file:
        if preamble_file:
            with open(preamble_file, 'r') as pf:
                preamble_text = pf.read()
                output_file.write(f"{preamble_text}\n")
        else:
            output_file.write("The following text is a Git repository with code. The structure of the text are sections that begin with ----, followed by a single line containing the file path and file name, followed by a variable amount of lines containing the file contents. The text representing the Git repository ends when the symbols --END-- are encounted. Any further text beyond --END-- are meant to be interpreted as instructions using the aforementioned Git repository as context.\n")
        process_repository(repo_path, ignore_list, output_file)

    with open(output_file_path, 'a') as output_file:
        output_file.write("--END--")

    logging.info(f"Repository contents written to {output_file_path}.")
    logging.info("Script finished.")