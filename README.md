# rl_go1

## Установка через docker

1. Перед стартом, на хосте
```bash
git submodule update --init --recursive
```

2. Build docker
Внутри директории ```rl_go1``` запускаем
```bash
xhost si:localuser:root

docker-compose up --build
```

Дальше можно подключиться к запущенному контейнеру через bash (`docker attach`) или через VSCode.

## Установка без docker

После клонирования репозитория устанавливаем следующие зависимости, если не установлены:
```
conda create -n rl_go
conda activate rl_go
sudo snap install plotjuggler
pip install cbor2 mujoco
conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia
```
Далее подгружаем сабмодули:
```
git submodule update --init --recursive
pip install -e submodules/free-dog-sdk/
```
Затем нужно перейти к подмодулю с unitree_legged_sdk и выполнить readme оттуда (убедитесь, что установили lcm и остальные указанные там зависимости. 
```
cd submodules/unitree_legged_sdk
mkdir -p build
cd build
cmake ..
make 

cd submodules/unitree_legged_sdk/python_wrapper
mkdir -p build
cd build
cmake ..
make 
```

## Запуск скриптов и политик в симуляторе Mujoco

Скрипты из директории ./scripts без флагов запускаются в симуляторе mujoco. 

Поднятие робота на ноги в симуляторе mujoco:
```bash
python3 ./scripts/standup.py
```

Запуск политики в симуляторе mujoco: 
```python3 ./src/policy.py```

## Запуск скриптов и политик на Aliengo

Соедините ноутбук и робота Aliengo Ethernet-проводом. Если адрес порта автоматически был выставлен неверно, то устанавливаем Network->Wired->IPv4->Manual адрес 192.168.123.200 с маской 255.255.255.0.

Проверьте, что робот пингуется:

```ping 192.168.123.10```

Для запуска на Aliengo добавьте флаги `-r -a`.

Запуск политики на реальном роботе:  
```python3 ./src/policy.py -r -a```

## Возможные решения проблем

Проблемы с MESA для симмуляции [link](https://stackoverflow.com/questions/72110384/libgl-error-mesa-loader-failed-to-open-iris):
```
cd /home/$USER/miniconda/lib
mkdir backup  # Create a new folder to keep the original libstdc++
mv libstd* backup  # Put all libstdc++ files into the folder, including soft links
cp /usr/lib/x86_64-linux-gnu/libstdc++.so.6  ./ # Copy the c++ dynamic link library of the system here
ln -s libstdc++.so.6 libstdc++.so
ln -s libstdc++.so.6 libstdc++.so.6.0.19
```
