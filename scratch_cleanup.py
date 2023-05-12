#!/nfs/dhcommon/dhhadoop/python3/bin/python3

# Import required python libraries
import os
import sys
import time

path = '/nfs/science/shared/www/html/science-env/scratch_area/UKWatford2'
number_of_days = 10
#----------------------------------------------------------------------
def remove(path):
    """
    Remove the file or directory
    """
    if os.path.isdir(path):
        try:
            os.rmdir(path)
        except OSError:
            print ("Unable to remove folder: %s" % path)
    else:
        try:
            if os.path.exists(path):
                os.remove(path)
        except OSError:
            print ("Unable to remove file: %s" % path)
#----------------------------------------------------------------------
def cleanup(number_of_days, path):
    """
    Removes files from the passed in path that are older than or equal
    to the number_of_days
    """
    time_in_secs = time.time() - (number_of_days * 24 * 60 * 60)
    for root, dirs, files in os.walk(path, topdown=False):
        for file_ in files:
            full_path = os.path.join(root, file_)
            stat = os.stat(full_path)

            if stat.st_mtime <= time_in_secs:
                remove(full_path)

#----------------------------------------------------------------------
if __name__ == "__main__":
    cleanup(number_of_days, path)
