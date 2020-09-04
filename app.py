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


@app.route('/api/live-price', methods=['GET'])
@cross_origin(headers=["Access-Control-Allow-Origin", "*"])
def getLivePrice():
    ticker = request.args.get('ticker')
    # date params format: YYYY/MM/DD
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    data_pandas = get_data(ticker, start_date = start_date, end_date= end_date,
                            index_as_date= False)

    del data_pandas['ticker']

    data_json = data_pandas.to_json(orient='records')
    data_dict = json.loads(data_json)

    data_array = []

    for data in data_dict:
        data["date"] = data["date"]/1000
        
        # item = [Timestamp, O, H, L, C]
        item = []
        
        item.append(data["date"])
        item.append(data["open"])
        item.append(data["high"])
        item.append(data["low"])
        item.append(data["close"])

        data_array.append(item)
    

    return_json = {}
    return_json['ticker'] = ticker
    return_json['name'] = get_name(ticker)
    return_json['data'] = data_array

    return jsonify(return_json)


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
