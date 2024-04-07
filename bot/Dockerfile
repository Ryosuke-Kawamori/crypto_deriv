FROM ubuntu:18.04

# python
RUN apt-get update -y &&\
    apt autoremove &&\
    apt-get install -y --no-install-recommends \
        vim git less wget \
        build-essential \
        libatlas-base-dev \
        python3.8 \
        python3.8-distutils\
        python3.8-dev python3-setuptools \
        python3-scipy python3-h5py \
        curl &&\
     apt-get clean &&\
     rm -rf /var/lib/apt/lists*

## pipの導入
RUN apt-get update -y &&\
    apt-get install curl &&\
    curl -kL https://bootstrap.pypa.io/get-pip.py | python3.8

# add sudo
RUN apt-get update && \
    apt-get -y install sudo
RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo

# python library
RUN sudo apt-get update -y &&\
    sudo apt-get upgrade -y &&\
    python3.8 -m pip install --upgrade pip &&\
    python3.8 -m pip install schedule &&\
    python3.8 -m pip install selenium &&\
    python3.8 -m pip install urllib3 &&\
    python3.8 -m pip install beautifulsoup4 &&\
    python3.8 -m pip install tqdm &&\
    python3.8 -m pip install pytz &&\
    python3.8 -m pip install python-dateutil &&\
    python3.8 -m pip install lxml &&\
    python3.8 -m pip install numpy &&\
    python3.8 -m pip install pandas &&\
    python3.8 -m pip install jupyterlab &&\
    python3.8 -m pip install matplotlib &&\
    python3.8 -m pip install seaborn &&\
    python3.8 -m pip install progressbar2 &&\
    python3.8 -m pip install Cython &&\
    python3.8 -m pip install -U scikit-learn &&\
    python3.8 -m pip install dask[complete] &&\
    python3.8 -m pip install requests_oauthlib &&\
    python3.8 -m pip install tabulate &&\
    python3.8 -m pip install shape &&\
    python3.8 -m pip install statsmodels &&\
    python3.8 -m pip install cached-property &&\
    python3.8 -m pip install pytest

# language
RUN sudo apt-get -y update  &&\
    sudo apt-get -y install language-pack-ja &&\
    sudo apt-get -y install unzip &&\
    sudo update-locale LANG=ja_JP.UTF-8

# discord
RUN python3.8 -m pip install discord

# 定時実行ジョブ
RUN sudo apt-get -y install cron

# Set environment variables.
ENV LANG ja_JP.UTF-8
ENV PYTHONIOENCODIND utf_8