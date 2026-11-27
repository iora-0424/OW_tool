import logging
from config.settings import PathConfig


def get_logger():

    PathConfig.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("OWLogger")

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    #
    # コンソール
    #
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)

    #
    # ファイル
    #
    file = logging.FileHandler(
        PathConfig.LOG_FILE,
        encoding="utf-8"
    )

    file.setLevel(logging.DEBUG)
    file.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file)

    return logger