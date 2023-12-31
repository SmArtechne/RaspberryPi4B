# RaspberryPi4B

## 0. Default settings

### 0.1 Hardware specification

| Hardware            | Description                                                                                    |
| ------------------- | ---------------------------------------------------------------------------------------------- |
| Raspberry Pi 4B 4GB | Mini computer which Manage camera module and sensors, and send data to aws storage s3          |
| Picam module 3 wide | Features up to 4608x2592 resolution of image capture and 1920x1080 resolution of video capture |
| DHT 11              | Sensor module for arduino. measure temperature and humidity                                    |
| SD card             | Raspberry Pi's main storage. we used sandisk Ultra 64GB, which written with 'A1' Symbol        |

### 0.2 Hardware default settings

| program   | version  | Description                               |
| --------- | -------- | ----------------------------------------- |
| Debian OS | Bookworm | Raspberry Pi 64bit-OS, based on Debian OS |
| python    | 3.11.2   | Python                                    |
| opencv    | 4.8.1    | OpenCV                                    |

We used Raspberry Pi OS for out Raspberry 4B computer's OS, which basically features the picam module 3

## 1. Code analyze

### 1.1 main.py

[main.py](main.py)<br/>
[modules](requirements.txt)

| module_name  | description                                                      |
| ------------ | ---------------------------------------------------------------- |
| time         | Add delay                                                        |
| cv2          | Recognize face and mosaic                                        |
| picamera2    | Use PiCamera module in Python 3, Debian OS 12                    |
| datetime     | Get current timestamp                                            |
| cvlib        | Face detection library                                           |
| board        | Interface with hardware pins on Raspberry Pi                     |
| adafruit_dht | Adafruit DHT sensor library for temperature and humidity sensing |
| json         | JSON (JavaScript Object Notation) manipulation                   |
| os           | Operating system interface for file operations                   |
| boto3        | AWS SDK for Python (Boto3) - Amazon S3 operations                |
| PIL (Image)  | Python Imaging Library for image processing                      |

`main.py` file has 2 main functions

1. s3_connection()
   Used to connect to Amazon S3, and send files to it.

2. modify_img()
   Used to modify an image(resize into lower resolution, rotate, and add black-background to make it as 1:1 image).

3. others (not defined as function)
   The other codes are used to capture image, add mosaic and save, read sensor data and save as json, etc., to make files and send it to s3 and delete in local for space efficiency.

### 1.2 run_script.sh

[run_script.sh](run_script.sh)

created bash shell script file with named `run_script.sh` and change permissions with the follwing bash command.

```bash
sudo chmod +x run_script.sh
```

and modified system file to auto-start when boot.

```bash
# modify autostart file
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart
# add following command on the end of the file
bash ~/workspace/run_script.sh
```

The python program works within 1 minutes delay, including booting time and preparing time.
