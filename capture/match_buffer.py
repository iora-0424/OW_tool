class MatchBuffer:
    """
    同一マッチの最後のスクリーンショットだけ保持する。
    """

    def __init__(self):
        self.previous_frame = None
        self.previous_map_name = None

    def update(self, frame, map_name: str):
        """
        新しいスクリーンショットを受け取り、
        マップ名が変わった場合に、直前の画像とマップ名を返す。
        """

        previous_capture = None
        if self.previous_frame is not None and self.previous_map_name != map_name:
            previous_capture = (self.previous_frame, self.previous_map_name)
        self.previous_frame = frame
        self.previous_map_name = map_name

        return previous_capture

    def flush(self):
        """
        プログラム終了時に最後の画像とマップ名を返す。
        """

        if self.previous_frame is None:
            return None

        capture = (self.previous_frame, self.previous_map_name)
        self.previous_frame = None
        self.previous_map_name = None

        return capture
