from tkinter.ttk import *
from tkinter import Menu, Toplevel, StringVar
import tkinter
import os, sys, math, collections, pickle
from os import listdir
from os.path import isfile, join

from pydub import AudioSegment
from pydub.playback import play

from popups import *
from utils import RepeatedTimer
from calls import *

root = tkinter.Tk()

#the alert class, holds the price and whether to check for it being below or above
class Alert(object):
    def __init__(self, btc_price, usd_price, g_l):
        self.btc_price = btc_price
        self.usd_price = usd_price
        self.g_l = g_l

#the alert event class, this is sent back when an alert is triggered
class AlertEvent(object):
    def __init__(self, alert, info):
        self.alert = alert
        self.info = info

class NotifSound(object):
    def __init__(self, filename, path, selected):
        self.filename = filename
        self.path = path

# the coin class, this is used to hold info about a coin including list of alerts
class Coin(object):
    def __init__(self, name, btc_price, usd_price):
        self.name = name
        self.btc_price = btc_price
        self.usd_price = usd_price
        self.alerts = []
        self.displayed = False

    def check_alerts(self):
        alert_events = []
        for a in self.alerts:
            if a.g_l and a.btc_price != None:
                if float(self.btc_price) > float(a.btc_price):
                    alert_events.append(AlertEvent(a, "BTC price is now " + self.btc_price + " (greater than the alert price, set at " + a.btc_price + ")"))
                    self.remove_alert(a)
            if a.g_l and a.usd_price != None:
                if float(self.usd_price) > float(a.usd_price):
                    alert_events.append(AlertEvent(a, "USD price is now " + self.usd_price + " (greater than the alert price, set at " + a.usd_price + ")"))
                    self.remove_alert(a)
            if not a.g_l and a.btc_price != None:
                if float(self.btc_price) < float(a.btc_price):
                    alert_events.append(AlertEvent(a, "BTC price is now " + self.btc_price + " (less than the alert price, set at " + a.btc_price + ")"))
                    self.remove_alert(a)
            if not a.g_l and a.usd_price != None:
                if float(self.usd_price) < float(a.usd_price):
                    alert_events.append(AlertEvent(a, "USD price is now " + self.usd_price + " (less than the alert price, set at " + a.usd_price + ")"))
                    self.remove_alert(a)
            return alert_events

    def add_alert(self, alert):
        if alert not in self.alerts:
            self.alerts.append(alert)

    def remove_alert(self, alert):
        self.alerts = [x for x in self.alerts if x != alert]

class Overview:
    def __init__(self, master):
        self._NAME = "Coinz.py"
        self._SOUNDS = "sounds"

        self.master = master
        self.master.title(self._NAME)        

        self.sound_name = "320181__dland__hint.wav"
        self.sound_array = self.get_sounds()

        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        #root.configure(bg=_LIGHT_BG_COLOR)

        #style = Style(root)
        #style.theme_use("clam")
        #style.configure("Treeview", background=_BG_COLOR, foreground=_LIGHT_BG_COLOR, fieldbackground=_BG_COLOR)

        #get btc price, start timer, init coin list
        self.btc_price = GetTicker("usdt-btc").json()["result"]["Last"]
        self.rt = RepeatedTimer(15, self.update_coins, "World")
        self.coin_list = []

        #create menubar
        self.menubar = Menu(master)
        self.settingsmenu = Menu(self.menubar, tearoff=0)
        self.settingsmenu.add_command(label="Sounds", command=self.edit_sounds)
        #self.settingsmenu.add_command(label="setting 2", command="")
        #self.settingsmenu.add_separator()
        #self.settingsmenu.add_command(label="setting 3", command="")
        self.menubar.add_cascade(label="Settings", menu=self.settingsmenu)

        root.config(menu=self.menubar)

        #create treeview
        ct_header = ["shitcoin", "฿itcoin ฿rice", "usd price", "alerts"]
        ct_width = [128, 100, 100, 40]
        self.cointree = Treeview(master, selectmode="browse", columns=ct_header, show="headings")
        for i in range(len(ct_header)):
            self.cointree.heading(ct_header[i], text=ct_header[i])
            self.cointree.column(ct_header[i], width=ct_width[i])
        self.cointree.grid(column=0, row=0, columnspan=6, rowspan=6)

        #create buttons
        button_frame = Frame(master)

        self.addcoin_button = Button(button_frame, text="Add Coin", command=self.add_coin)
        self.addcoin_button.grid(column=0, row=0)
        self.removecoin_button = Button(button_frame, text="Remove Coin", command=self.remove_coin)
        self.removecoin_button.grid(column=0, row=1)
        self.button_separator = Separator(button_frame, orient="horizontal")
        self.button_separator.grid(column=0, row=2, sticky="NEWS", pady=5)
        self.addalert_button = Button(button_frame, text="Add Alert", command=self.add_alert)
        self.addalert_button.grid(column=0, row=3)
        self.viewalerts_button = Button(button_frame, text="View Alerts", command=self.view_alerts)
        self.viewalerts_button.grid(column=0, row=4)

        button_frame.grid(column=6, row=0)

        #status label
        status_frame = Frame(master)
        self.status_info_text = StringVar()
        self.status_info_text.set("example info")
        self.status_price_text = StringVar()
        self.status_price_text.set("example price")
        self.status_info = Label(status_frame, relief="sunken", textvariable=self.status_info_text)
        self.status_price = Label(status_frame, relief="sunken", textvariable=self.status_price_text)
        self.status_info.grid(column=0, row=0)
        self.status_price.grid(column=1, row=0)
        status_frame.grid(column=0, row=6, columnspan=6)
        ##load shit

        if os.path.exists(os.path.join(os.getcwd(), "coinlist.pickle")):
            with open('coinlist.pickle', 'rb') as f:
                self.coin_list = pickle.load(f)

        temp_sound_name = ""
        if os.path.exists(os.path.join(os.getcwd(), "soundname.pickle")):
            with open('soundname.pickle', 'rb') as f:
                temp_sound_name = pickle.load(f)

        ind = next(iter([i for i in range(len(self.sound_array)) if self.sound_array[i].find(temp_sound_name) != -1]),None)
        if ind != None:
            self.sound_name = temp_sound_name
        else:
            ErrorPopup(self.master,"saved sound " + temp_sound_name + " not found! \\n it will be replaced with the default on close")
        
        del(temp_sound_name)

        #update treeview
        self.display_coinlist(True)

    def edit_sounds(self):
        self.edit_sounds_popup = EditSoundsPopup(self, self.master)
        self.master.wait_window(self.edit_sounds_popup.top)

    def get_sounds(self):
        sound_array = []
        for sound in [f for f in listdir(self._SOUNDS) if isfile(join(self._SOUNDS, f))]:
            sound_array.append(join(self._SOUNDS, sound))
        return sound_array

    def get_selected_sound(self):        
        print(self.sound_array[self.sound_index])
        return self.sound_array[self.sound_index]

    def update_coins(self,args):
        #update btc price and btc display
        self.btc_price = GetTicker("usdt-btc").json()["result"]["Last"]
        self.status_price_text.set(("BTC: " + self.format_dollar(self.btc_price)))
        #update coin objects
        for c in self.coin_list:
            coin_data = GetTicker(c.name).json()
            c.btc_price = self.format_satoshi(coin_data["result"]["Last"])
            c.usd_price = self.format_dollar(coin_data["result"]["Last"]*self.btc_price)
            #this will return alert events if any are tripped
            alert_events = c.check_alerts()
            if alert_events is not None:
                if len(alert_events) > 0:
                    #dont spam alert sounds, one will suffice
                    self.master.deiconify()
                    self.master.focus_force()
                    self.play_notif_sound()
                    #display each one
                    for a in alert_events:
                        AlertPopup(self.master, c, a.info)
        #coin objects are updated, time to update display
        if len(self.cointree.get_children()) > 0:
            for y in self.cointree.get_children():
                c = [f for f in self.coin_list if f.name == self.cointree.item(y)["values"][0]]
                if len(c) > 0:
                    self.cointree.set(y,column="฿itcoin ฿rice",value=c[0].btc_price)
                    self.cointree.set(y,column="usd price",value=c[0].usd_price)
                    self.cointree.set(y,column="alerts",value=len(c[0].alerts))
                else:
                    ErrorPopup(self.master, "error updating " + c[0].name )

    def add_coin(self):
        self.add_coin_popup =AddCoinPopup(self.master)
        self.addcoin_button["state"] = "disabled"
        self.master.wait_window(self.add_coin_popup.top)
        self.addcoin_button["state"] = "normal"

        ##check if user did not fill out form
        if not hasattr(self.add_coin_popup, "value"):
            print("no value 'value' in add_coin_popup")
            return
        #get ticker from input
        coin_ticker = self.add_coin_popup.value
        #rudimentary check for validity
        if coin_ticker.find("-") == -1:
            ErrorPopup(self.master,"Coin ticker appears to be malformed! please enter it formatted as XXX-XXX")
            return

        for c in self.coin_list:
            if coin_ticker.lower() == c.name.lower():
                InfoPopup(self.master,"You already added this coin!")
                return

        #this needs some checking
        coin_data = GetTicker(coin_ticker).json()
        #create coin object
        _coin = Coin(
            coin_ticker.upper(),
            self.format_satoshi(coin_data["result"]["Last"]),
            self.format_dollar(coin_data["result"]["Last"]*self.btc_price)
        )
        #add
        self.coin_list.append(_coin)
        #update treeview
        self.display_coinlist(False)

    def remove_coin(self):
        selected_coin = self.cointree.selection()[0] if len(self.cointree.selection()) > 0 else None
        #if shit in None show a popup
        if selected_coin is None:
            InfoPopup(self.master, "You must select a coin to remove it!")
            return
        ##get the values of the item that was selected
        cointree_item = self.cointree.item(selected_coin)["values"][:-1]
        #do you wanna do dis?
        AreYouSure = AreYouSurePopup(self.master, "remove " + cointree_item[0])
        compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
        self.removecoin_button["state"] = "disabled"
        self.master.wait_window(AreYouSure.top)
        self.removecoin_button["state"] = "normal"
        remove_successful = False
        if AreYouSure.value:
            for c in self.coin_list:
                if compare(cointree_item, [c.name, c.btc_price, c.usd_price]):
                    #found it
                    #remove from treeview
                    self.cointree.delete(selected_coin)
                    #remove from coinlist
                    self.coin_list =  [x for x in self.coin_list if x != c]
                    #ool flip
                    remove_successful = True
        if not remove_successful:
            ErrorPopup(self.master,"Something went wrong during removal! The coin was not deleted.")

    def display_coinlist(self,first_time):
        #this adds a coin to the treeview only if the "displayed" internal value of it is false
        if first_time:
            for c in self.coin_list:
                self.cointree.insert('', 'end', values=(c.name,c.btc_price,c.usd_price,len(c.alerts)))
        else:
            for c in [x for x in self.coin_list if x.displayed != True]:
                c.displayed = True
                self.cointree.insert('', 'end', values=(c.name,c.btc_price,c.usd_price,len(c.alerts)))

    def view_alerts(self):
        selected_coin = self.cointree.selection()[0] if len(self.cointree.selection()) > 0 else None
        #if shit in None show a popup
        if selected_coin is None:
            InfoPopup(self.master, "You must select a coin to view alerts!")
            return
        #find coin obj from selected treeview item
        coin_obj = next((v for v in self.coin_list if v.name == self.cointree.item(selected_coin)["values"][0]), None)
        #make sure shit is there
        if coin_obj is None:
            ErrorPopup(self.master, "Selected coin not found in the internal coin list!")
            return

        self.view_alerts_popup =ViewAlertsPopup(self.master, coin_obj)
        self.viewalerts_button["state"] = "disabled"
        self.master.wait_window(self.view_alerts_popup.top)
        self.viewalerts_button["state"] = "normal"

        ##user might have deleted alerts, so update the alert column
        self.cointree.set(selected_coin,column="alerts",value=len(coin_obj.alerts))

    def add_alert(self):
        selected_coin = self.cointree.selection()[0] if len(self.cointree.selection()) > 0 else None
        #if shit in None show a popup
        if selected_coin is None:
            InfoPopup(self.master, "You must select a coin to add an alert!")
            return

        self.add_alert_popup=AddAlertPopup(self.master)
        self.addalert_button["state"] = "disabled"
        self.master.wait_window(self.add_alert_popup.top)
        self.addalert_button["state"] = "normal"

        ##check if user did not fill out form
        if not hasattr(self.add_alert_popup, "value"):
            print("no value 'value' in add_alert_popup")
            return

        alert_data = self.add_alert_popup.value
        #todo:check data for validity

        #find coin obj from selected treeview item
        coin_obj = next((v for v in self.coin_list if v.name == self.cointree.item(selected_coin)["values"][0]), None)
        #make sure shit is there
        if coin_obj is None:
            ErrorPopup(self.master, "Selected coin not found in the internal coin list!")
            return
        ##add alert to the coin object if shit is there
        coin_obj.add_alert(
            Alert(
                alert_data[2] if alert_data[1] == '0' else None,
                alert_data[2] if alert_data[1] == '1' else None,
                True if alert_data[0] == '1' else False
            )
        )
        ##update alert count in the treeview
        self.cointree.set(selected_coin, column="alerts", value=len(coin_obj.alerts))

    def format_satoshi(self, val):
        return "{:10.8f}".format(val)

    def format_dollar(self, val):
        return "{:10.2f}".format(val)

    def play_notif_sound(self):
        ind = next(iter([i for i in range(len(self.sound_array)) if self.sound_array[i].find(self.sound_name) != -1]),None)
        if ind is None:
            ErrorPopup(self.master,"sound " + self.sound_name + " not found!")
            return
        ns = AudioSegment.from_file(self.sound_array[ind])
        ns = ns[:3*1000]
        play(ns)

    def on_closing(self):
        with open("soundname.pickle", 'wb') as f:
            pickle.dump(self.sound_name, f)

        with open("coinlist.pickle", 'wb') as f:
            pickle.dump(self.coin_list, f)

        self.rt.stop()
        root.destroy()

my_gui = Overview(root)
root.iconbitmap(os.path.join(os.getcwd(), "mao.ico"))
root.mainloop()