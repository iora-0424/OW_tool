import cv2
from skimage.metrics import structural_similarity as ssim

from logger.logger import get_logger

logger = get_logger()


# ======================================================
# ROI (1920x1080 Fullscreen)
# ======================================================

MAP_ROI_X = 1323
MAP_ROI_Y = 13
MAP_ROI_WIDTH = 420
MAP_ROI_HEIGHT = 42

# ======================================================
# Comparison
# ======================================================

SLIDE_RANGE = 10
COMPARE_WIDTH = MAP_ROI_WIDTH - (SLIDE_RANGE * 2)


class MapComparator:
    """
    スコアボード右上のマップ名を比較するクラス。

    前処理として
        ・CLAHE
        ・GaussianBlur
        ・Canny
    を適用し、暗転や明るさ変化の影響を軽減する。
    """

    def compare(self, frame1, frame2) -> float:

        roi1 = self._crop(frame1)
        roi2 = self._crop(frame2)

        img1 = self._preprocess(roi1)
        img2 = self._preprocess(roi2)

        score, offset = self._calculate_best_ssim(
            img1,
            img2,
        )

        logger.info(
            "Map similarity : %.4f (offset=%d)",
            score,
            offset,
        )

        return score

    def _crop(self, frame):

        return frame[
            MAP_ROI_Y:MAP_ROI_Y + MAP_ROI_HEIGHT,
            MAP_ROI_X:MAP_ROI_X + MAP_ROI_WIDTH,
        ]

    def _preprocess(self, roi):

        gray = cv2.cvtColor(
            roi,
            cv2.COLOR_BGR2GRAY,
        )

        # 明るさ補正
        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8),
        )

        gray = clahe.apply(gray)

        # 軽いノイズ除去
        gray = cv2.GaussianBlur(
            gray,
            (3, 3),
            0,
        )

        # 輪郭のみ抽出
        edge = cv2.Canny(
            gray,
            50,
            150,
        )

        return edge

    def _calculate_best_ssim(
        self,
        img1,
        img2,
    ):

        base = img1[
            :,
            SLIDE_RANGE:SLIDE_RANGE + COMPARE_WIDTH,
        ]

        best_score = -1.0
        best_offset = 0

        for offset in range(
            -SLIDE_RANGE,
            SLIDE_RANGE + 1,
        ):

            start = SLIDE_RANGE + offset

            target = img2[
                :,
                start:start + COMPARE_WIDTH,
            ]

            score = ssim(base, target)

            if score > best_score:
                best_score = score
                best_offset = offset

        return best_score, best_offset