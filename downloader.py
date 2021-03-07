import urllib
import pymongo
import requests
import time
import random
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

import asyncio
import aiohttp
import backoff

from progeress_bar import progress
from util import (n_at_a_time)


def requests_session():
    # inifinite request retries
    retry_strategy = Retry(
        total=None,
        backoff_factor=0.2,
        status_forcelist=[500, 502, 503, 504]
    )
    s = None #requests.Session()
    #s.mount('http://', HTTPAdapter(max_retries=retry_strategy))
    #s.mount('https://', HTTPAdapter(max_retries=retry_strategy))
    return s

#s = requests_session()
#r = s.get('http://httpstat.us/500')


@backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ConnectionError,
                       requests.exceptions.RequestException))
def request_with_retries_sync(session, **kwargs):
    try:
        r = requests.request(**kwargs, timeout=30)
        return r
    except Exception as e:
        print(e)
        raise(e)

def request_companies_count():
    url = "https://api.simplywall.st/api/grid/filter?include="
    body = {
        "id": "0",
        "no_result_if_limit": False,
        "offset": 0,
        "size": 1,
        "state": "read",
        "rules": "[[\"order_by\",\"market_cap\",\"desc\"],[\"value_score\",\">=\",0],[\"dividends_score\",\">=\",0],[\"future_performance_score\",\">=\",0],[\"health_score\",\">=\",0],[\"past_performance_score\",\">=\",0],[\"grid_visible_flag\",\"=\",true],[\"market_cap\",\"is_not_null\"],[\"primary_flag\",\"=\",true],[\"is_fund\",\"=\",false]]"
    }
    s = requests_session()
    #r = https.post(url, data=body)
    r = request_with_retries_sync(s, method='POST', url=url, data=body)
    return r.json()["meta"]["total_records"]


def requests_company_list_chunk(offset, size=24):
    url = "https://api.simplywall.st/api/grid/filter?include="
    body = {
        "id": "0",
        "no_result_if_limit": False,
        "offset": offset,
        "size": size,
        "state": "read",
        "rules": "[[\"order_by\",\"market_cap\",\"desc\"],[\"value_score\",\">=\",0],[\"dividends_score\",\">=\",0],[\"future_performance_score\",\">=\",0],[\"health_score\",\">=\",0],[\"past_performance_score\",\">=\",0],[\"grid_visible_flag\",\"=\",true],[\"market_cap\",\"is_not_null\"],[\"primary_flag\",\"=\",true],[\"is_fund\",\"=\",false]]"
    }
    s = requests_session()
    #r = https.post(url, data=body)
    r = request_with_retries_sync(s, method='POST', url=url, data=body)
    return r.json()["data"]

def request_company_detailed(canonical_url:str):
    base_url = "https://api.simplywall.st/api/company"
    include = [
        'info',
        'score',
        'analysis.extended.raw_data',
        'analysis.extended.raw_data.insider_transactions'
    ]
    params = {'include': ','.join(include), 'version': '2.0'}
    params = '?' + urllib.parse.urlencode(params)

    url = base_url + canonical_url + params

    s = requests_session()
    #r = https.get(url)
    r = request_with_retries_sync(s, method='GET', url=url)
    return r.json()["data"]


def companies():
    total_count = request_companies_count()
    total_count = 1000 * 24
    chunk_size = 24
    for i in range(0, total_count, chunk_size):
        for j, company in enumerate(requests_company_list_chunk(i, chunk_size)):
            total_i = i + j + 1
            progress(total_i, total_count, f'{total_i}/{total_count}')
            yield company

@backoff.on_exception(backoff.expo, (aiohttp.ClientError, asyncio.TimeoutError))
async def request_with_retries(session, **kwargs):
    try:
        async with aiohttp.request(timeout=aiohttp.ClientTimeout(total=20), raise_for_status=True, **kwargs) as response:
        #async with aiohttp.request(timeout=aiohttp.ClientTimeout(total=20), raise_for_status=True, method='GET', url="http://localhost:8000") as response:
            # if response.status not in (200, 429,):
            #     raise aiohttp.ClientResponseError()
            
            return await response.json()
    except Exception as e:
        print(e)
        raise(e)


async def request_company_detailed_async(session, canonical_url:str):
    base_url = "https://api.simplywall.st/api/company"
    include = [
        'info',
        'score',
        'analysis.extended.raw_data',
        'analysis.extended.raw_data.insider_transactions'
    ]
    params = {'include': ','.join(include), 'version': '2.0'}
    params = '?' + urllib.parse.urlencode(params)

    url = base_url + canonical_url + params

    json = await request_with_retries(session, method='GET', url=url)
    return json["data"]

async def request_multiple_companies_detailed(companies):
    try:
        timeout = aiohttp.ClientTimeout(total=60)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            tasks = []
            for company in companies:
                ticker = company["ticker_symbol"]
                ticker_in_db = db.companies.find_one({"ticker_symbol": ticker})
                if ticker_in_db is None:
                    canonical_url = company["canonical_url"]
                    tasks.append(
                        request_company_detailed_async(session, canonical_url)
                    )

            detailed_infos = await asyncio.gather(*tasks)
        
        for company_info in detailed_infos:
            db.companies.insert_one(company_info)
    except Exception as e:
        print(e)

    
if __name__ == "__main__":
    client = pymongo.MongoClient('localhost', 27017)
    db = client.simplywallst

    print("downloading...")

    # fill db with company info
    for n_companies in n_at_a_time(7, companies()):
        asyncio.run(request_multiple_companies_detailed(n_companies))
        time.sleep(random.randint(1, 3))

    print('\ndone')

