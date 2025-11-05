from dotenv import load_dotenv
import os
import logging

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Logging config for the small CLI (lightweight)
    LOG_LEVEL = os.getenv("MLA_LOG_LEVEL", "INFO")
    @classmethod
    def get_logger(cls, name: str = __name__):
        logger = logging.getLogger(name)
        if not logger.handlers:
            level = getattr(logging, cls.LOG_LEVEL.upper(), logging.INFO)
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(level)
        return logger

    @classmethod
    def validate(cls):
        if not cls.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY missing. Run setup.ps1 and enter your key.")