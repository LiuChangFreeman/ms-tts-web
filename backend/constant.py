# -*- coding: utf-8 -*-
import os
import datetime
import time
import uuid
import asyncio
import hashlib

PATH_PREFIX = os.environ.get("PATH_PREFIX", "tts")
PATH_LIB = os.environ.get("LIB_PATH")
PATH_STORAGE = os.environ.get("STORAGE_PATH")

EXPIRE_SECONDS = 60*15
DEFAULT_LIMIT = "1 per 3 second"
KEY_SECRET = "tts19980731"

tts_styles = ["Default", "assistant", "chat", "customerservice", "newscast", "affectionate","angry", "calm", "cheerful", "disgruntled", "fearful", "gentle", "lyrical", "sad", "serious"]

MIN_VIDEO_HEIGHT = 720
VIDEO_WIDTH = 1280