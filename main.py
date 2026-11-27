from capture.keyboard_listener import KeyboardListener
from capture.game_capture import GameCapture
from capture.capture_manager import CaptureManager
from capture.match_buffer import MatchBuffer

from config.settings import ScoreboardConfig

from detector.scoreboard_locator import ScoreboardLocator
from detector.map_recognizer import MapRecognizer

from logger.logger import get_logger

logger = get_logger()

listener = KeyboardListener()

capture = GameCapture()

locator = ScoreboardLocator(
    ScoreboardConfig.HEADER_TEMPLATE,
    threshold=ScoreboardConfig.HEADER_THRESHOLD
)

match_buffer = MatchBuffer()

manager = CaptureManager(
    capture=capture,
    locator=locator,
    match_buffer=match_buffer,
    map_recognizer=MapRecognizer(),
)

logger.info("==========")
logger.info("OW Logger Started")
logger.info("==========")

try:

    while True:

        # TAB押下待ち
        listener.wait_for_tab()

        # 押した瞬間に処理
        manager.process_tab_press()

        # TABを離すまで次の処理を行わない
        listener.wait_for_tab_release()

except KeyboardInterrupt:

    logger.info("Stopping...")

finally:

    # 最後のマッチのスクリーンショットを保存
    manager.flush()

    logger.info("OW Logger Stopped")
