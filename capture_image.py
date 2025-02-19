import time
import os
import sys

from unitree_sdk2py.core.channel import ChannelFactoryInitialize
from unitree_sdk2py.go2.video.video_client import VideoClient

def capture_image():

    ChannelFactoryInitialize(0, "eth0")

    client = VideoClient()
    client.SetTimeout(3.0)
    client.Init()

    print("##################GetImageSample###################")
    code, data = client.GetImageSample()

    if code != 0:
        print("get image sample error. code:", code)
    else:
        imageName = "./img.jpg"
        print("ImageName:", imageName)

        with open(imageName, "+wb") as f:
            f.write(bytes(data))
    time.sleep(1)

if __name__ == "__main__":
    capture_image()