import json
import logging
import os
import shutil

import requests


def create_folder(folder_path: str) -> None:
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


def delete_folder(folder_path: str) -> None:
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


def check_folder_path(folder_path: str) -> str:
    """
    Add a slash at the end of the folder_path if it doesn't exist
    Parameters
    ----------
    folder_path : str
        Path of the folder

    Returns
    -------
    str
        folder_path ends with a slash
    """
    if not folder_path.endswith("/"):
        folder_path += "/"
    return folder_path


def write_to_json_file(file_path: str, content: object) -> None:
    """
    Write content as a json file to file_path
    Parameters
    ----------
    file_path : str
        Path of the file to store the json file
    content : object
        Content to be stored as a json file

    Returns
    -------

    """
    with open(file_path, "w") as file:
        json.dump(content, file, indent=4)


def write_request_response_to_file(file_path: str, response: requests.Response, chunk_size: int = 1024) -> None:
    """
    Write content as a json file to file_path
    Parameters
    ----------
    file_path : str
        Path of the file to store the json file
    response : requests.Response
        Response of a request
    chunk_size : int
        Chunk size

    Returns
    -------

    """
    with open(file_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                file.write(chunk)


def remove_slash_folder_path(folder_path: str) -> str:
    """
    Remove slash at the end of the folder_path
    Parameters
    ----------
    folder_path : str
        Path of the folder

    Returns
    -------
    str
        folder_path without slash at the end
    """
    if folder_path.endswith("/"):
        folder_path = folder_path[:-1]
    return folder_path
