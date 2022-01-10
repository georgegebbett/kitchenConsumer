import evdev


def grab_key_in_thread(app_instance):
    print(app_instance.frames)
    device = evdev.InputDevice('/dev/input/event0')
    device.grab()
    for event in device.read_loop():

        # print(f"Type: {event.type!s} Code: {event.code!s} Value: {event.value!s}")

        if event.type == evdev.ecodes.EV_KEY and event.value == 1:
            # app_instance.active_frame.interpret_keypress(evdev.ecodes.KEY[int(event.code)], event.code, True)
            print(app_instance.active_frame)
            app_instance.active_frame.interpret_keypress(str(event.code), event.code)
