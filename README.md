__downloader.py__ 

is a downloading script
which retrieves data from `https://api.simplywall.st` in following steps:
1) retreives company list size
2) retreives company list in chunks
3) downloads detailed per company info in json format using company list<br />
   example data that gets stored can be seen at:<br />
   <https://api.simplywall.st/api/company/stocks/us/tech/nasdaq-aapl/apple?include=info,score%2Cscore%2Canalysis.extended.raw_data%2Canalysis.extended.raw_data.insider_transactions&version=2.0>
2) stores retrieved jsons 'as is' into `mongodb`

to run `downloader.py` use:
```
$ source venv/bin/activate
$ python3 downloader.py
```

__server.py__ 

is a flask web app<br />
which serves data downloaded with `downloader.py`

to run the server use: 
```
$ ./run_server.sh
```

after that downloaded data will be available at `http://127.0.0.1:5000/simplywallst/XXXX` <br />
where 'XXXX' is the ticker symbol for a company <br />

example:
```
http://127.0.0.1:5000/simplywallst/AAPL
```

__./mongodb/docker-compose.yml__

contains config to run `mongodb` in a docker container with docker volume mounted to `./mongodb/database/` to store database files
