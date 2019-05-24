import os
from urllib.parse import urlparse

import requests
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from requests.exceptions import RequestException
from contextlib import closing
import json


class ImportException(Exception):
    def __init__(self, msg, cause=None):
        if cause:
            super().__init__(f'{msg}: {cause}')
        else:
            super().__init__(msg)
        self.cause = cause


def is_200(response):
    return response.status_code == 200


def get_filename(resp):
    content_disposition = resp.headers.get('content-disposition', None)
    if content_disposition:
        for disposition in content_disposition.split(';'):
            disposition = disposition.strip()
            key = 'filename'
            if disposition[0:len(key) + 1] == f'{key}=':
                return disposition[len(key) + 1:].strip()
    url = urlparse(resp.url)
    path = url.path
    return os.path.basename(path)


def decode_content_if_text(resp):
    content_type = resp.headers['content-type']  # type: str
    if any((text_type in content_type for text_type in ['application/json', 'text/html', 'charset=utf-8'])):
        return resp.content.decode('utf-8')
    if content_type.startswith('image/'):
        return SimpleUploadedFile(get_filename(resp), resp.content, content_type)
    return resp.content


def http_get(url, headers=None, params=None):
    try:
        with closing(requests.get(url, params=params, stream=True, headers=headers)) as resp:
            if not is_200(resp):
                raise ImportException(f'Could not fetch url: {url}')
            return decode_content_if_text(resp)
    except RequestException as e:
        raise ImportException(f'Could not fetch url: {url}', e)


def get_json(url, **kwargs):
    headers = kwargs.pop('headers', {})
    headers['Accept'] = 'application/json'
    raw_json = http_get(url, headers=headers, **kwargs)
    return json.loads(raw_json)


def levenshtein(s1, s2):
    """
    From https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
    License: https://creativecommons.org/licenses/by-sa/3.0/
    :param str s1:
    :param str s2:
    :return int:
    """
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # j+1 instead of j since previous_row and current_row are one character longer
            insertions = previous_row[j + 1] + 1
            # than s2
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def bytes_to_file(bytes, file):
    with open(file, 'wb+') as dest:
        chunk_size = 4096
        for i in range(0, len(bytes), chunk_size):
            dest.write(bytes[i:i + chunk_size])
    return File(file)
