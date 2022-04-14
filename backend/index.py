# -*- coding: utf-8 -*-
from constant import *
import json
import os
from flask import Flask,request,Blueprint,session
from flask_session import Session
from flask_limiter import Limiter
from PIL import Image, ImageDraw, ImageFont
from msspeech import MSSpeech

api_main = Blueprint('api', __name__)
app = Flask(__name__)

app.config['SESSION_KEY_PREFIX']= "tts"
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=30)
Session(app)

limiter = Limiter(
    app,
    key_func=lambda :request.remote_addr,
    default_limits=[DEFAULT_LIMIT]
)

@app.errorhandler(429)
def ratelimit_handler(e):
    response={
        "success":False,
        "msg":"请求过快"
    }
    return json.dumps(response,ensure_ascii=False)

@app.before_request
def before_request(*args,**kwargs):
    uid = session.get("id", None)
    if not uid:
        uid=str(uuid.uuid4())
        session["id"]=uid

def get_storage_path(filename):
    return os.paht.join(PATH_STORAGE,filename)

def get_signed_url(filename):
    date = (datetime.datetime.now() + datetime.timedelta(hours=8)).strftime('%Y-%m-%d')
    uri="/{}/{}".format(date, filename)
    ts_expired=int(time.time())+EXPIRE_SECONDS
    rand=str(uuid.uuid4()).replace("-","")
    sign=hashlib.md5("{}-{}-{}-0-{}".format(uri,ts_expired,rand,KEY_SECRET).encode('utf-8')).hexdigest()
    url="./files{}?auth_key={}-{}-0-{}".format(uri,ts_expired,rand,sign)
    return url

async def tts_worker(text,rate,style,uid):
    try:
        mss = MSSpeech()
        await mss.set_voice("zh-CN-XiaoxiaoNeural")
        filename_mp3 = "{}.mp3".format(uid)
        await mss.set_rate(rate)
        await mss.set_pitch(0)
        await mss.set_volume(2)
        await mss.set_style(style)
        await mss.synthesize(text.strip(), get_storage_path(filename_mp3))
        return True
    except Exception as e:
        print(e)
        return False

@api_main.route('/ping')
def ping():
    return "pong"

@api_main.route('/generate',methods = ["POST"])
def generate():
    if request.method == 'POST':
        try:
            data = request.get_data(as_text=True)
            data = json.loads(data)
            text=data["text"]
            style=data["style"]
            rate=data["rate"]
            assert style in tts_styles
            assert type(rate)==int
            assert len(text)<=150
            uid=str(uuid.uuid4())
            loop = asyncio.get_event_loop()
            result=loop.run_until_complete(tts_worker(text,rate,style,uid))
            if result:
                filename_mp3="{}.mp3".format(uid)
                font_size = 60
                font_width = font_size + 8
                
                path_font=os.path.join(PATH_LIB,'bin','pingfang.ttf')
                font = ImageFont.truetype(path_font, font_size)
                color = "#000000"
                img = Image.new('RGB', (1080, 0), (255, 255, 255))
                draw = ImageDraw.Draw(img)
                
                total_lines = []
                padding=font_width*3
                current_line = ""
                current_line_width = padding
                text += " "
                for char in text:
                    width = draw.textsize(char, font)[0]
                    if current_line_width + width > VIDEO_WIDTH-padding:
                        flag = True
                    elif char == "\n":
                        flag = True
                    elif text.index(char) == len(text) - 1 and current_line != "":
                        flag = True
                    else:
                        flag = False
                    if flag:
                        total_lines.append(current_line)
                        current_line = char
                        current_line_width = padding+width
                    else:
                        current_line_width += width
                        current_line += char
                
                video_height=720
                y_start=0
                current_height=font_width * len(total_lines)
                if current_height<MIN_VIDEO_HEIGHT:
                    video_height=MIN_VIDEO_HEIGHT
                    y_start=(MIN_VIDEO_HEIGHT-current_height+font_width)/2-font_width
                img = Image.new('RGB', (VIDEO_WIDTH, video_height), (255, 255, 255))
                draw = ImageDraw.Draw(img)
                for i in range(len(total_lines)):
                    current_line=total_lines[i]
                    current_line_width=len(current_line)*font_width
                    if current_line_width>= VIDEO_WIDTH-padding*2:
                        draw.text(xy=(padding, y_start+font_width * i), text=current_line, fill=color, font=font)
                    else:
                        x_offset=int((VIDEO_WIDTH-padding*2-current_line_width)/2)
                        draw.text(xy=(x_offset+padding, y_start+font_width * i), text=current_line, fill=color, font=font)
                filename_image= "{}.jpg".format(str(uuid.uuid4()))
                img.save(get_storage_path(filename_image))

                ts_expired=int(time.time())+EXPIRE_SECONDS
                response={
                    "success":True,
                    "data":{
                        "audio":get_signed_url(filename_mp3),
                        "expires_in":ts_expired
                    }
                }

                filename_video = "{}.mp4".format(str(uuid.uuid4()))
                os.system("ffmpeg -y -r 1 -i {} -i {} -absf aac_adtstoasc {}".format(get_storage_path(filename_image),get_storage_path(filename_mp3),get_storage_path(filename_video)))
                if os.path.exists(filename_video):
                    stat_info = os.stat(filename_video)
                    file_szie=stat_info.st_size
                    if file_szie>0:
                        response["data"]["video"]=get_signed_url(filename_video)
            else:
                response={
                    "success":False,
                    "msg":"生成失败"
                }
        except Exception as e:
            response={
                "success":False,
                "msg":str(e)
            }
    return json.dumps(response,ensure_ascii=False)

app.register_blueprint(api_main, url_prefix="/{}".format(PATH_PREFIX))

def handler(environ, start_response):
    return app(environ, start_response)

if __name__ == "__main__":
    port = os.environ.get("FC_SERVER_PORT", "9000")
    app.run(host="0.0.0.0",port=int(port))