FROM ubuntu:24.04
LABEL Name=rl_go1 Version=0.0.1

RUN apt-get update &&  apt-get install -y --no-install-recommends \
    git \
    curl \    
    lsb-release \    
    software-properties-common \
    wget \
    unzip \    
    iputils-ping \
    vim \ 
    python3-dev \
    python3-setuptools \
    &&  rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    cmake \
    libxkbcommon0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    libgbm1 \
    mesa-utils \
    &&  rm -rf /var/lib/apt/lists/*

# Install Glib and Cmake
RUN apt update && apt install -y \
    build-essential \
    g++ \
    libglib2.0-dev \
    # cmake \
    libboost-all-dev \
    libmsgpack* \
    &&  rm -rf /var/lib/apt/lists/*

# Install lcm >=1.4.0
RUN wget https://github.com/lcm-proj/lcm/archive/refs/tags/v1.5.0.zip && \
    unzip v1.5.0.zip && \
    mv lcm-1.5.0 lcm && \
    cd lcm && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make && \
      make install && \
    cd ../lcm-python && \
      python3 setup.py install

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /root/miniconda.sh && \
    mkdir -p /root/.conda && \
    bash /root/miniconda.sh -b -p /root/miniconda3 && \
    rm -f miniconda.sh

ENV PATH=/root/miniconda3/bin:$PATH
RUN conda tos accept --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --channel https://repo.anaconda.com/pkgs/r

RUN conda create -n rl_go 

ARG PYTORCH_CUDA_VERSION=12.1
ENV PYTORCH_CUDA_VERSION=${PYTORCH_CUDA_VERSION}

ENV CONDA_DEFAULT_ENV=rl_go
ENV CONDA_PREFIX=/root/miniconda3/envs/rl_go
ENV PATH=/root/miniconda3/envs/rl_go/bin:/root/miniconda3/bin:$PATH

# Source conda.sh to enable `conda activate`
RUN . /root/miniconda3/etc/profile.d/conda.sh && \
    conda activate rl_go && \
    conda install -y \
        pytorch torchvision torchaudio pytorch-cuda=${PYTORCH_CUDA_VERSION} \
        -c pytorch -c nvidia && \
    pip install cbor2 mujoco crcmod

RUN echo "export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6" >> ~/.bashrc
RUN echo "source /root/miniconda3/bin/activate" >> ~/.bashrc
RUN echo "conda init" >> ~/.bashrc
RUN echo "conda activate rl_go" >> ~/.bashrc

WORKDIR /workspace

COPY docker/build.sh .

RUN ["chmod", "+x", "/workspace/build.sh"]
RUN "/workspace/build.sh"
