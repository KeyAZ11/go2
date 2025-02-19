import json
import sys
import time
from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.sport.sport_client import SportClient

ChannelFactoryInitialize(0, "eth0")
sport_client = SportClient()
sport_client.SetTimeout(10.0)
sport_client.Init()

sport_client.StandUp()
time.sleep(1)
sport_client.BalanceStand()
time.sleep(1)
sport_client.Move(0.3, 0, 0)
time.sleep(1)
sport_client.Move(-0.3, 0, 0)
time.sleep(1)
sport_client.StandDown()
