from pathlib import Path


class OCRConfig:
    LANGUAGE = "eng"
    OEM = 3
    PSM = 7
    SCALE = 4
    ADAPTIVE_BLOCK_SIZE = 31
    ADAPTIVE_C = 11
    LEGACY_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    LEGACY_SCALE = 3
    LEGACY_BINARY_THRESHOLD = 180


class ROIConfig:
    MAP_X = 1323
    MAP_Y = 13
    MAP_WIDTH = 420
    MAP_HEIGHT = 42


class ScoreboardConfig:
    HEADER_TEMPLATE = "template/header.png"
    HEADER_THRESHOLD = 0.80
    DEFAULT_HEADER_THRESHOLD = 0.90
    DISPLAY_DELAY = 0.10
    FRAME_COUNT = 3
    FRAME_INTERVAL = 0.05
    QUALITY_MEAN_MIN = 20
    QUALITY_MEAN_MAX = 200


class MatchConfig:
    SLIDE_RANGE = 10
    BLUR_KERNEL = (3, 3)


class ImageConfig:
    CLAHE_CLIP_LIMIT = 2.0
    CLAHE_TILE_GRID_SIZE = (8, 8)
    CANNY_LOW_THRESHOLD = 50
    CANNY_HIGH_THRESHOLD = 150


class CaptureConfig:
    GAME_PROCESS = "overwatch.exe"
    MONITOR_INDEX = 1
    TAB_KEY = "tab"
    TAB_RELEASE_POLL_INTERVAL = 0.01


class PathConfig:
    CAPTURES_DIR = Path("captures")
    LOG_FILE = Path("logs/ow_logger.log")


class DiagnosticsConfig:
    OK_DIR = PathConfig.CAPTURES_DIR / "ok"
    NG_DIR = PathConfig.CAPTURES_DIR / "ng"
    MAP_LABELS = OK_DIR / "map_name.txt"
    OCR_COMPARE_DIR = PathConfig.CAPTURES_DIR / "ocr_compare"
    OCR_DEBUG_DIR = PathConfig.CAPTURES_DIR / "ocr_debug"
    OCR_RESULTS = PathConfig.CAPTURES_DIR / "result.csv"
    SEPARATOR_DEBUG_DIR = PathConfig.CAPTURES_DIR / "bar_debug"
    SEPARATOR_OCR_MARGIN = 10
    SEPARATOR_MIN_HEIGHT = 15
    SEPARATOR_MAX_WIDTH = 6
    HISTOGRAM_DARK_LIMIT = 30
    HISTOGRAM_BRIGHT_LIMIT = 225
    TEST_IMAGES = Path("test_images")
    DETECTOR_SAMPLE = Path("image/test3.png")
    DETECTOR_DEBUG_FILE = Path("debug.png")
