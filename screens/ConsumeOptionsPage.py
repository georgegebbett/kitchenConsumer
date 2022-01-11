from grocy.do_consume import do_consume


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

        self.progress_thread = None

    def on_raise(self, item: GrocyItem):
        self.progress_bar["value"] = 0
        self.item = item
        self.item_name.set(item.name)
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
                self.controller.show_frame(ItemsPage)
                do_consume(self.item.id, self.quantity.get())
                break

    def interpret_keypress(self, key, code):
        print("Consume option page handler")
        if get_hotkey_item(get_hotkey_location(code)).id == self.item.id:
            self.progress_thread.do_run = False
            self.quantity.set(self.quantity.get() + 1)
            self.quantity_string.set(f"Quantity: {self.quantity.get()}")
            self.progress_bar["value"] = 0
            self.progress_thread.do_run = True

    def do_consume(self, item_id: int, quantity: int):
        headers = {'GROCY-API-KEY': grocy_config_object.api_key}
        consume_url = f"{grocy_config_object.base_url}/stock/products/{item_id}/consume"
        res = requests.post(consume_url, json={"amount": quantity}, headers=headers)
        print(res.json())