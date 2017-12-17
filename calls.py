import requests

def a(market):
    return requests.get("https://bittrex.com/api/v1.1/public/getticker?market=" + market).json()

def b(market):
    return requests.get("https://api.binance.com/api/v1/ticker/24hr?symbol="+market).json()

def alp(market, name):
    return float(requests.get("https://bittrex.com/api/v1.1/public/getticker?market=" + market + \
       "-" + name).json()["result"]["Last"])

def blp(market, name):
    return float(requests.get("https://api.binance.com/api/v1/ticker/24hr?symbol=" + name.upper() \
        + "" + market.upper()).json()["lastPrice"])

get_ticker = {
    'Bittrex': a,
    'Binance': b
}

get_last_price = {
    'Bittrex': alp,
    'Binance': blp
}
