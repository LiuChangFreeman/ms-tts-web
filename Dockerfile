FROM python:3.7.4-slim-stretch
ENV HOST=0.0.0.0
ENV PORT=7031
ENV WORK_DIR=/home/tts
ENV LIB_PATH=/home/tts/lib
ENV STORAGE_PATH=/home/storage
ENV NODE_VERSION=v16.14.2
ENV PATH=/usr/local/lib/nodejs/node-$NODE_VERSION-linux-x64/bin:$PATH
ARG GITHUB_HTTP_PORXY=

VOLUME [$STORAGE_PATH]
EXPOSE 9000/tcp

ADD container/sources.list /etc/apt/sources.list
RUN mkdir -p $LIB_PATH
RUN apt-get update && \
    apt-get install -y wget unzip xz-utils

# Install python library
COPY backend $WORK_DIR/backend
WORKDIR $WORK_DIR/backend
RUN pip install -r requirements.txt -t $LIB_PATH -i https://mirrors.aliyun.com/pypi/simple/ --upgrade && \
    chmod +x bootstrap

# Build frontend
COPY frontend $WORK_DIR/frontend
WORKDIR $WORK_DIR/frontend
RUN mkdir /usr/local/lib/nodejs && \
    wget https://nodejs.org/dist/$NODE_VERSION/node-$NODE_VERSION-linux-x64.tar.xz && \
    tar -xJvf node-$NODE_VERSION-linux-x64.tar.xz -C /usr/local/lib/nodejs && \
    rm -rf node-$NODE_VERSION-linux-x64.tar.xz
RUN npm install yarn -g  && \
    yarn config set registry https://registry.npm.taobao.org  && \
    yarn && \
    npm run build && \
    rm -rf $WORK_DIR/frontend/node_modules && \
    rm -rf /usr/local/share/.cache/yarn

# Install pinfang font
RUN wget $(echo ${GITHUB_HTTP_PORXY})https://github.com/LiuChangFreeman/ms-tts-web/releases/download/asserts/pingfang.ttf && \
    mv pingfang.ttf $LIB_PATH/bin/

# Install ffmpeg
RUN wget $(echo ${GITHUB_HTTP_PORXY})https://github.com/LiuChangFreeman/ms-tts-web/releases/download/asserts/ffmpeg.zip && \
    unzip ffmpeg.zip && \
    rm -rf ffmpeg.zip && \
    mv ffmpeg /usr/local/bin/ && \
    chmod +x /usr/local/bin/ffmpeg

WORKDIR $WORK_DIR/backend
ENTRYPOINT ["/bin/bash","bootstrap"]