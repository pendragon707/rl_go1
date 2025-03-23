Локально:
```
xhost +local:
docker run --rm -it --ipc=host -p 8082:8082 --net=host -v .:/workspace --volume=$Home/.Xauthority:/root/.Xauthority:rw -e DISPLAY=:1.0 -v /tmp/.X11-unix:/tmp/.X11-unix --privileged nonpenguin/rlgo1 bash
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