import re
import time
from datetime import datetime

import cv2
import numpy as np
import psutil
import win32gui
import win32process

from config.settings import CaptureConfig, PathConfig, ScoreboardConfig
from logger.logger import get_logger

logger = get_logger()


class CaptureManager:

    def __init__(
        self,
        capture,
        locator,
        match_buffer,
        map_recognizer,
    ):
        self.capture = capture
        self.locator = locator
        self.match_buffer = match_buffer
        self.map_recognizer = map_recognizer

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

        map_name = self.map_recognizer.recognize(frame)
        if map_name is None:
            logger.info("Frame rejected (map name unavailable)")
            return

        capture_to_save = self.match_buffer.update(frame, map_name)

        if capture_to_save is not None:
            self.save_capture(*capture_to_save)

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

    def is_valid_frame(self, frame):
        """
        画面全体の平均輝度が許容範囲内か確認する。
        """

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean = np.mean(gray)
        logger.info("Frame Quality : screen mean=%.1f", mean)

        if mean < ScoreboardConfig.QUALITY_MEAN_MIN:
            logger.info("Frame rejected (too dark)")
            return False

        if mean > ScoreboardConfig.QUALITY_MEAN_MAX:
            logger.info("Frame rejected (too bright)")
            return False

        logger.info("Frame accepted")

        return True

    def save_capture(self, frame, map_name: str):
        """
        スクリーンショット保存
        """

        PathConfig.CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

        filename = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )[:-3]

        safe_map_name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", map_name).rstrip(" .")
        filepath = PathConfig.CAPTURES_DIR / f"{filename}_{safe_map_name}.png"
        encoded, png = cv2.imencode(".png", frame)
        if not encoded:
            logger.error("Could not encode capture: %s", filepath)
            return
        filepath.write_bytes(png.tobytes())

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

    def flush(self):
        """
        終了時に最後の1枚を保存する
        """

        capture_to_save = self.match_buffer.flush()

        if capture_to_save is not None:
            self.save_capture(*capture_to_save)
