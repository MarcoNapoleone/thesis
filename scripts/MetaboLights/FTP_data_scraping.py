from ftplib import FTP
from humanize import naturalsize
from tqdm import tqdm  # Importa la libreria tqdm per la progress bar
import pandas as pd
from io import BytesIO

NUMBER_OF_DIRECTORY = 10


# Function to list files in the current directory of the FTP server
def list_files(ftp):
    file_list = []
    ftp.retrlines('LIST', file_list.append)
    return file_list


# Function to find the largest n files with specific extensions, method can be "FILE_SIZE" or "SHEET_COLUMNS"
def find_largest_files(ftp, extensions, n=NUMBER_OF_DIRECTORY, method="FILE_SIZE"):

    file_list = list_files(ftp)

    # Filter files by extensions
    filtered_files = [name for name in file_list if name.lower().endswith(extensions)]

    if method == "FILE_SIZE":
        # Sort files by size in descending order
        filtered_files.sort(key=lambda x: int(x.split()[4]), reverse=True)

        # Keep only the top n the largest files
        top_n_files = filtered_files[:n]

        return top_n_files

    elif method == "SHEET_COLUMNS":
        # Initialize a list to store file information including column count
        file_info_list = []

        # Loop through the filtered files and get their column count
        for file_name in filtered_files:
            try:
                # Download the file to a BytesIO object
                with BytesIO() as file_buffer:
                    ftp.retrbinary("RETR " + file_name, file_buffer.write)
                    file_buffer.seek(0)

                    # Switch file extension to read with pandas


                    # Read the file with pandas to count columns
                    df = pd.read_csv(file_buffer)
                    column_count = df.shape[1]

                    # Add file information to the list
                    file_info_list.append((file_name, column_count))

            except Exception as e:
                # Handle the exception (e.g., print an error message)
                print(f"Error processing file {file_name}: {e}")

        # Sort files by column count in descending order
        file_info_list.sort(key=lambda x: x[1], reverse=True)

        # Keep only the top n files with the most columns
        top_n_files = [file_info[0] for file_info in file_info_list[:n]]

        return top_n_files

    elif method == "SHEET_ROWS":
        # Initialize a list to store file information including column count
        file_info_list = []

        # Loop through the filtered files and get their column count
        for file_name in filtered_files:
            try:
                # Download the file to a BytesIO object
                with BytesIO() as file_buffer:
                    ftp.retrbinary("RETR " + file_name, file_buffer.write)
                    file_buffer.seek(0)

                    # Read the file with pandas to count columns
                    df = pd.read_csv(file_buffer)
                    row_count = df.shape[0]

                    # Add file information to the list
                    file_info_list.append((file_name, row_count))

            except Exception as e:
                # Handle the exception (e.g., print an error message)
                print(f"Error processing file {file_name}: {e}")

        # Sort files by column count in descending order
        file_info_list.sort(key=lambda x: x[1], reverse=True)

        # Keep only the top n files with the most columns
        top_n_files = [file_info[0] for file_info in file_info_list[:n]]

        return top_n_files


# Connect to the FTP server
server = "ftp.ebi.ac.uk"
base_folder = "/pub/databases/metabolights/studies/public/"

# Define the extensions to search for
extensions_to_search = (".csv")  #(".tsv", ".csv", ".xlsx")

with FTP(server) as ftp:
    ftp.login()
    ftp.cwd(base_folder)

    print(f"Connected to {server} successfully!")

    # List subdirectories in the current directory of the FTP server using NLST
    subdirectories = ftp.nlst()

    print(f"Total number of subdirectories: {len(subdirectories)}")

    # Initialize a dictionary to store folder names as key with the largest files as values
    folders_with_largest_files = {}

    # Initialize a dictionary to store file name as key with a tuple of folder name and file size as values
    files_with_folder_names = {}

    # Total files scraped
    total_files_scraped = 0

    # Initialize tqdm for progress bar
    progress_bar = tqdm(total=len(subdirectories), desc="Progress", unit="folder")

    # Loop through the subdirectories
    for subdirectory in subdirectories:
        try:
            # Change directory to the current subdirectory
            ftp.cwd(subdirectory)

            # Find the largest files in the current subdirectory
            largest_files = find_largest_files(ftp, extensions_to_search, method="SHEET_COLUMNS")

            # Update the total files scraped
            total_files_scraped += len(largest_files)

            # Update the dictionary
            for file in largest_files:
                files_with_folder_names[file] = (subdirectory, file.split()[4])

            # Return to the parent directory
            ftp.cwd('..')

        except Exception as e:
            # Handle the exception (e.g., print an error message)
            print(f"Error accessing subdirectory {subdirectory}: {e}")

        finally:
            # Update the progress bar with current folder and total files scraped
            progress_bar.set_description_str(
                f"Current Folder: {subdirectory} | Total Files Scraped: {total_files_scraped}")
            progress_bar.update(1)

    # Close the progress bar
    progress_bar.close()

    # Fiter the n largest elements in the dictionary by file size
    files_with_folder_names = dict(
        sorted(files_with_folder_names.items(), key=lambda x: int(x[1][1]), reverse=True)[:NUMBER_OF_DIRECTORY])

    # transponder the dictionary to have the folder as key and the files as values
    for file in files_with_folder_names:
        if files_with_folder_names[file][0] not in folders_with_largest_files:
            folders_with_largest_files[files_with_folder_names[file][0]] = [file]
        else:
            folders_with_largest_files[files_with_folder_names[file][0]].append(file)

    # Print the folder names with the largest files and the relative files
    print("Folders with the largest files:")
    print("=====================================")
    print(base_folder)
    for folder in folders_with_largest_files:
        print()
        print(f"{folder}")
        for file in folders_with_largest_files[folder]:
            print(f"    |")
            # print file and size in human-readable format
            print(f"    |---> {file.split()[8]} ({naturalsize(file.split()[4])} bytes)")
