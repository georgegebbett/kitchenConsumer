import evdev


def grab_key_in_thread(app_instance):
    device_path = None

    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if "Toshiba" in device.name:
            print(f"Keypad found at {device.path}")
            device_path = device.path

    if device_path is None:
        print("No keypad found")
        return

    keypad = evdev.InputDevice(device_path)
    keypad.grab()
    for event in keypad.read_loop():
        print(f"Type: {event.type!s} Code: {event.code!s} Value: {event.value!s}")
        if event.type == evdev.ecodes.EV_KEY and event.value == 1:
            app_instance.active_frame.interpret_keypress(event.code)
