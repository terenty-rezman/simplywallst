import urllib
import time
import random
import datetime

import requests
import pymongo
import asyncio
import aiohttp
import backoff

from helpers.progress_bar import progress
from helpers.util import (n_at_a_time, human_delta)
from helpers.util import timestamp_print as print


@backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ConnectionError,
                       requests.exceptions.RequestException))
def request_with_retries_sync(**kwargs):
    try:
        r = requests.request(**kwargs, timeout=30)
        r.raise_for_status()
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
    r = request_with_retries_sync(method='POST', url=url, data=body)
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
    r = request_with_retries_sync(method='POST', url=url, data=body)
    return r.json()["data"]


def companies():
    total_count = request_companies_count()
    print("total companies count:", total_count)
    chunk_size = 24
    start_time = datetime.datetime.now()
    for i in range(0, total_count, chunk_size):
        for j, company in enumerate(requests_company_list_chunk(i, chunk_size)):
            total_i = i + j + 1
            now = datetime.datetime.now()
            elapsed = human_delta(now - start_time)
            progress(total_i, total_count,
                     f'{total_i}/{total_count} elapsed {elapsed}')
            yield company


def no_retry_code(e):
    # dont retry request if 404 received
    if isinstance(e, aiohttp.ClientResponseError):
        return e.status == 404


@backoff.on_exception(backoff.expo, (aiohttp.ClientError, asyncio.TimeoutError), giveup=no_retry_code)
async def request_with_retries(**kwargs):
    try:
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.request(timeout=timeout, raise_for_status=True, **kwargs) as response:
            return await response.json()
    except Exception as e:
        print(e)
        raise(e)


async def request_company_detailed_async(canonical_url: str):
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

    try:
        json = await request_with_retries(method='GET', url=url)
    except aiohttp.ClientResponseError as e:
        # request is allowed to fail when 404 received
        return None

    return json["data"]


async def request_multiple_companies_detailed(companies):
    # check if companies already in db
    tickers_to_check = [
        {"ticker_symbol": company["ticker_symbol"]} for company in companies
    ]

    # single request to db
    companies_in_db = db.companies.find(
        {"$or": tickers_to_check},
        {"ticker_symbol": 1, "_id": 0}  # return only "ticker_symbol"
    )

    # put tickers in a set
    tickers_in_db = {company["ticker_symbol"] for company in companies_in_db}

    companies_not_in_db = (
        company for company in companies if company["ticker_symbol"] not in tickers_in_db
    )

    # only download data for companies that are NOT in db already
    tasks = []
    for company in companies_not_in_db:
        canonical_url = company["canonical_url"]
        tasks.append(
            request_company_detailed_async(canonical_url)
        )

    results = await asyncio.gather(*tasks)

    # some request are allowed to fail and return None
    results = [item for item in results if item is not None]

    if results:
        db.companies.insert_many(results)

    made_requests = True if tasks else False
    return made_requests


if __name__ == "__main__":
    client = pymongo.MongoClient('localhost', 27017)
    db = client.simplywallst

    print("downloading...")

    # fill db with company info
    concurrent_requests = 7
    for n_companies in n_at_a_time(concurrent_requests, companies()):
        need_sleep = asyncio.run(
            request_multiple_companies_detailed(n_companies))
        # random sleep to relieve stress on api
        if need_sleep:
            time.sleep(random.randint(1, 3))
        else:
            time.sleep(1)

    print('\ndone')
