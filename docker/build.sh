#!/bin/bash

cd /home/rl_go1/submodules/unitree_legged_sdk
rm -rf build
mkdir -p build
cd build
cmake ..
make 

cd /home/rl_go1/submodules/unitree_legged_sdk/python_wrapper
rm -rf build
mkdir build
cd build
cmake ..
make 

ldconfig -v