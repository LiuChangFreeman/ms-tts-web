# -*- coding: utf-8 -*-
from constant import *
import json
import os
from flask import Flask, request, Blueprint, session, render_template,send_from_directory
from flask_session import Session
from flask_limiter import Limiter
from PIL import Image, ImageDraw, ImageFont
from msspeech import MSSpeech


app = Flask(__name__)
app.secret_key=KEY_SECRET 
app.debug=True
api_main = Blueprint('main', __name__)
api_static = Blueprint('static', __name__,template_folder=PATH_FRONTEND_ASSERTS,static_folder=PATH_FRONTEND_ASSERTS)

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=[DEFAULT_LIMIT]
)


@app.errorhandler(429)
def ratelimit_handler(e):
    response = {
        "success": False,
        "msg": "请求过快"
    }
    return json.dumps(response, ensure_ascii=False)


@app.before_request
def before_request(*args, **kwargs):
    uid = session.get("id", None)
    if not uid:
        uid = str(uuid.uuid4())
        session["id"] = uid

def get_date():
    return (datetime.datetime.now()).strftime('%Y-%m-%d')

def get_storage_path(filename):
    return os.path.join(PATH_STORAGE,get_date(),filename)


def get_signed_url(filename):
    date = get_date()
    uri = "/files/{}/{}".format(date, filename)
    ts_expired = int(time.time())+EXPIRE_SECONDS
    rand = str(uuid.uuid4()).replace("-", "")
    sign = hashlib.md5("{}-{}-{}-0-{}".format(uri, ts_expired,
                                              rand, KEY_SECRET).encode('utf-8')).hexdigest()
    url = "{}?auth_key={}-{}-0-{}".format(uri, ts_expired, rand, sign)
    return url


async def tts_worker(text, rate, style, uid):
    try:
        mss = MSSpeech()
        await mss.set_voice("zh-CN-XiaoxiaoNeural")
        filename_mp3 = "{}.mp3".format(uid)
        await mss.set_rate(rate)
        await mss.set_pitch(0)
        await mss.set_volume(2)
        await mss.set_style(style)
        folder=os.path.join(PATH_STORAGE,get_date())
        if not os.path.exists(folder):
            os.mkdir(folder)
        filepath=get_storage_path(filename_mp3)
        print(filepath)
        await mss.synthesize(text.strip(), filepath)
        return True
    except Exception as e:
        print(e)
        return False


@api_main.route('/ping')
def ping():
    return "pong"


@api_main.route('/generate', methods=["POST"])
def generate():
    if request.method == 'POST':
        try:
            data = request.get_data(as_text=True)
            data = json.loads(data)
            text = data["text"]
            style = data["style"]
            rate = data["rate"]
            assert style in tts_styles
            assert type(rate) == int
            assert len(text) <= 150
            uid = str(uuid.uuid4())
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(tts_worker(text, rate, style, uid))
            if result:
                filename_mp3 = "{}.mp3".format(uid)

                path_font = os.path.join(PATH_LIB, 'bin', 'pingfang.ttf')
                font = ImageFont.truetype(path_font, FONT_SIZE)
                color = "#000000"
                img = Image.new('RGB', (1080, 0), (255, 255, 255))
                draw = ImageDraw.Draw(img)

                total_lines = []
                current_line = ""
                current_line_width = LINE_PADDING
                text += " "
                for char in text:
                    width = draw.textsize(char, font)[0]
                    if current_line_width + width > VIDEO_WIDTH-LINE_PADDING:
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
                        current_line_width = LINE_PADDING+width
                    else:
                        current_line_width += width
                        current_line += char

                video_height = 720
                y_start = 0
                current_height = FONT_WIDTH * len(total_lines)
                if current_height < MIN_VIDEO_HEIGHT:
                    video_height = MIN_VIDEO_HEIGHT
                    y_start = (MIN_VIDEO_HEIGHT-current_height +
                               FONT_WIDTH)/2-FONT_WIDTH
                img = Image.new(
                    'RGB', (VIDEO_WIDTH, video_height), (255, 255, 255))
                draw = ImageDraw.Draw(img)
                for i in range(len(total_lines)):
                    current_line = total_lines[i]
                    current_line_width = len(current_line)*FONT_WIDTH
                    if current_line_width >= VIDEO_WIDTH-LINE_PADDING*2:
                        draw.text(xy=(LINE_PADDING, y_start+FONT_WIDTH * i),
                                  text=current_line, fill=color, font=font)
                    else:
                        x_offset = int(
                            (VIDEO_WIDTH-LINE_PADDING*2-current_line_width)/2)
                        draw.text(xy=(x_offset+LINE_PADDING, y_start+FONT_WIDTH * i),
                                  text=current_line, fill=color, font=font)
                filename_image = "{}.jpg".format(str(uuid.uuid4()))
                img.save(get_storage_path(filename_image))

                ts_expired = int(time.time())+EXPIRE_SECONDS
                response = {
                    "success": True,
                    "data": {
                        "audio": get_signed_url(filename_mp3),
                        "expires_in": ts_expired
                    }
                }

                filename_video = "{}.mp4".format(str(uuid.uuid4()))
                filepath_video=get_storage_path(filename_video)
                os.system("ffmpeg -y -r 1 -i {} -i {} -absf aac_adtstoasc {}".format(get_storage_path(filename_image), get_storage_path(filename_mp3), filepath_video))
                if os.path.exists(filepath_video):
                    stat_info = os.stat(filepath_video)
                    file_szie = stat_info.st_size
                    if file_szie > 0:
                        response["data"]["video"] = get_signed_url(filename_video)
            else:
                response = {
                    "success": False,
                    "msg": "生成失败"
                }
        except Exception as e:
            response = {
                "success": False,
                "msg": str(e)
            }
    return json.dumps(response, ensure_ascii=False)

@api_static.route('/')
@limiter.exempt
def index():
    return render_template('index.html')

@api_static.route('/<path:filename>')
@limiter.exempt
def return_static_files(filename):
    return send_from_directory(PATH_FRONTEND_ASSERTS,filename,as_attachment=True)

@app.route("/files/<path:filepath>")
@limiter.exempt
def download_file(filepath):
    auth_key=request.args.get("auth_key",None)
    assert auth_key!=None
    groups=auth_key.split("-")
    assert len(groups)==4
    ts_expired, rand, sign=groups[0], groups[1], groups[3]
    assert ts_expired<=int(time.time())
    uri="/files/{}".format(filepath.strip("/"))
    hash = hashlib.md5("{}-{}-{}-0-{}".format(uri, ts_expired,rand, KEY_SECRET).encode('utf-8')).hexdigest()
    assert sign==hash
    date,filename=filepath.strip("/").split('/')
    directory=os.path.join(PATH_STORAGE, date)
    print(directory,filename)
    return send_from_directory(directory,filename,as_attachment=True)

app.register_blueprint(api_main, url_prefix="/tts")
app.register_blueprint(api_static)

if __name__ == "__main__":
    host=os.environ.get("HOST","0.0.0.0")
    port=int(os.environ.get("PORT",7031))
    app.run(host=host, port=port)
