#FROM ubuntu:18.04
FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04

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
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py &&\
    python3.8 get-pip.py

# add sudo
RUN apt-get update && \
    apt-get -y install sudo
RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo

# Nvidia Add Public Key
RUN apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/3bf863cc.pub &&\
    apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub

# python library
RUN sudo apt-get update -y &&\
    sudo apt-get upgrade -y &&\
    python3.8 -m pip install --upgrade pip &&\
    python3.8 -m pip install flask &&\
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
    python3.8 -m pip install wheel &&\
    python3.8 -m pip install sqlalchemy &&\
    sudo apt-get -y install libpq-dev &&\
    python3.8 -m pip install psycopg2 &&\
    python3.8 -m pip install dask[complete] &&\
    python3.8 -m pip install testfixtures &&\
    python3.8 -m pip install apscheduler &&\
    python3.8 -m pip install requests_oauthlib &&\
    python3.8 -m pip install tabulate &&\
    python3.8 -m pip install shape &&\
    python3.8 -m pip install statsmodels &&\
    python3.8 -m pip install cached-property &&\
    python3.8 -m pip install pandarallel &&\
    python3.8 -m pip install pytest &&\
    python3.8 -m pip install ipywidgets

# lightgbm
RUN sudo apt-get upgrade -y &&\
    sudo apt-get update -y &&\
    sudo apt-get install git &&\
    sudo apt-get -y install cmake &&\
    git clone --recursive https://github.com/microsoft/LightGBM ; cd LightGBM &&\
    mkdir build ; cd build &&\
    sudo apt-get -y install libboost-all-dev &&\
    cmake -DUSE_GPU=1 -DOpenCL_LIBRARY=/usr/local/cuda/lib64/libOpenCL.so -DOpenCL_INCLUDE_DIR=/usr/local/cuda/include/ .. &&\
    make -j4 &&\
    cd ../ &&\
    cd python-package &&\
    sudo python3.8 setup.py install --precompile &&\
    ## パスを通さないとOpenCL Device Not Foundと怒られる
    mkdir -p /etc/OpenCL/vendors && echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd

# language
RUN sudo apt-get -y update  &&\
    sudo apt-get -y install language-pack-ja &&\
    sudo update-locale LANG=ja_JP.UTF-8 &&\
    curl -L 'http://moji.or.jp/wp-content/ipafont/IPAfont/IPAfont00303.zip' > ipa.zip &&\
    unzip ipa.zip -d ./ipa &&\
    cp -r ./ipa/IPAfont00303 /usr/share/fonts/truetype/ &&\
    chmod 644 /usr/share/fonts/truetype/IPAfont00303 &&\
    rm -rf font.zip ipa

# 定時実行ジョブ
RUN sudo apt-get -y install cron

# Set environment variables.
ENV LANG ja_JP.UTF-8
ENV PYTHONIOENCODIND utf_8