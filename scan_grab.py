import re

import evdev


def grab_scan_in_thread(app_instance):
    device_path = None
    key_regex = "KEY_(\\w+)"

    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if "Joystick" in device.name:
            print(f"Scanner found at {device.path}")
            device_path = device.path

    if device_path is None:
        print("No scanner found")
        return

    scanner = evdev.InputDevice(device_path)
    scanner.grab()
    for event in scanner.read_loop():
        # print(f"Type: {event.type!s} Code: {event.code!s} Value: {event.value!s}")
        if event.type == evdev.ecodes.EV_KEY and event.value == 1:
            match = re.match(key_regex, evdev.ecodes.KEY[event.code]).group(1)
            try:
                app_instance.active_frame.interpret_scan(match)
            except:
                pass

