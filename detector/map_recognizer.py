import cv2
import pytesseract
from rapidfuzz import fuzz, process

from config.maps import MAP_NAMES
from config.settings import OCRConfig, ROIConfig
from logger.logger import get_logger

logger = get_logger()


class MapRecognizer:
    def recognize(self, frame) -> str | None:
        roi = frame[
            ROIConfig.MAP_Y:ROIConfig.MAP_Y + ROIConfig.MAP_HEIGHT,
            ROIConfig.MAP_X:ROIConfig.MAP_X + ROIConfig.MAP_WIDTH,
        ]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        config = f"--oem {OCRConfig.OEM} --psm {OCRConfig.PSM}"

        try:
            text = pytesseract.image_to_string(
                gray, lang=OCRConfig.LANGUAGE, config=config
            ).strip()
        except (pytesseract.TesseractNotFoundError, pytesseract.TesseractError) as error:
            logger.error("Map OCR failed: %s", error)
            return None

        if not any(character.isalpha() for character in text):
            return None

        map_name, score, _ = process.extractOne(text, MAP_NAMES, scorer=fuzz.WRatio)
        logger.info("Map OCR: %s (match score=%.1f, text=%r)", map_name, score, text)
        return map_name
