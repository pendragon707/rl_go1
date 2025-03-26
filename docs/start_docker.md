Локально:
```
xhost +local:
docker run --rm -it -p 8082:8082 --ipc=host --net=host -v .:/workspace --volume=$HOME/.Xauthority:/root/.Xauthority:rw -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --privileged nonpenguin/rlgo1 bash
```
Внутри докера в директории `/home` запускаем:
```
./build.sh
```

Запускаем саму политику:
```
cd rl_go1
python scripts/policy.py --real --aliengo
```