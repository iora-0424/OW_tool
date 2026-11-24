import mss
import numpy as np


class GameCapture:

    def __init__(self):
        self.sct = mss.mss()

    def capture(self):
        """
        メインモニター全体をキャプチャする。
        フルスクリーン前提。
        """

        monitor = self.sct.monitors[1]

        img = np.array(self.sct.grab(monitor))

        # BGRA → BGR
        return img[:, :, :3]