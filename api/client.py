import asyncio
import json

import aiohttp
from aiohttp import ClientSession, TCPConnector
from fastapi import Response
from starlette import status

from configs.logging import logger


class AiohttpClient():
    def __init__(self):
        self.sem = asyncio.Semaphore(1000)
        self.session: aiohttp.ClientSession = None

    def get_session(self):
        if self.session is None:
            self.session = ClientSession(connector=TCPConnector(ssl=False))
            logger.info("Client session created")

    async def close_session(self):
        if hasattr(self, 'session'):
            await self.session.close()
            logger.info('Client session closed')
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

    async def gather_urls(self, method, urls, **kwargs):
        tasks = []
        self.get_session()

        for url in urls:
            task = asyncio.ensure_future(self.fetch(method, url))
            tasks.append(task)

        responses = asyncio.gather(*tasks)
        return await responses

    async def fetch(self, method, url):
        self.get_session()
        response = Response(content=f"No Data", status_code=status.HTTP_400_BAD_REQUEST)
        async with self.sem:
            try:
                response = await self.session.get(url)
            except Exception as e:
                logger.error(e)
                response = Response(content=f"Error fetching from URL {url}. {e}",
                                    status_code=status.HTTP_400_BAD_REQUEST)
                return response

            resp = await response.read()
            try:
                response = json.loads(resp)
                logger.info({"called_url": url, "status": status.HTTP_200_OK})
            except Exception:
                response = Response(content=resp, status_code=status.HTTP_400_BAD_REQUEST)
                logger.error({"url": url, "status": response.status})
            return response

    # TODO: check for these events
    async def on_startup(self):
        self.get_session()

    async def on_shutdown(self):
        await self.close_session()
