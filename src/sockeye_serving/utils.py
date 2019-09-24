import re
import subprocess

from typing import Dict


def create_request(input: str) -> Dict:
    return {'text': input}


def decode_bytes(data: bytearray) -> str:
    """
    Decodes a bytes array from a file upload

    :param data: a UTF-8 encoded byte array
    :return: a cleaned string
    """
    pattern = re.compile('\r', re.UNICODE)
    res = data.decode('utf-8', 'ignore')
    res = pattern.sub('', res)
    return res


def get_request(req: Dict) -> Dict:
    """
    Returns the text string, if any, in the request

    :param req: a JSON request
    :return: a text string
    """
    for field in ['body']:
        if field in req:
            data = req[field]
            if isinstance(data, str):
                return create_request(data)
            elif isinstance(data, dict) and 'text' in data:
                return data
    return None


def get_file_data(req: Dict) -> bytearray:
    """
    Returns the file data, if any, in the request

    :param req: a JSON request
    :return: a byte array
    """
    for field in ['body', 'file', 'data']:
        if field in req:
            data = req[field]
            if isinstance(data, bytearray):
                return data
    return None


def read_sockeye_args(params_path):
    """
    Reads command line arguments stored in a file

    :param params_path: path to the parameters file
    :return: a list of command line arguments
    """
    with open(params_path) as f:
        content = f.readlines()

    res = []
    for line in content:
        res += line.split()
    return res


def run_subprocess(text, args):
    """
    Runs a subprocess that processes text
    :param text: input text
    :param args: command line arguments
    :return: processed text
    """
    proc = subprocess.run(
        args,
        input=text,
        encoding='utf-8',
        stdout=subprocess.PIPE)
    return proc.stdout.strip()
