#!/bin/bash

source /root/miniconda3/bin/activate
conda activate rl_go

cd /home/rl_go
git submodule update --init --recursive
pip install -e submodules/free-dog-sdk

cd /home/rl_go1/submodules/unitree_legged_sdk
mkdir -p build
cd build
cmake ..
make 

cd /home/rl_go1/submodules/unitree_legged_sdk/python_wrapper
mkdir build
cd build
cmake ..
make 

sudo ldconfig -v

