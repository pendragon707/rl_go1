# rl_go1

После клонирования репозитория устанавливаем следующие зависимости, если не установлены:
```
conda create --name rl_go
conda activate rl_go
sudo snap install plotjuggler
pip install cbor2 mujoco crcmod pynput==1.5.0
conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia
```

Далее подгружаем сабмодули:
```
git submodule update --init --recursive
pip install -e submodules/free-dog-sdk/
```
Если хотим запускать в симуляторе, то изменяем в standup.py real = False, если на реальном роботе, то real = True

Запускаем код поднятия робота:
```
python3 ./scripts/standup.py
```
Если выдает ошибку, то попробуйте следующую команду и повторите предыдущую команду:
```
export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6
```

Проблемы с MESA для симмуляции [link](https://stackoverflow.com/questions/72110384/libgl-error-mesa-loader-failed-to-open-iris):
```
cd /home/$USER/miniconda/lib
mkdir backup  # Create a new folder to keep the original libstdc++
mv libstd* backup  # Put all libstdc++ files into the folder, including soft links
cp /usr/lib/x86_64-linux-gnu/libstdc++.so.6  ./ # Copy the c++ dynamic link library of the system here
ln -s libstdc++.so.6 libstdc++.so
ln -s libstdc++.so.6 libstdc++.so.6.0.19
```
