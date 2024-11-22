```bash
sudo apt install g++ libeigen3-dev make minizip ffmpeg
sudo ln -s /usr/lib/x86_64-linux-gnu/libdl.so.2 /usr/lib/x86_64-linux-gnu/libdl.so

conda create --name cms python=3.9
conda activate cms

# Это вне директории rl_go1
export LOCAL_INSTALL=$(pwd)/raisim_build

cd rl_go1/submodules/raisimLib

export WORKSPACE=$(pwd)
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$WORKSPACE/raisim/linux/lib
export PYTHONPATH=$PYTHONPATH:$WORKSPACE/raisim/linux/lib:$WORKSPACE/raisimGymTorch

cp path_to/activation.raisim $WORKSPACE/rsc

# Build raisim
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=$LOCAL_INSTALL -DRAISIM_EXAMPLE=ON -DRAISIM_PY=ON -DPYTHON_EXECUTABLE=$(which python)
make install -j4

# Install go1
cd raisimGymTorch
pip install -e .

# Train 1-stage
cd raisimGymTorch/env/envs/rsg_go1_task
python runner.py --name random --gpu 1 --exptid 1 --cpu --overwrite

# Train 2-stage
#  exptid - номер папки в которую запишуштся результаты,
#  loaid - номер политики, которую нужно взять из этапа 1:
python dagger.py --name cms_dagger --exptid 1 --loadpth ../../../../data/rsg_go1_task/0001 --loadid 0 --gpu 1


# Визуализация, 0 - номер политики:
python viz_policy.py ../../../../data/dagger_ckpt/0001 0
```