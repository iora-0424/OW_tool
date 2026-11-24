from capture.keyboard_listener import KeyboardListener
from capture.game_capture import GameCapture
from capture.capture_manager import CaptureManager
from capture.match_buffer import MatchBuffer

from detector.scoreboard_locator import ScoreboardLocator
from detector.map_comparator import MapComparator

from logger.logger import get_logger

logger = get_logger()

listener = KeyboardListener()

capture = GameCapture()

locator = ScoreboardLocator(
    "template/header.png",
    threshold=0.80
)

map_comparator = MapComparator()

match_buffer = MatchBuffer(
    comparator=map_comparator,
    threshold=0.985,
)

manager = CaptureManager(
    capture=capture,
    locator=locator,
    match_buffer=match_buffer,
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