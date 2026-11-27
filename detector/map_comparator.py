import cv2
from skimage.metrics import structural_similarity as ssim

from config.settings import ImageConfig, MatchConfig, ROIConfig
from logger.logger import get_logger

logger = get_logger()


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
            ROIConfig.MAP_Y:ROIConfig.MAP_Y + ROIConfig.MAP_HEIGHT,
            ROIConfig.MAP_X:ROIConfig.MAP_X + ROIConfig.MAP_WIDTH,
        ]

    def _preprocess(self, roi):

        gray = cv2.cvtColor(
            roi,
            cv2.COLOR_BGR2GRAY,
        )

        # 明るさ補正
        clahe = cv2.createCLAHE(
            clipLimit=ImageConfig.CLAHE_CLIP_LIMIT,
            tileGridSize=ImageConfig.CLAHE_TILE_GRID_SIZE,
        )

        gray = clahe.apply(gray)

        # 軽いノイズ除去
        gray = cv2.GaussianBlur(
            gray,
            MatchConfig.BLUR_KERNEL,
            0,
        )

        # 輪郭のみ抽出
        edge = cv2.Canny(
            gray,
            ImageConfig.CANNY_LOW_THRESHOLD,
            ImageConfig.CANNY_HIGH_THRESHOLD,
        )

        return edge

    def _calculate_best_ssim(
        self,
        img1,
        img2,
    ):

        slide_range = MatchConfig.SLIDE_RANGE
        compare_width = ROIConfig.MAP_WIDTH - 2 * slide_range
        base = img1[
            :,
            slide_range:slide_range + compare_width,
        ]

        best_score = -1.0
        best_offset = 0

        for offset in range(
            -slide_range,
            slide_range + 1,
        ):

            start = slide_range + offset

            target = img2[
                :,
                start:start + compare_width,
            ]

            score = ssim(base, target)

            if score > best_score:
                best_score = score
                best_offset = offset

        return best_score, best_offset