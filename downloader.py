import urllib
import pymongo
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from progeress_bar import progress


def requests_session():
    # inifinite request retries
    retry_strategy = Retry(
        total=None,
        backoff_factor=0.2,
        status_forcelist=[500, 502, 503, 504]
    )
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=retry_strategy))
    s.mount('https://', HTTPAdapter(max_retries=retry_strategy))
    return s

#s = requests_session()
#r = s.get('http://httpstat.us/500')

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
    https = requests_session()
    r = https.post(url, data=body)
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
    https = requests_session()
    r = https.post(url, data=body)
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

    https = requests_session()
    r = https.get(url)
    return r.json()["data"]


def companies():
    total_count = request_companies_count()
    total_count = 48
    chunk_size = 24
    for i in range(0, total_count, chunk_size):
        for j, company in enumerate(requests_company_list_chunk(i, chunk_size)):
            total_i = i + j + 1
            progress(total_i, total_count, f'{total_i}/{total_count}')
            yield company

if __name__ == "__main__":
    client = pymongo.MongoClient('localhost', 27017)
    db = client.simplywallst

    print("downloading...")

    # fill db with company info
    for company in companies():
        ticker = company["ticker_symbol"]
        ticker_in_db = db.companies.find_one({"ticker_symbol": ticker})
        if ticker_in_db is None:
            canonical_url = company["canonical_url"]
            company_info = request_company_detailed(canonical_url)
            db.companies.insert_one(company_info)

print('\ndone')

