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

    for data in data_dict:
        data["date"] = datetime.utcfromtimestamp(data["date"]/1000).strftime('%Y/%m/%d')

    return_json = []
    return_json.append({'ticker': ticker, 'name': get_name(ticker)})
    return_json.append({'values': data_dict})
    return jsonify(return_json)


if __name__ == '__main__':
    app.run(debug=True)