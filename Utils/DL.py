from aiohttp import ClientSession
from json import loads


class DL:
    def __init__(self, client):
        self.client = client

    @staticmethod
    async def async_post_json(url, data=None, headers=None):
        async with ClientSession(headers=headers) as session:
            async with session.post(url, data=data) as response:
                return await response.json()

    @staticmethod
    async def async_post_text(url, data=None, headers=None):
        async with ClientSession(headers=headers) as session:
            async with session.post(url, data=data) as response:
                res = await response.read()
                return res.decode("utf-8", "replace")

    @staticmethod
    async def async_post_bytes(url, data=None, headers=None):
        async with ClientSession(headers=headers) as session:
            async with session.post(url, data=data) as response:
                return await response.read()

    @staticmethod
    async def async_head_json(url, headers=None):
        async with ClientSession(headers=headers) as session:
            async with session.head(url) as response:
                return await response.json()

    @staticmethod
    async def async_dl(url, headers=None):
        # print("Attempting to download {}".format(url))
        total_size = 0
        data = b""
        async with ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                assert response.status == 200
                while True:
                    chunk = await response.content.read(4*1024)  # 4k
                    data += chunk
                    total_size += len(chunk)
                    if not chunk:
                        break
                    if total_size > 8000000:
                        # Too big...
                        # print("{}\n - Aborted - file too large.".format(url))
                        return None
        return data

    async def async_text(self, url, headers=None):
        data = await self.async_dl(url, headers)
        if data is not None:
            return data.decode("utf-8", "replace")
        else:
            return data

    async def async_json(self, url, headers=None):
        data = await self.async_dl(url, headers)
        if data is not None:
            return loads(data.decode("utf-8", "replace"))
        else:
            return data
