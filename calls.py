import requests

def GetTicker(market):
    return requests.get("https://bittrex.com/api/v1.1/public/getticker?market=" + market)

def GetMarketSummary(market):
    return requests.get("https://bittrex.com/api/v1.1/public/getmarketsummary?market=" + market)
