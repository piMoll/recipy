import requests
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


class Handler(object):
    def __init__(self, crawler_input):
        """
        :param crawler_input: str 
        """
        self.input = crawler_input

    @staticmethod
    def is_200(response):
        return response.status_code == 200

    def http_get(self, url, headers=None, params=None):
        try:
            with closing(requests.get(url, params=params, stream=True, headers=headers)) as resp:
                if not self.is_200(resp):
                    raise ImportException(f'Could not fetch url for input "{self.input}": {url}')
                return resp.content.decode('utf-8')
        except RequestException as e:
            raise ImportException(f'Could not fetch url for input "{self.input}": {url}', e)

    def get_json(self, url, **kwargs):
        headers = kwargs.pop('headers', {})
        headers['Accept'] = 'application/json'
        raw_json = self.http_get(url, headers=headers, **kwargs)
        return json.loads(raw_json)

    @classmethod
    def levenshtein(cls, s1, s2):
        """
        From https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
        License: https://creativecommons.org/licenses/by-sa/3.0/
        :param s1:
        :param s2:
        :return:
        """
        if len(s1) < len(s2):
            return cls.levenshtein(s2, s1)

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
