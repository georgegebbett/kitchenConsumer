class OptionPage(tk.Frame):

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
        print("Option page handler")
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
