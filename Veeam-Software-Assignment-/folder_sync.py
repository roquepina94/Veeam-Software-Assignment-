import os
import shutil
import argparse
import time
import hashlib

# Function to compute the MD5 hash of a given file
def get_md5(file_path):
    """Compute the MD5 hash of the file at the specified path."""
    # Initialize the MD5 hasher
    hasher = hashlib.md5()
    
    # Open the file in binary read mode
    with open(file_path, 'rb') as afile:
        # Read the file.
        buf = afile.read()
        
        # Update the MD5 hasher with the file content
        hasher.update(buf)
        
    # Return the hexadecimal representation of the hash
    return hasher.hexdigest()

# Function to synchronize content between source and replica folders
def synchronize(src_folder, replica_folder):
    """Synchronize the content of src_folder to replica_folder."""
    # Iterate over all items in the source folder
    for item in os.listdir(src_folder):
        src_path = os.path.join(src_folder, item)
        replica_path = os.path.join(replica_folder, item)
        
        # If the item is a directory, create the directory in replica 
        # (if it doesn't exist) and recursively synchronize its content
        if os.path.isdir(src_path):
            if not os.path.exists(replica_path):
                os.makedirs(replica_path)
            synchronize(src_path, replica_path)
            
        # If the item is a file and it either doesn't exist in replica or has different content,
        # copy it from source to replica
        elif os.path.isfile(src_path):
            if not os.path.exists(replica_path) or get_md5(src_path) != get_md5(replica_path):
                shutil.copy2(src_path, replica_path)
                log(f'File copied/overwritten: {src_path} -> {replica_path}')
                
    # Remove items in replica that don't exist in source
    for item in os.listdir(replica_folder):
        replica_path = os.path.join(replica_folder, item)
        src_path = os.path.join(src_folder, item)
        if not os.path.exists(src_path):
            if os.path.isfile(replica_path):
                os.remove(replica_path)
                log(f'File removed: {replica_path}')
            else:
                shutil.rmtree(replica_path)
                log(f'Empty folder removed: {replica_path}')

# Function to log messages to the console and log file
def log(message):
    """Log the provided message to the console and to the log file."""
    print(message)
    try:
        with open(log_file_path, 'a') as log_file:
            log_file.write(message + '\n')
    except PermissionError:
        print(f"Error: Couldn't write to log file at {log_file_path}. Please check permissions or path.")
    except Exception as e:
        print(f"Unexpected error while logging: {e}")

if __name__ == '__main__':
    # Argument parsing for command line input
    parser = argparse.ArgumentParser(description='Synchronize folders.')
    parser.add_argument('src_folder', help='Source folder path')
    parser.add_argument('replica_folder', help='Replica folder path')
    parser.add_argument('sync_interval', type=int, help='Synchronization interval in seconds')
    parser.add_argument('log_file', help='Log file path')
    
    args = parser.parse_args()
    
    # Assigning parsed arguments to variables
    src_folder = args.src_folder
    replica_folder = args.replica_folder
    sync_interval = args.sync_interval
    log_file_path = args.log_file

    # Initial checks before starting synchronization loop
    if not os.path.exists(src_folder):
        print(f"Source folder '{src_folder}' does not exist!")
        exit(1)
    
    if not os.path.exists(replica_folder):
        os.makedirs(replica_folder)

    # Infinite loop to keep synchronizing at specified intervals
    while True:
        synchronize(src_folder, replica_folder)
        time.sleep(sync_interval)

