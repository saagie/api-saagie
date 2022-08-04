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
        logging.info("Creating folder: '%s'", folder_path)
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
    logging.info("Deleting folder: '%s'", folder_path)
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
    with open(file_path, "w", encoding="utf-8") as file:
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


def write_string_to_file(file_path: str, content: str) -> None:
    """
    Write the content in the file. If the file is not empty, append the content in the file
    Parameters
    ----------
    file_path : str
        Path of the file
    content : str
        Content to be stored in the file

    Returns
    -------

    """
    file_exist = os.path.exists(file_path)
    if file_exist:
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(f"{content}\n")
        else:
            with open(file_path, "a", encoding="utf-8") as file:
                file.write(f"{content}\n")
    else:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"{content}\n")


def write_error(error_folder, element, error_content):
    """
    Write the error content in a file inside the sub folder of error_folder.
    Parameters
    ----------
    error_folder : str
        Path of the error file
    element : str
        Specify the sub folder of the error folder to store the error file
        Should be 'apps', 'env_vars', 'jobs', 'pipelines'
    error_content : str
        Content to be stored in the file

    Returns
    -------

    """
    if error_folder:
        error_folder = check_folder_path(error_folder) + f"{element}/"
        create_folder(error_folder)
        error_file_path = error_folder + f"{element}_error.txt"
        write_string_to_file(error_file_path, error_content)
