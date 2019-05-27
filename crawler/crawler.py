import requests
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


class BatchCrawler(object):
    PARALLEL_JOBS = 5
    client = None

    def __init__(self):
        self.jobs = []
        self.running = []

    def _crawl_single(self, job):
        return type(self)().crawl_single(job)

    async def crawl_single(self, job):
        raise NotImplementedError()

    def get_result(self):
        raise NotImplementedError()

    async def _crawl_all(self):
        import aiohttp
        import asyncio

        BatchCrawler.client = aiohttp.ClientSession()

        while len(self.jobs) > 0:
            # create and launch a new task
            next_job = self.jobs.pop(0)
            next_task = asyncio.create_task(self._crawl_single(next_job))
            self.running.append(next_task)

            # if the queue is full, wait for a task to complete:
            if len(self.running) >= self.PARALLEL_JOBS:
                _, pending = await asyncio.wait(self.running, return_when=asyncio.FIRST_COMPLETED)
                self.running = list(pending)  # hold on to the rest

        # finalize
        await asyncio.gather(*self.running)
        await self.client.close()

    def crawl_all(self, jobs):
        import asyncio

        self.jobs = list(jobs)
        self.running.clear()
        asyncio.run(self._crawl_all())

        return self.get_result()

    async def http_get(self, url, headers=None, params=None):
        import aiohttp.http_exceptions

        try:
            resp = await self.client.get(url, headers=headers, params=params)
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ) as e:
            raise ImportException(f'Could not fetch url: {url}, reason: {str(e)}', e)
        if not resp.status == 200:
            raise ImportException(f'Could not fetch url: {url}', resp.status)
        return await self.decode_content(resp)

    async def get_json(self, url, **kwargs):
        headers = kwargs.pop('headers', {})
        headers['Accept'] = 'application/json'
        raw_json = await self.http_get(url, headers=headers, **kwargs)
        return json.loads(raw_json)

    async def decode_content(self, resp):
        content_type = resp.headers['content-type']  # type: str
        if any((text_type in content_type for text_type in ['application/json', 'text/html', 'charset=utf-8'])):
            return await resp.text()
        if content_type.startswith('image/'):
            return SimpleUploadedFile(get_filename(resp), await resp.read(), content_type)
        return await resp.read()

    def prepend_job(self, job):
        self.jobs.insert(0, job)

    def append_job(self, job):
        self.jobs.append(job)


def get_filename(resp):
    content_disposition = resp.headers.get('content-disposition', None)
    if content_disposition:
        for disposition in content_disposition.split(';'):
            disposition = disposition.strip()
            key = 'filename'
            if disposition[0:len(key) + 1] == f'{key}=':
                return disposition[len(key) + 1:].strip()
    return resp.url.name


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
            if not resp.status_code == 200:
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
