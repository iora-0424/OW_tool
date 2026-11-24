import keyboard
import time


class KeyboardListener:

    def wait_for_tab(self):
        """
        TABキーが押されるまで待機する。
        押下(KEY_DOWN)イベントで返る。
        """

        while True:
            event = keyboard.read_event()

            if (
                event.name == "tab"
                and event.event_type == keyboard.KEY_DOWN
            ):
                return

    def wait_for_tab_release(self):
        """
        TABキーが離されるまで待機する。
        """

        while keyboard.is_pressed("tab"):
            time.sleep(0.01)