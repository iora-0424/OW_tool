import os
import time
from datetime import datetime

import cv2
import numpy as np
import psutil
import win32gui
import win32process

from logger.logger import get_logger

logger = get_logger()


# =====================================
# Map Name ROI
# =====================================

MAP_ROI_X = 1323
MAP_ROI_Y = 13
MAP_ROI_WIDTH = 420
MAP_ROI_HEIGHT = 42


# =====================================
# Frame Quality Threshold
# =====================================

QUALITY_MEAN_MIN = 20
QUALITY_MEAN_MAX = 200
QUALITY_STD_MIN = 30


class CaptureManager:

    def __init__(
        self,
        capture,
        locator,
        match_buffer,
    ):
        self.capture = capture
        self.locator = locator
        self.match_buffer = match_buffer

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

        if not result.matched:
            logger.info("Not a scoreboard. Discard.")
            return

        logger.info("Scoreboard detected.")

        # -----------------------------
        # 品質チェック
        # -----------------------------
        if not self.is_valid_frame(frame):
            return

        frame_to_save = self.match_buffer.update(frame)

        if frame_to_save is not None:
            self.save_capture(frame_to_save)

    def capture_best_frame(self):
        """
        スコアボード表示待ち後に3枚撮影し、
        最も一致率の高い画像を返す。

        Returns:
            tuple(frame, result)
        """

        time.sleep(0.10)

        best_frame = None
        best_result = None

        for i in range(3):

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

            time.sleep(0.05)

        return best_frame, best_result

    def is_valid_frame(self, frame):
        """
        マップ名ROIの品質チェック。

        暗転・白飛びなど、
        比較に向かない画像は除外する。
        """

        roi = frame[
            MAP_ROI_Y:MAP_ROI_Y + MAP_ROI_HEIGHT,
            MAP_ROI_X:MAP_ROI_X + MAP_ROI_WIDTH,
        ]

        gray = cv2.cvtColor(
            roi,
            cv2.COLOR_BGR2GRAY,
        )

        mean = np.mean(gray)
        std = np.std(gray)

        logger.info(
            "Frame Quality : mean=%.1f std=%.1f",
            mean,
            std,
        )

        if mean < QUALITY_MEAN_MIN:
            logger.info("Frame rejected (too dark)")
            return False

        if mean > QUALITY_MEAN_MAX:
            logger.info("Frame rejected (too bright)")
            return False

        if std < QUALITY_STD_MIN:
            logger.info("Frame rejected (low contrast)")
            return False

        logger.info("Frame accepted")

        return True

    def save_capture(self, frame):
        """
        スクリーンショット保存
        """

        os.makedirs("captures", exist_ok=True)

        filename = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )[:-3]

        filepath = os.path.join(
            "captures",
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

            return process.name().lower() == "overwatch.exe"

        except Exception as e:

            logger.exception(e)

            return False

    def flush(self):
        """
        終了時に最後の1枚を保存する
        """

        frame = self.match_buffer.flush()

        if frame is not None:
            self.save_capture(frame)