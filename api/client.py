import asyncio
import json
from functools import lru_cache
from json.decoder import JSONDecodeError

import aiohttp
from aiohttp import ClientSession, TCPConnector
from aiohttp.client_exceptions import ClientConnectorError
from starlette import status

from api.configurations.base import config
from api.exceptions.responses import HTTPException


@lru_cache()
def get_api_client():
    return AiohttpClient()


class AiohttpClient():
    def __init__(self):
        self.sem = asyncio.Semaphore(1000)
        self.session: aiohttp.ClientSession = None

    def get_session(self):
        if self.session is None:
            self.session = ClientSession(connector=TCPConnector(ssl=False))
            config.logger.info("Client session created")

    async def close_session(self):
        if hasattr(self, 'session'):
            await self.session.close()
            config.logger.info('Client session closed')
            self.aiohttp_client = None
        return

    async def call_url(self, method='GET', url='', headers=None, fetch=True):
        self.get_session()
        if not headers:
            headers = {}
        if fetch:
            return await self.fetch(method, url)
        else:
            return self.fetch(method, url)

    async def gather_urls(self, method, urls, return_exceptions=False, **kwargs):
        tasks = []
        self.get_session()

        for url in urls:
            task = asyncio.ensure_future(self.fetch(method, url))
            tasks.append(task)

        responses = asyncio.gather(*tasks, return_exceptions=return_exceptions)
        return await responses

    async def fetch(self, method, url):
        self.get_session()
        async with self.sem:
            try:
                response = await self.session.get(url)
            except ClientConnectorError as e:
                config.logger.error(str(e))
                raise HTTPException(url=url, message=str(e), status=status.HTTP_400_BAD_REQUEST)

            resp = await response.read()
            try:
                response = json.loads(resp) or {}
                message = f'url: {url}, status: {status.HTTP_200_OK}'
                config.logger.info(message)
            except JSONDecodeError as e:
                error_message = str(e) + ', ' + e.doc
                config.logger.error(
                    f'url: {url}, response: {str(resp)}, message: {error_message}, status: {response.status}')
                raise HTTPException(url=url, response=str(resp), message=error_message, status=response.status)
            return response

    # TODO: check for these events
    async def on_startup(self):
        self.get_session()

    async def on_shutdown(self):
        await self.close_session()
