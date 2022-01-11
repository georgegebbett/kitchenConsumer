class ItemsPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.keyName = tk.StringVar()
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=1)

        label = tk.Label(self, text="Scan an item or select a hotkey", font=LARGER_FONT, wraplength=1000)
        label.grid(column=0, row=0)

        label = tk.Label(self, text="Press Ctrl to access options", font=LARGE_FONT)
        label.grid(column=0, row=1, sticky='EW')

        # label = tk.Label(self, textvariable=self.keyName, font=LARGE_FONT)
        # label.grid(column=0, row=2, sticky='EW')

        self.key_mapping = {
            29: self.open_options_screen
        }

    def handle_hotkey(self, hotkey_position):
        try:
            selected_item: GrocyItem = get_hotkey_item(hotkey_position)
            print(selected_item)
            item_name = selected_item.name
            self.keyName.set(item_name)
            self.open_consume_option_screen(selected_item)
        except IndexError:
            self.keyName.set("Key not configured")

    def open_options_screen(self):
        self.controller.show_frame(OptionPage)

    def open_consume_option_screen(self, item: GrocyItem):
        self.controller.show_frame(ConsumeOptionsPage)
        self.controller.frames[ConsumeOptionsPage].on_raise(item)

    def interpret_keypress(self, key, code):
        print("Item page handler")
        hotkey_location = get_hotkey_location(code)
        if hotkey_location == -1:
            try:
                self.key_mapping[code]()
            except KeyError:
                self.keyName.set("Number key")
        else:
            self.handle_hotkey(hotkey_location)