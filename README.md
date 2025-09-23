# rl_go1

## Установка через docker

1. Перед стартом, на хосте
```bash
git submodule update --init --recursive
```

2. Build docker
Внутри директории ```rl_go1``` запускаем
```bash
docker build -t rl_go -f docker/Dockerfile .
```

3. Start Docker
Внутри директории ```rl_go1```

```bash
xhost si:localuser:root

docker run --rm -it -p 8082:8082 --ipc=host --net=host -v .:/workspace/rl_go1 --volume=$HOME/.Xauthority:/root/.Xauthority:rw 
-e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --privileged rl_go bash
```
Дальше можно подключиться к запущенному контейнеру через bash (`docker attach`) или через VSCode.

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
