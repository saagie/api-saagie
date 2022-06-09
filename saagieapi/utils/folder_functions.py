import logging
import os
import shutil


def create_folder(folder_path):
    """
    Create the folder
    Parameters
    ----------
    folder_path : str
        Path of the folder

    Returns
    -------

    """
    is_exist = os.path.exists(folder_path)
    if not is_exist:
        logging.info(f"Creating folder: '{folder_path}'")
        os.makedirs(folder_path)


def delete_folder(folder_path):
    """
    Delete the folder recursively
    Parameters
    ----------
    folder_path : str
        Path of the folder

    Returns
    -------

    """
    logging.info(f"Deleting folder: '{folder_path}'")
    shutil.rmtree(folder_path)
