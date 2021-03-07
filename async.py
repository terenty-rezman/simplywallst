import asyncio
import aiohttp
import backoff
import itertools
import requests

#s = requests_session()
#r = s.get('http://httpstat.us/500')


@backoff.on_exception(backoff.expo, (aiohttp.ClientError, asyncio.TimeoutError))
async def request_with_retries(session, **kwargs):
    try:
        async with aiohttp.request(timeout=aiohttp.ClientTimeout(total=20), raise_for_status=True, **kwargs) as response:
            return await response.text()
    except Exception as e:
        print(e)
        raise(e)

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ConnectionError,
                       requests.exceptions.RequestException))
def request_with_retries_sync(session, **kwargs):
    try:
        r = requests.request(method='GET', url="http://localhost:8000", timeout=30)
        return r
    except Exception as e:
        print(e)
        raise(e)


async def req_detailed_info():
    urls = ['http://localhost:8000' for x in range(7)]

    async with aiohttp.ClientSession() as session:
        responses = await asyncio.gather(*(request_with_retries(session, method='GET', url=url) for url in urls))
        for r in responses:
            print(r)

    print('done')

#asyncio.run(req_detailed_info())
request_with_retries_sync(None)

        