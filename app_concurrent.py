import json
import time
import cedears
import asyncio
import requests
from timeit import default_timer
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, _request_ctx_stack
from flask_cors import cross_origin
from datetime import date, timedelta, datetime


app = Flask(__name__)


def get_name(ticker):
    for i in cedears.lista:
        if(i['ticker'] == ticker):
            return i['nombre']


async def fetch(ticker, session, data):
    url = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch"
    
    fetch.start_time[url] = default_timer()
    
    span_class = "Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"
    
    async with session.get(url) as response:
        r = await response.read()
        
        elapsed = default_timer() - fetch.start_time[url]
        
        print(f"{url}   took {elapsed}")
        
        r = BeautifulSoup(r, "html.parser")
        
        cotizacion = r.find_all("span", class_= span_class)
        cotizacion = cotizacion[0].get_text()
        
        row = {}
        row['ticker'] = ticker
        row['cotizacion'] = cotizacion
        
        data.append(row)
        
        return r


async def fetch_all(tickers, data):
    tasks = []
    
    fetch.start_time = dict() 
    
    async with ClientSession() as session:
        for ticker in tickers:
            task = asyncio.ensure_future(fetch(ticker, session, data))
            tasks.append(task) 
        _ = await asyncio.gather(*tasks)


def get_live_price_all_concurrent():
    start_time = default_timer()
    
    tickers = []
    
    for i in cedears.lista:
        tickers.append(i['ticker'])
    
    data = []

    asyncio.set_event_loop(asyncio.new_event_loop())
    
    loop = asyncio.get_event_loop() 
    
    future = asyncio.ensure_future(fetch_all(tickers, data)) 
    
    loop.run_until_complete(future) 

    tot_elapsed = default_timer() - start_time
    
    print(f"Total time taken: {tot_elapsed}")

    return data


@app.route('/api/live-price/all', methods=['GET'])
def get_all_assets_prices():

    return_json = get_live_price_all_concurrent()

    print(return_json)

    return jsonify(return_json)


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    header['Access-Control-Allow-Methods'] = 'GET'
    return response

# https://realpython.com/async-io-python/#async-io-explained
# https://medium.com/@ProxiesAPI.com/synchronous-web-scraping-v-s-asynchronous-web-scraping-with-python-a9ee77aa51c4
if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)
