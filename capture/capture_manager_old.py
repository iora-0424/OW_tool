import os
import time
from datetime import datetime

import cv2
import psutil
import win32gui
import win32process

from config.settings import CaptureConfig, PathConfig, ScoreboardConfig
from logger.logger import get_logger

logger = get_logger()


class CaptureManager:

    def __init__(self, capture, locator):
        self.capture = capture
        self.locator = locator

    def process_tab_press(self):
        """
        TABキー押下時の一連の処理
        """

        logger.info("TAB pressed")

        if not self.is_overwatch_active():
            logger.debug("Foreground window is not Overwatch.")
            return

        frame, result = self.capture_best_frame()

        if frame is None:
            logger.warning("Failed to capture frame.")
            return

        if result.matched:
            logger.info("Scoreboard detected.")
            self.save_capture(frame)
        else:
            logger.info("Not a scoreboard. Discard.")

    def capture_best_frame(self):
        """
        スコアボード表示待ち後に3枚撮影し、
        最も一致率の高い画像を返す。

        Returns:
            tuple(frame, result)
        """

        time.sleep(ScoreboardConfig.DISPLAY_DELAY)

        best_frame = None
        best_result = None

        for i in range(ScoreboardConfig.FRAME_COUNT):

            frame = self.capture.capture()

            if frame is None:
                continue

            result = self.locator.detect(frame)

            logger.info(
                "Capture %d : %.3f",
                i + 1,
                result.score
            )

            if (
                best_result is None
                or result.score > best_result.score
            ):
                best_result = result
                best_frame = frame

            time.sleep(ScoreboardConfig.FRAME_INTERVAL)

        return best_frame, best_result

    def save_capture(self, frame):
        """
        スクリーンショット保存
        """

        os.makedirs(PathConfig.CAPTURES_DIR, exist_ok=True)

        filename = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )[:-3]

        filepath = os.path.join(
            PathConfig.CAPTURES_DIR,
            f"{filename}.png"
        )

        cv2.imwrite(filepath, frame)

        logger.info("Saved : %s", filepath)

    def is_overwatch_active(self):
        """
        現在アクティブなウィンドウがOverwatchか判定
        """

        hwnd = win32gui.GetForegroundWindow()

        if hwnd == 0:
            return False

        try:

            _, pid = win32process.GetWindowThreadProcessId(hwnd)

            process = psutil.Process(pid)

            return process.name().lower() == CaptureConfig.GAME_PROCESS

        except Exception as e:

            logger.exception(e)

            return False