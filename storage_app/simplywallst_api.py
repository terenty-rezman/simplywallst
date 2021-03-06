from flask import (Blueprint, request, abort, send_file, redirect)

from storage_app import db as database
from helpers.util import safe_parse_int

bp = Blueprint("storage", __name__, url_prefix="/simplywallst")

@bp.route('/<ticker>', methods=('GET',))
def get_company_info(ticker):
    # some of the ticker symbols are ints in simplywallst db
    ticker_int = safe_parse_int(ticker)
    ticker = ticker_int if ticker_int is not None else ticker

    db = database.get_db()
    db = db.simplywallst

    # {"_id": 0} removes mongodb "_id" property from result
    company_info = db.companies.find_one({"ticker_symbol": ticker}, {"_id": 0})

    if company_info is None:
        abort(404)
    
    return company_info