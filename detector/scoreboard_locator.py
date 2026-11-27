import cv2
from dataclasses import dataclass

from config.settings import ScoreboardConfig


@dataclass
class MatchResult:
    matched: bool
    score: float
    location: tuple[int, int]


class ScoreboardLocator:
    def __init__(
        self,
        template_path: str,
        threshold: float = ScoreboardConfig.DEFAULT_HEADER_THRESHOLD,
    ):
        """
        template_path : ヘッダーテンプレート画像
        threshold     : 一致率
        """

        self.threshold = threshold

        self.template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

        if self.template is None:
            raise FileNotFoundError(template_path)

        self.template_h, self.template_w = self.template.shape

    def detect(self, frame) -> MatchResult:
        """
        frame : BGR画像(cv2.imreadやmssで取得した画像)

        return:
            MatchResult
        """

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        result = cv2.matchTemplate(
            gray,
            self.template,
            cv2.TM_CCOEFF_NORMED
        )

        _, max_score, _, max_loc = cv2.minMaxLoc(result)

        return MatchResult(
            matched=max_score >= self.threshold,
            score=max_score,
            location=max_loc
        )

    def draw_debug(self, frame, match: MatchResult):
        """
        検出位置を描画する
        """

        x, y = match.location

        cv2.rectangle(
            frame,
            (x, y),
            (x + self.template_w, y + self.template_h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"{match.score:.3f}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        return frame