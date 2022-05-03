# 晓晓配音  
edge人工合成音同款，基于react+flask的网页版配音生成工具，可根据提供的文案在线生成.mp4字幕视频和.mp3音源  
后端api来源于[msspeech](https://github.com/alekssamos/msspeech)
## 安装方法
```bash
export GITHUB_HTTP_PORXY=https://ghproxy.com/
# 使用ghproxy加速代理克隆仓库
git clone $(echo ${GITHUB_HTTP_PORXY})https://github.com/LiuChangFreeman/ms-tts-web
cd ms-tts-web
# 不设置GITHUB_HTTP_PORXY参数则不启用加速，适用于海外机器构建
docker build --build-arg GITHUB_HTTP_PORXY=$GITHUB_HTTP_PORXY -t ms_tts_web . --rm --network=host
docker run --name my_edge_tts -d --net=host -v $YOUR_TEMP_FILES_DIR:/home/storage -e HOST=0.0.0.0 -e PORT=8080 ms_tts_web
#访问 http://YOUR_IP:8080
```