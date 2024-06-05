from pathlib import Path
import sys

from loguru import logger

logger.remove() 
logger.add(sys.stderr, level="INFO")

logger.add("cloud_shield_ai.log", rotation="00:00", level="INFO")


output_folder = Path(__file__).parent / "output"