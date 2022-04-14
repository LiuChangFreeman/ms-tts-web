# -*- coding: utf-8 -*-
import os
import datetime
import time
import uuid
import asyncio
import hashlib

PATH_LIB = os.environ.get("LIB_PATH","/home/tts/lib")
PATH_STORAGE = os.environ.get("STORAGE_PATH","/home/storage")
PATH_FRONTEND_ASSERTS="../frontend/dist"

EXPIRE_SECONDS = 60*15
DEFAULT_LIMIT = "1 per 3 second"
KEY_SECRET = "tts19980731"

tts_styles = ["Default", "assistant", "chat", "customerservice", "newscast", "affectionate","angry", "calm", "cheerful", "disgruntled", "fearful", "gentle", "lyrical", "sad", "serious"]

MIN_VIDEO_HEIGHT = 720
VIDEO_WIDTH = 1280
FONT_SIZE = 60
FONT_WIDTH = FONT_SIZE + 8
LINE_PADDING = FONT_WIDTH*3