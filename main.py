import threading
import tkinter as tk
import json
import requests
import os
import sys
import evdev
import yaml

from key_grab import grab_key_in_thread
from hotkey_utils import get_hotkey_location

# import keyboard

if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

# open and read the config file
with open('/home/pi/barcode/kitchenConsumer/config.yaml', 'r') as config:
    try:
        options = yaml.safe_load(config)
    except yaml.YAMLError as err:
        print(err)

# set Grocy variables
grocy_config_object = options['grocy']

# Other misc variables
runFullscreen = options['fullscreen']
LARGE_FONT = ("Verdana", 25)

hotkey_items = options['hotkey_items']

print(hotkey_items)

# Get the items from Grocy
headers = {'GROCY-API-KEY': grocy_config_object["api_key"]}
itemRes = requests.get(grocy_config_object["base_url"] + "objects/products", headers=headers)

items = []

for item in json.loads(itemRes.content):
    items.append({"id": item["id"], "name": item["name"]})

print(items)


def do_nothing():
    pass


def get_hotkey_item(hotkey_position):
    return get_item_by_id(hotkey_items[hotkey_position[0]][hotkey_position[1]])


def get_item_by_id(item_id):
    for item in items:
        if item["id"] == item_id:
            return item

    return -1


class CupboardConsumer(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.active_frame = None
        container = tk.Frame(self)

        if runFullscreen:
            self.attributes('-fullscreen', True)
            self.config(cursor="none")

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.geometry('1024x768')

        self.frames = {}

        for F in (
                SplashScreen, ItemsPage, QuantityPage, ConsumeResultPage):
            frame = F(container, self)
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SplashScreen)

        # Start keyboard watcher thread
        thread = threading.Thread(target=grab_key_in_thread, args=[self])
        thread.start()

        self.show_frame(ItemsPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        self.active_frame = frame
        frame.tkraise()


class SplashScreen(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        label = tk.Label(self, text="Cupboard Consumer\nLoading...", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='NSEW')


def set_numlock():
    ui = evdev.UInput()
    ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_A, 1)
    ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_A, 0)
    ui.syn()
    ui.close()


class ItemsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.keyName = tk.StringVar()
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)

        label = tk.Label(self, text="Scan an item or select a hotkey", font=LARGE_FONT)
        label.grid(column=0, row=0)

        label = tk.Label(self, text="Press Ctrl to access options", font=LARGE_FONT)
        label.grid(column=0, row=1, sticky='EW')

        label = tk.Label(self, textvariable=self.keyName, font=LARGE_FONT)
        label.grid(column=0, row=2, sticky='EW')

        self.key_mapping = {
            29: self.open_options_screen
        }

    def handle_hotkey(self, hotkey_position):
        try:
            selected_item = get_hotkey_item(hotkey_position)
            item_name = selected_item["name"]
            print(selected_item)
            self.keyName.set(item_name)
        except IndexError:
            self.keyName.set("Key not configured")

    def open_options_screen(self):
        self.controller.show_frame(QuantityPage)

    def interpret_keypress(self, key, code):
        hotkey_location = get_hotkey_location(code)
        if hotkey_location == -1:
            try:
                self.key_mapping[code]()
            except KeyError:
                self.keyName.set("Number key")
        else:
            self.handle_hotkey(hotkey_location)


class QuantityPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.quantity = tk.StringVar()
        self.itemId = tk.StringVar()
        self.itemName = tk.StringVar()
        self.quantityChanged = tk.BooleanVar()

        self.key_mapping = {
            67: self.open_home_screen
        }

        label = tk.Label(self, text="Choose a hotkey to set up", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW', columnspan=3)

        button = tk.Button(self, text="1", wraplength='140', font=LARGE_FONT,
                           command=lambda: self.appendToQuantity("1"))
        button.grid(column=0, row=1, sticky="NSEW")

        button = tk.Button(self, text="2", wraplength='140', font=LARGE_FONT,
                           command=lambda: self.appendToQuantity("2"))
        button.grid(column=1, row=1, sticky="NSEW")

        button = tk.Button(self, text="3", wraplength='140', font=LARGE_FONT,
                           command=lambda: self.appendToQuantity("3"))
        button.grid(column=2, row=1, sticky="NSEW")

        button = tk.Button(self, text="4", wraplength='140', font=LARGE_FONT,
                           command=lambda: self.appendToQuantity("4"))
        button.grid(column=0, row=2, sticky="NSEW")

        button = tk.Button(self, text="5", wraplength='140', font=LARGE_FONT,
                           command=lambda: self.appendToQuantity("5"))
        button.grid(column=1, row=2, sticky="NSEW")

        button = tk.Button(self, text="6", wraplength='140', font=LARGE_FONT,
                           command=lambda: self.appendToQuantity("6"))
        button.grid(column=2, row=2, sticky="NSEW")

        button = tk.Button(self, text="7", wraplength='140', font=LARGE_FONT,
                           command=lambda: self.appendToQuantity("7"))
        button.grid(column=0, row=3, sticky="NSEW")

        button = tk.Button(self, text="8", wraplength='140', font=LARGE_FONT,
                           command=lambda: self.appendToQuantity("8"))
        button.grid(column=1, row=3, sticky="NSEW")

        button = tk.Button(self, text="9", wraplength='140', font=LARGE_FONT,
                           command=lambda: self.appendToQuantity("9"))
        button.grid(column=2, row=3, sticky="NSEW")

        button = tk.Button(self, text="0", wraplength='140', font=LARGE_FONT,
                           command=lambda: self.appendToQuantity("0"))
        button.grid(column=0, row=4, sticky="NSEW")

        button = tk.Button(self, text="<", wraplength='140', font=LARGE_FONT,
                           command=lambda: self.backspaceQuantity())
        button.grid(column=1, row=4, sticky="NSEW", columnspan=2)

        button = tk.Button(self, text="Consume", wraplength='320', font=LARGE_FONT,
                           command=lambda: self.doConsume(self.itemId.get(), self.itemName.get()))
        button.grid(column=0, row=5, sticky="NSEW", columnspan=3)

    def open_home_screen(self):
        self.controller.show_frame(ItemsPage)

    def interpret_keypress(self, key, code):
        self.quantity.set(code)
        try:
            self.key_mapping[code]()
        except KeyError:
            do_nothing()

    def appendToQuantity(self, quant):
        if not self.quantityChanged.get():
            self.quantity.set(quant)
            self.quantityChanged.set(True)
        else:
            self.quantity.set(self.quantity.get() + quant)

    def backspaceQuantity(self):
        if not self.quantityChanged.get() or self.quantity.get() == "":
            self.controller.show_frame(ItemsPage)
        self.quantity.set(self.quantity.get()[0:-1])

    def doConsume(self, itemId, itemName):
        pass
        # consumeHeaders = {
        #     'GROCY-API-KEY': grocyApiKey,
        #     'Content-Type': 'application/json'
        # }
        #
        # data = json.dumps({
        #     "amount": self.quantity.get(),
        #     "transaction_type": "consume",
        #     "spoiled": False
        # })
        # consumeRes = requests.post(grocyApiUrl + "stock/products/" + itemId + "/consume", headers=consumeHeaders,
        #                            data=data)
        # if consumeRes.status_code == 200:
        #     openResultPage(itemName, self.quantity.get(), True, self.controller)
        # else:
        #     openResultPage(json.loads(consumeRes.text)["error_message"], self.quantity.get(), False, self.controller)


class ConsumeResultPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.success = tk.BooleanVar()
        self.message = tk.StringVar()

        self.label = tk.Label(self, textvariable=self.message, font=LARGE_FONT, wraplength='320')
        self.label.grid(column=0, row=0, sticky='NSEW')


# def openQuantityPage(item, controller):
#     app.frames[QuantityPage].quantity.set(item["quick_consume_amount"])
#     app.frames[QuantityPage].quantityChanged.set(False)
#     app.frames[QuantityPage].itemId.set(item["id"])
#     app.frames[QuantityPage].itemName.set(item["name"])
#     controller.show_frame(QuantityPage)
#
#
# def openResultPage(item, quantity, success, controller):
#     app.frames[ConsumeResultPage].success.set(success)
#     if success:
#         app.frames[ConsumeResultPage].message.set("Successfully consumed " + quantity + " of " + item)
#         app.frames[ConsumeResultPage].label.config(bg="GREEN")
#     else:
#         app.frames[ConsumeResultPage].message.set("Error during consumption\n" + item)
#         app.frames[ConsumeResultPage].label.config(bg="RED")
#
#
#     controller.show_frame(ConsumeResultPage)
#
#     controller.after(2500, controller.show_frame, ItemsPage)


app = CupboardConsumer()

app.mainloop()
