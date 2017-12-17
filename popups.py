from tkinter.ttk import Label, Button, Combobox, Entry, Treeview, Notebook, Style, Frame
from tkinter import Toplevel, Spinbox, StringVar
import collections, os

from objs import Exchange
from pydub import AudioSegment
from pydub.playback import play

def center(win, master):
    win.update_idletasks()
    xcenter_of_master = master.winfo_rootx() + (master.winfo_width()/2)
    ycenter_of_master = master.winfo_rooty() + ((master.winfo_rooty() - master.winfo_y())/2)
    xpos_for_pop = xcenter_of_master - win.winfo_width()/2
    ypos_for_pop = ycenter_of_master - win.winfo_height()/4
    win.geometry("+%d+%d" % (xpos_for_pop, ypos_for_pop))

class InfoPopup(object):
    def __init__(self, master, info):
        self.top = Toplevel(master)
        Label(self.top, text=info).pack()
        Button(self.top, text='Ok', command=self.cleanup).pack()
        ##center after packing
        center(self.top, master)
    def cleanup(self):
        self.top.destroy()

class ErrorPopup(object):
    def __init__(self, master, error):
        self.top = Toplevel(master)
        Label(self.top, text="Error! \n" + error).pack()
        Button(self.top, text='Ok', command=self.cleanup).pack()
        ##center after packing
        center(self.top, master)
    def cleanup(self):
        self.top.destroy()

class AlertPopup(object):
    def __init__(self, master, coin, info):
        self.top = Toplevel(master)
        Label(self.top, text="Alert for " + coin.name +"!" + "\n" \
            + info + "\n" + "The alert has now been removed").pack()
        Button(self.top, text='Ok', command=self.cleanup).pack()
        ##center after packing
        center(self.top, master)
    def cleanup(self):
        self.top.destroy()

class AreYouSurePopup(object):
    def __init__(self, master, text):
        self.top = Toplevel(master, padx=20)
        Label(self.top, text="Are you sure you want to " + text + "?").pack()
        Button(self.top, text='Yes', command=self.yes).pack()
        Button(self.top, text='No!', command=self.no).pack()
        ##center after packing
        center(self.top, master)
    def yes(self,):
        self.value = True
        self.top.destroy()
    def no(self,):
        self.value = False
        self.top.destroy()

class EditSettingsPopup(object):
    def __init__(self, overview, master):
        self.top = Toplevel(master)
        self.top.title("Settings")
        self.master = master
        self.overview = overview

        self.nb = Notebook(self.top, width=500, height=330)

        self.nb_t1 = Frame(self.top)
        self.nb_t2 = Frame(self.top)
        
        ex = [x.name for x in Exchange]

        #general tab
        self.t1_exchange = Combobox(self.nb_t1, values=ex, width=20)
        #replace with old val
        self.t1_exchange.set(ex[0])
        Label(self.nb_t1, text="Default exchange:").grid(row=0, column=0, sticky="NEWS")
        self.t1_exchange.grid(row=0, column=2, columnspan=1)
        Label(self.nb_t1, text="Update interval(sec):").grid(row=1, column=0, sticky="NEWS")
        self.t1_interval_var = StringVar()
        self.t1_interval = Spinbox(self.nb_t1, textvariable=self.t1_interval_var, values=(3,5,10,15,30,60,120,300), width=20)
        ##replace with old val---set after making spinbox
        self.t1_interval_var.set("15")
        self.t1_interval.grid(row=1, column=2, columnspan=1)

        self.nb.add(self.nb_t1, text="General")
        self.nb.add(self.nb_t2, text="Sounds")

        self.nb.grid(row=0, column=0, columnspan=3, rowspan=3, sticky="NEWS")

        ##center after packing
        center(self.top, master)
        
    def cleanup(self):
        self.top.destroy()

class EditSoundsPopup(object):
    def __init__(self, overview, master):
        self.top = Toplevel(master, padx=50, pady=20)
        self.top.title("Edit Sounds")
        self.master = master
        self.overview = overview

        s_a = [x[x.rfind("\\")+1:] for x in self.overview.sound_array]

        ind = next(iter([i for i in range(len(self.overview.sound_array)) \
            if self.overview.sound_array[i].find(self.overview.sound_name) != -1]), None)
        if ind is None:
            ErrorPopup(self.master, "default sound " + self.overview.sound_name + " not found!")
            return

        soundobj = self.overview.sound_array[ind]
        self.c = Combobox(self.top, values=s_a, width=40)
        self.c.set(soundobj[soundobj.rfind("\\")+1:])
        self.c.grid(row=1, column=0, columnspan=2, sticky="NEWS")
        Label(self.top, text="Choose a sound:").grid(row=0, column=0, columnspan=2, sticky="NEWS")

        Button(self.top, text='Preview', command=self.play_s).grid(row=2, column=0, pady=10)
        Button(self.top, text='Set', command=self.set_s).grid(row=2, column=1, pady=10)

        ##center after packing
        center(self.top, master)

    def play_s(self):
        print(self.c.get())
        ns = AudioSegment.from_file(os.path.join(self.overview._SOUNDS, self.c.get()))
        ns = ns[:3*1000]
        play(ns)

    def set_s(self):
        self.overview.sound_name = self.c.get()
        self.cleanup()

    def cleanup(self):
        self.top.destroy()

class AddCoinPopup(object):
    def __init__(self, master, overview):
        #228 107
        self.top = Toplevel(master, padx=50, pady=5)
        self.top.title("Add Coin")
        #Label(self.top, text="Add coin").grid(row=0,column=0,columnspan=2,sticky="NEWS")
        exch = ["Bittrex", "Binance"]

        mark = ["BTC", "ETH", "BNB", "USDT"]
        self.c = Combobox(self.top, values=exch, width=10)
        self.c.set(exch[0])
        self.c.grid(row=0, column=0, columnspan=2, sticky="NEWS")
        self.m = Combobox(self.top, values=mark, width=10)
        self.m.set(mark[0])
        self.m.grid(row=1, column=0, sticky="NEWS")
        self.e = Entry(self.top)
        self.e.focus_set()
        self.e.grid(row=1, column=1, columnspan=1, sticky="NEWS")
        Button(self.top, text='Ok', command=self.cleanup).grid(row=2, column=0, columnspan=2)
        ##center after packing
        center(self.top, master)
    def cleanup(self,):
        self.value = [self.c.get(), self.m.get(), self.e.get()]
        self.top.destroy()

class AddAlertPopup(object):
    def __init__(self, master, coin):
        self.top = Toplevel(master)
        self.top.title("Add Alert")
        Label(self.top, text=("Alert when price goes")).grid(row=0, column=0, columnspan=2, sticky="NEWS")
        b_m = ["above", "below"]
        self.a = Combobox(self.top, values=b_m, width=10)
        self.a.set(b_m[0])
        self.a.grid(row=1, column=0, sticky="NEWS")

        self.e = Entry(self.top)
        self.e.focus_set()
        self.e.grid(row=1, column=1, sticky="NEWS")

        mark = [coin.market, "USDT"]
        self.m = Combobox(self.top, values=mark, width=10)
        self.m.set(mark[0])
        self.m.grid(row=1, column=2, sticky="NEWS")

        Button(self.top, text='Ok', command=self.cleanup).grid(row=2, column=0, columnspan=3)
        ##center after packing
        center(self.top, master)
    def cleanup(self):
        self.value = [self.a.get(), self.e.get(), self.m.get()]
        self.top.destroy()

class ViewAlertsPopup(object):
    def __init__(self, master, coin):
        self.top = Toplevel(master)
        self.top.title("View Alerts")
        ##need self.coin later
        self.coin = coin
        ##create treeview
        at_header = ["?", "value", "market"]
        at_width = [90, 100, 100]
        ##need alerttree later
        self.alerttree = Treeview(self.top, selectmode="extended", columns=at_header, show="headings")
        for i in range(len(at_header)):
            self.alerttree.heading(at_header[i], text=at_header[i])
            self.alerttree.column(at_header[i], width=at_width[i], stretch=False)
        self.alerttree.grid(column=0, row=0, columnspan=6, rowspan=6)
        #display alerts
        for a in self.coin.alerts:
            less_or_greater = "less than"
            if a.g_l:
                less_or_greater = "greater than"
            self.alerttree.insert('', 'end', values=(less_or_greater, a.value, a.market))
        #buttons
        self.removealert_button = Button(self.top, text='Remove Alert', command=self.remove_alert)
        self.removealert_button.grid(column=1, row=6, sticky="NEWS")
        Button(self.top, text='Ok', command=self.cleanup).grid(column=0, row=6, sticky="NEWS")
        ##center after packing
        center(self.top, master)

    def remove_alert(self):
        at_value = self.alerttree.item(self.alerttree.selection()[0])["values"] if len(self.alerttree.selection()) > 0 else None
        if at_value is None:
            InfoPopup(self, "You must select an alert to remove it!")
            return
        AreYouSure = AreYouSurePopup(self.top, "remove this alert")
        self.removealert_button["state"] = "disabled"
        self.top.wait_window(AreYouSure.top)
        self.removealert_button["state"] = "normal"
        compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
        if AreYouSure.value:
            for a in self.coin.alerts:
                alt_a_g_l_value = 'less than'
                if a.g_l:
                    alt_a_g_l_value = 'greater than'
                if compare(at_value, [alt_a_g_l_value, float(a.value), a.market]):
                    #found it
                    self.alerttree.delete(self.alerttree.selection()[0])
                    self.coin.alerts = [x for x in self.coin.alerts if x != a]

    def cleanup(self):
        self.top.destroy()
