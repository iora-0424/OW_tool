import logging
import os


def get_logger():

    os.makedirs("logs", exist_ok=True)

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
        "logs/ow_logger.log",
        encoding="utf-8"
    )

    file.setLevel(logging.DEBUG)
    file.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(file)

    return logger