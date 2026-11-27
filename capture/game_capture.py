import mss
import numpy as np

from config.settings import CaptureConfig


class GameCapture:

    def __init__(self):
        self.sct = mss.mss()

    def capture(self):
        """
        メインモニター全体をキャプチャする。
        フルスクリーン前提。
        """

        monitor = self.sct.monitors[CaptureConfig.MONITOR_INDEX]

        img = np.array(self.sct.grab(monitor))

        # BGRA → BGR
        return img[:, :, :3]