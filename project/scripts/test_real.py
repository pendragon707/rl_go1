import time
from project.proxy.go_proxy import import RealGo1


conn = RealGo1()
conn.start()

cycles = 0
while True:
    s = conn.get_latest_state()
    if s is not None and cycles > 100:
        cycles = 0
    cycles += 1
    time.sleep(0.01)
