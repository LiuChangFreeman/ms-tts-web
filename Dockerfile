FROM python:3.7.4-slim-stretch
ENV GITHUB_HTTP_PORXY=https://ghproxy.com
ENV WORK_DIR=/home/tts
ENV LIB_PATH=/home/tts/lib
ENV STORAGE_PATH=/home/storage
ENV NODE_VERSION=v16.14.2
ENV PATH=/usr/local/lib/nodejs/node-$NODE_VERSION-linux-x64/bin:$PATH

VOLUME [$STORAGE_PATH]
EXPOSE 9000/tcp

RUN mkdir -p $LIB_PATH $WORK_DIR $WORK_DIR/fronted $WORK_DIR/backend
ADD container/sources.list /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y wget unzip xz-utils

# Install ffmpeg
RUN wget $GITHUB_HTTP_PORXY/https://github.com/LiuChangFreeman/ms-tts-web/releases/download/asserts/ffmpeg.zip
RUN unzip ffmpeg.zip
RUN rm ffmpeg.zip
RUN mv ffmpeg /usr/local/bin/
RUN wget chmod +x /usr/local/bin/ffmpeg

# Build fronted
WORKDIR $WORK_DIR/fronted
ADD fronted/ $WORK_DIR/fronted/
RUN mkdir mkdir /usr/local/lib/nodejs
RUN wget https://nodejs.org/dist/$NODE_VERSION/node-$NODE_VERSION-linux-x64.tar.xz
RUN tar -xJvf node-$NODE_VERSION-linux-x64.tar.xz -C /usr/local/lib/nodejs
RUN npm install tyarn -g
RUN tyarn
RUN npm run build

# Install python library
WORKDIR $WORK_DIR/backend
ADD backend/ $WORK_DIR/backend/
RUN pip install -r requirements.txt -t $LIB_PATH -i https://mirrors.aliyun.com/pypi/simple/ --upgrade
RUN chmod +x bootstrap

# Install pinfang font
RUN wget $GITHUB_HTTP_PORXY/https://github.com/LiuChangFreeman/ms-tts-web/releases/download/asserts/pingfang.ttf
RUN mv pingfang.ttf $LIB_PATH/bin/

ENTRYPOINT ["/bin/bash","bootstrap"]