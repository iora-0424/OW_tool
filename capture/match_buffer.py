from detector.map_comparator import MapComparator
from logger.logger import get_logger

logger = get_logger()



class MatchBuffer:
    """
    同一マッチの最後のスクリーンショットだけ保持する。
    """

    def __init__(
        self,
        comparator: MapComparator,
        threshold: float = 0.90,
    ):
        self.comparator = comparator
        self.threshold = threshold

        self.previous_frame = None

    def update(self, frame):
        """
        新しいスクリーンショットを受け取り、
        保存するべき画像があれば返す。

        Returns
        -------
        None
            保存不要

        ndarray
            保存する画像
        """

        # 初回
        if self.previous_frame is None:
            self.previous_frame = frame
            return None

        score = self.comparator.compare(
            self.previous_frame,
            frame,
        )
        logger.info(
            "Match similarity : %.4f",
            score,
        )

        if score >= self.threshold:
            # 同じマッチ
            self.previous_frame = frame
            return None

        # 違うマッチ
        save_frame = self.previous_frame
        self.previous_frame = frame

        return save_frame

    def flush(self):
        """
        プログラム終了時に最後の1枚を返す
        """

        frame = self.previous_frame
        self.previous_frame = None

        return frame