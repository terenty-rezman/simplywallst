// init mongo db here

print("initializing db:", db)

const result = [
    db.companies.createIndex({ "ticker_symbol": 1 }, { unique: true })
]

printjson(result)