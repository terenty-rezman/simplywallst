from types import SimpleNamespace
import pymongo
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# inifinite request retries
def requests_session():
    retry_strategy = Retry(
        total=None,
        backoff_factor=0.2,
        status_forcelist=[500, 502, 503, 504]
    )
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=retry_strategy))
    s.mount('https://', HTTPAdapter(max_retries=retry_strategy))
    return s

s = requests_session()
r = s.get('http://httpstat.us/500')


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


companies_count = request_companies_count()
print(companies_count)

client = pymongo.MongoClient('localhost', 27017)
db = client.simplywallst

# general info collection
company_general = db.company_general
