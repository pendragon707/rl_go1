FROM ubuntu:24.04
LABEL Name=rlgo1 Version=0.0.1

RUN apt-get update &&  apt-get install -y --no-install-recommends \
    git \
    curl \    
    lsb-release \    
    software-properties-common \
    wget \
    unzip \    
    python3-dev \
    python3-setuptools \
    &&  rm -rf /var/lib/apt/lists/*

# Install Glib and Cmake
RUN  apt update && apt install -y \
    build-essential \
    g++ \
    libglib2.0-dev \
    cmake \
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

# cuda
# RUN apt-get update && \
#     apt-get install -y wget mesa-utils python3-pip python-is-python3 && \
#     wget -qO - https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub | apt-key add - && \
#     echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /" >> /etc/apt/sources.list && \
#     apt-get update && \
#     apt-get install -y libcudnn8=8.9.7.29-1+cuda12.2 cuda-toolkit && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /root/miniconda.sh && \
    mkdir -p /root/.conda && \
    bash /root/miniconda.sh -b -p /root/miniconda3 && \
    rm -f miniconda.sh

RUN echo "export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6" >> ~/.bashrc

WORKDIR /home

ENV PATH=/root/miniconda3/bin:$PATH
COPY rl_go.yml .
RUN conda env create -n rl_go --file /home/rl_go.yml

COPY build.sh .
                
# RUN conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia

# COPY .. .

RUN ["chmod", "+x", "/home/build.sh"]
CMD ["/home/build.sh"]
