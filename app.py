import json
import cedears
from flask import Flask, request, jsonify, _request_ctx_stack
from flask_cors import cross_origin
from yahoo_fin.stock_info import *
from datetime import date, timedelta, datetime

app = Flask(__name__)

def get_name(ticker):
    for i in cedears.lista:
        if(i['ticker'] == ticker):
            return i['nombre']


def data_pandas_to_arrays(data_pandas):
    del data_pandas['ticker']

    data_json = data_pandas.to_json(orient='records')
    data_dict = json.loads(data_json)

    data_array = []

    for data in data_dict:
        data["date"] = int(data["date"])
        data["open"] = round(data["open"], 2)
        data["high"] = round(data["high"], 2)
        data["low"] = round(data["low"], 2)
        data["close"] = round(data["close"], 2)
        
        # item = [Timestamp, O, H, L, C]
        item = []
        
        item.append(data["date"])
        item.append(data["open"])
        item.append(data["high"])
        item.append(data["low"])
        item.append(data["close"])

        data_array.append(item)
    
    return data_array


@app.route('/api/live-price', methods=['GET'])
def get_price():
    ticker = request.args.get('ticker')

    live_price = get_live_price(ticker)

    return_json = {}
    return_json['ticker'] = ticker
    return_json['name'] = get_name(ticker)
    return_json['live-price'] = live_price

    return jsonify(return_json)


@app.route('/api/price-between', methods=['GET'])
def get_prices():
    ticker = request.args.get('ticker')
    # date params format: YYYY/MM/DD
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    data_pandas = get_data(ticker, start_date = start_date, end_date= end_date,
                index_as_date= False)

    del data_pandas['ticker']

    data_json = data_pandas.to_json(orient='records')
    data_dict = json.loads(data_json)

    for data in data_dict:
        data["date"] = datetime.utcfromtimestamp(data["date"]/1000).strftime('%Y/%m/%d')

    return_json = []
    return_json.append({'ticker': ticker, 'name': get_name(ticker)})
    return_json.append({'values': data_dict})
    return jsonify(return_json)


@app.route('/api/year-today-price', methods=['GET'])
def get_year_today_prices():
    ticker = request.args.get('ticker')
    # date params format: YYYY/MM/DD
    start_date = date.today() - timedelta(days=365)
    start_date = start_date.strftime("%Y/%m/%d")

    data_pandas = get_data(ticker, start_date = start_date, index_as_date= False)
 
    data_array = data_pandas_to_arrays(data_pandas)

    return_json = {}
    return_json['ticker'] = ticker
    return_json['name'] = get_name(ticker)
    return_json['data'] = data_array

    return jsonify(return_json)


@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    header['Access-Control-Allow-Methods'] = 'GET'
    return response


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
