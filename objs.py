from enum import Enum
from calls import get_ticker, get_last_price

#the alert class, holds the price and whether to check for it being below or above
class Alert(object):
    def __init__(self, market, value, g_l):
        self.market = market
        self.value = value
        self.g_l = g_l

#the alert event class, this is sent back when an alert is triggered
class AlertEvent(object):
    def __init__(self, alert, info):
        self.alert = alert
        self.info = info

class Exchange(Enum):
    Bittrex = 1
    Binance = 2

class Market(Enum):
    BTC = 1
    ETH = 2
    USDT = 3
    BNB = 4

# the coin class, this is used to hold info about a coin including list of alerts
class Coin(object):
    def __init__(self, name, exchange, market, market_price, usd_price):
        self.name = name
        self.exchange = exchange
        self.market = market
        ##used for btc-XXX, ltc-XXX etc
        self.market_price = market_price
        self.usd_price = usd_price
        self.alerts = []
        self.displayed = False

    def check_alerts(self):
        alert_events = []
        for a in self.alerts:
            old_price = float(a.value)
            new_price = get_last_price[self.exchange](a.market,self.name)
            if a.g_l:
                if new_price > old_price:
                    alert_events.append(AlertEvent(a, "price is now " + str(new_price) + ""+ self.market + "(greater than the alert price, set at " + str(old_price) + ")"))
                    self.remove_alert(a)
            else:
                if new_price < old_price:
                    alert_events.append(AlertEvent(a, "price is now " + str(new_price) + ""+ self.market + "(less than the alert price, set at " + str(old_price) + ")"))
                    self.remove_alert(a)
            return alert_events

    def add_alert(self, alert):
        if alert not in self.alerts:
            self.alerts.append(alert)

    def remove_alert(self, alert):
        self.alerts = [x for x in self.alerts if x != alert]