import threading
import tkinter as tk
from tkinter import ttk
import json
import requests
import os
import yaml
from time import sleep

import hotkey_utils
from key_grab import grab_key_in_thread
from scan_grab import grab_scan_in_thread
from hotkey_utils import get_hotkey_location
from grocy.GrocyItem import GrocyItem
from grocy.GrocyConfig import GrocyConfig
from grocy.ConsumeResponse import ConsumeResponse

if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')

test_mode = False
config_file_name = "config.yaml"

if test_mode:
    config_file_name = "config_demo.yaml"

# open and read the config file
with open(f'/home/pi/barcode/kitchenConsumer/{config_file_name}', 'r') as config:
    try:
        options = yaml.safe_load(config)
    except yaml.YAMLError as err:
        print(err)

# set Grocy variables
grocy_config = options['grocy']
grocy_config_object = GrocyConfig(grocy_config)
print(grocy_config_object)

# Other misc variables
runFullscreen = options['fullscreen']
LARGE_FONT = ("Verdana", 25)
LARGER_FONT = ("Verdana", 50)

hotkey_items = options['hotkey_items']

# Get the items from Grocy
grocy_headers = {'GROCY-API-KEY': grocy_config_object.api_key}
itemRes = requests.get(grocy_config_object.base_url + "/objects/products", headers=grocy_headers)

bb_headers = {"BBUDDY-API-KEY": grocy_config_object.bb_api_key}

items = []

for item in json.loads(itemRes.content):
    items.append(GrocyItem(int(item["id"]), item["name"]))


def do_nothing():
    pass


def get_hotkey_item(hotkey_position):
    try:
        return get_item_by_id(hotkey_items[hotkey_position[0]][hotkey_position[1]])
    except IndexError:
        return False


def get_item_by_id(item_id):
    for item in items:
        # print(f"Looking for {item_id} - this one is {item.id}")
        if item.id == item_id:
            return item

    return -1


def do_consume(item_id: int, quantity: int = 1):
    consume_url = f"{grocy_config_object.base_url}/stock/products/{item_id}/consume"
    res = requests.post(consume_url, json={"amount": quantity}, headers=grocy_headers)

    if res.status_code == 200:
        return ConsumeResponse(True, res.json())
    else:
        return ConsumeResponse(False, res.json())


def barcode_buddy_scan(barcode: str):
    print(f"BB barcode: {barcode}")
    scan_url = f"{grocy_config_object.bb_base_url}/action/scan?apikey={grocy_config_object.bb_api_key}&add={barcode}"
    res = requests.get(scan_url)
    # print(res.json()["data"]["result"])
    return res.json()["data"]["result"]




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

        self.last_keypress = None

        for F in (
                SplashScreen, ItemsPage, OptionPage, ConsumeOptionsPage, ConsumeFailurePage):
            frame = F(container, self)
            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(SplashScreen)

        # Start keyboard watcher thread
        thread = threading.Thread(target=grab_key_in_thread, args=[self])
        thread.start()

        # Start scanner grab thread
        thread2 = threading.Thread(target=grab_scan_in_thread, args=[self])
        thread2.start()

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


class ItemsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.keyName = tk.StringVar()
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.barcode_result = tk.StringVar()
        self.barcode = ""

        label = tk.Label(self, text="Scan an item or select a hotkey", font=LARGER_FONT, wraplength=1000)
        label.grid(column=0, row=0)

        label = tk.Label(self, text="Press Ctrl to access options", font=LARGE_FONT)
        label.grid(column=0, row=2, sticky='EW')

        label = tk.Label(self, textvariable=self.barcode_result, font=LARGE_FONT, wraplength=1000)
        label.grid(column=0, row=1, sticky='EW')

        self.key_mapping = {
            29: self.open_options_screen
        }

    def handle_hotkey(self, hotkey_position):
        selected_item: GrocyItem = get_hotkey_item(hotkey_position)
        print(selected_item)
        if selected_item:
            item_name = selected_item.name
            self.keyName.set(item_name)
            self.open_consume_option_screen(selected_item)
        else:
            self.keyName.set("Key not configured")

    def open_options_screen(self):
        self.controller.show_frame(OptionPage)

    def open_consume_option_screen(self, item: GrocyItem):
        self.controller.show_frame(ConsumeOptionsPage)
        self.controller.frames[ConsumeOptionsPage].on_raise(item)

    def interpret_keypress(self, code):
        print("Item page handler")
        hotkey_location = get_hotkey_location(code)
        if hotkey_location == -1:
            try:
                self.key_mapping[code]()
            except KeyError:
                self.keyName.set("Number key")
        else:
            self.handle_hotkey(hotkey_location)

    def interpret_scan(self, key: str):
        # self.barcode.set("")
        if key == "ENTER":
            # pass
            self.barcode_result.set(barcode_buddy_scan(self.barcode))
            self.barcode = ""
        elif len(key) == 1:
            self.barcode = (self.barcode + key)


class OptionPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.quantity = tk.StringVar()
        self.itemId = tk.StringVar()
        self.itemName = tk.StringVar()
        self.quantityChanged = tk.BooleanVar()

        self.key_mapping = {
            67: self.open_home_screen
        }

        label = tk.Label(self, text="Choose a hotkey to set up", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='EW', columnspan=4)

        label = tk.Label(self, text="Press 'Cancel' to exit", font=LARGE_FONT)
        label.grid(column=0, row=5, sticky='EW', columnspan=4)

        self.generate_hotkey_buttons()

    def generate_hotkey_buttons(self):
        hotkey_row = 0
        hotkey_col = 0

        while hotkey_row < len(hotkey_utils.hotkey_shape):
            while hotkey_col < len(hotkey_utils.hotkey_shape[hotkey_row]):
                current_item = get_hotkey_item([hotkey_row, hotkey_col])
                if current_item:
                    text = current_item.name
                else:
                    text = "Not Configured"
                hotkey_button = tk.Button(self, text=text, font=LARGE_FONT, wraplength=240)
                hotkey_button.grid(column=hotkey_col, row=hotkey_row + 1, sticky="NSEW")
                hotkey_col += 1
            hotkey_row += 1
            hotkey_col = 0

        # self.key_0_0_button = tk.Button(self, text="1", wraplength='140', font=LARGE_FONT)
        # self.key_0_0_button.grid(column=0, row=1, sticky="NSEW")

        # button = tk.Button(self, text="2", wraplength='140', font=LARGE_FONT)
        # button.grid(column=1, row=1, sticky="NSEW")
        #
        # button = tk.Button(self, text="3", wraplength='140', font=LARGE_FONT)
        # button.grid(column=2, row=1, sticky="NSEW")
        #
        # button = tk.Button(self, text="4", wraplength='140', font=LARGE_FONT)
        # button.grid(column=0, row=2, sticky="NSEW")
        #
        # button = tk.Button(self, text="5", wraplength='140', font=LARGE_FONT)
        # button.grid(column=1, row=2, sticky="NSEW")
        #
        # button = tk.Button(self, text="6", wraplength='140', font=LARGE_FONT)
        # button.grid(column=2, row=2, sticky="NSEW")
        #
        # button = tk.Button(self, text="7", wraplength='140', font=LARGE_FONT)
        # button.grid(column=0, row=3, sticky="NSEW")
        #
        # button = tk.Button(self, text="8", wraplength='140', font=LARGE_FONT)
        # button.grid(column=1, row=3, sticky="NSEW")
        #
        # button = tk.Button(self, text="9", wraplength='140', font=LARGE_FONT)
        # button.grid(column=2, row=3, sticky="NSEW")
        #
        # button = tk.Button(self, text="0", wraplength='140', font=LARGE_FONT)
        # button.grid(column=0, row=4, sticky="NSEW")
        #
        # button = tk.Button(self, text="<", wraplength='140', font=LARGE_FONT)
        # button.grid(column=1, row=4, sticky="NSEW", columnspan=2)

    def open_home_screen(self):
        self.controller.show_frame(ItemsPage)

    def interpret_keypress(self, code):
        print("Option page handler")
        self.quantity.set(code)
        try:
            self.key_mapping[code]()
        except KeyError:
            do_nothing()


class ConsumeOptionsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.success = tk.BooleanVar()
        self.item = None
        self.item_name = tk.StringVar()
        self.quantity = tk.IntVar()
        self.quantity_string = tk.StringVar()

        self.label = tk.Label(self, textvariable=self.item_name, font=LARGER_FONT, wraplength='1020')
        self.label.grid(column=0, row=0, sticky='NSEW')

        self.label = tk.Label(self, text="Enter a quantity or scan another item", font=LARGE_FONT, wraplength='320')
        self.label.grid(column=0, row=1, sticky='NSEW')

        self.label = tk.Label(self, textvariable=self.quantity_string, font=LARGE_FONT, wraplength='320')
        self.label.grid(column=0, row=2, sticky='NSEW')

        self.progress_bar = ttk.Progressbar(self, mode='determinate', orient='horizontal')
        self.progress_bar.grid(column=0, row=3, sticky='NSEW')

        self.key_mapping = {
            67: self.cancel_consume,
            88: do_nothing
        }

        self.progress_thread = None

    def on_raise(self, new_item: GrocyItem):
        self.progress_bar["value"] = 0
        self.item = new_item
        self.item_name.set(new_item.name)
        self.quantity.set(1)
        self.quantity_string.set(f"Quantity: {self.quantity.get()}")
        self.progress_thread = threading.Thread(target=self.progress)

        self.progress_thread.start()

    def progress(self):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            self.progress_bar["value"] += 2
            sleep(0.05)
            if self.progress_bar["value"] >= 100:
                result = do_consume(self.item.id, self.quantity.get())
                print(result)
                if result.success:
                    self.controller.show_frame(ItemsPage)
                else:
                    self.controller.frames[ConsumeFailurePage].error_message.set(result.error)
                    self.controller.frames[ConsumeFailurePage].on_raise()
                    self.controller.show_frame(ConsumeFailurePage)
                break

    def increase_quantity(self, quantity: int = 1):
        self.progress_thread.do_run = False
        self.quantity.set(self.quantity.get() + quantity)
        print(f"Quantity increased to {self.quantity.get()}")
        self.quantity_string.set(f"Quantity: {self.quantity.get()}")
        self.progress_bar["value"] = 0
        self.progress_thread.do_run = True

    def cancel_consume(self):
        print("Cancelling consumption!")
        self.progress_thread.do_run = False
        self.controller.show_frame(ItemsPage)

    def interpret_keypress(self, code):
        print("Consume option page handler")
        try:
            self.key_mapping[code]()
        except KeyError:
            if get_hotkey_item(get_hotkey_location(code)).id == self.item.id:
                self.increase_quantity()


class ConsumeFailurePage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.progress_thread = None
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.error_message = tk.StringVar()

        label = tk.Label(self, text="Consume failed!", font=LARGER_FONT, wraplength=1000, background="RED")
        label.grid(column=0, row=0, sticky="NSEW")

        label = tk.Label(self, textvariable=self.error_message, font=LARGE_FONT, wraplength=1000, background="RED")
        label.grid(column=0, row=1, sticky='NSEW')

        self.progress_bar = ttk.Progressbar(self, mode='determinate', orient='horizontal')
        self.progress_bar.grid(column=0, row=2, sticky='NSEW')

        self.key_mapping = {
            67: self.show_home_screen
        }

    def show_home_screen(self):
        print("Exiting to home")
        self.progress_thread.do_run = False
        self.controller.show_frame(ItemsPage)

    def interpret_keypress(self, code):
        print("Consume failure page handler")
        try:
            self.key_mapping[code]()
        except KeyError:
            pass

    def on_raise(self):
        self.progress_bar["value"] = 0
        self.progress_thread = threading.Thread(target=self.progress)
        self.progress_thread.start()

    def progress(self):
        t = threading.currentThread()
        while getattr(t, "do_run", True):
            self.progress_bar["value"] += 1
            sleep(0.05)
            if self.progress_bar["value"] >= 100:
                self.controller.show_frame(ItemsPage)
                break


app = CupboardConsumer()

app.mainloop()
