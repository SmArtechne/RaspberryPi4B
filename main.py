import time
import cv2
from picamera2 import Picamera2
import datetime
import cvlib as cv
import board
import adafruit_dht as dht
import json
import os
import boto3
from PIL import Image


def s3_connection():
    try:
        # Establish a connection to Amazon S3
        s3 = boto3.client(
            service_name="",  # Specify the AWS service name (e.g., "s3")
            region_name="",  # Specify the AWS region (e.g., "us-west-2")
            aws_access_key_id="",  # Specify your AWS access key ID
            aws_secret_access_key="",  # Specify your AWS secret access key
        )
    except Exception as e:
        print(e)
    else:
        print("S3 bucket connected!")
        return s3


def modify_img(image_path, output_path, target_width, target_height):
    # Load the image
    img = Image.open(image_path)
    img = img.resize((640, 360))  # Resize the image to 640x360

    # Create a new image with a black background
    new_image = Image.new("RGB", (target_width, target_height), (0, 0, 0))

    # Place the image in the center of the new image
    x_offset = (target_width - img.width) // 2
    y_offset = (target_height - img.height) // 2
    new_image.paste(img, (x_offset, y_offset))
    img = new_image.rotate(-90, expand=True)  # Rotate the image by -90 degrees
    img.save(output_path)


# Establish a connection to Amazon S3
s3 = s3_connection()

# Initialize the face detector using the Haar Cascade classifier
face_detector = cv2.CascadeClassifier(
    "/usr/local/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
)

cv2.startWindowThread()

# Initialize the PiCamera2
picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(
        main={"format": "XRGB8888", "size": (4608, 2592)}  # Set the capture image size
    )
)

# Initialize the DHT-11 sensor
mydht11 = dht.DHT11(board.D3)

# Initialize variables for image resizing
new_width, new_height = 640, 360

while True:
    picam2.start()
    image = picam2.capture_array()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    faces = face_detector.detectMultiScale(gray, 1.1, 5)

    for x, y, w, h in faces:
        startX, startY = x, y
        endX, endY = x + w, y + h
        face_region = image[startY:endY, startX:endX]

        # Resize the face region
        B = face_region.shape[0]
        S = face_region.shape[1]
        face_region = cv2.resize(
            face_region, None, fx=0.05, fy=0.05, interpolation=cv2.INTER_AREA
        )
        face_region = cv2.resize(face_region, (S, B), interpolation=cv2.INTER_AREA)
        image[startY:endY, startX:endX] = face_region

    # Define paths and filenames based on the current timestamp
    origin_path = ""  # temp path
    suffix = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    img_path = origin_path + suffix + ".jpg"
    json_path = origin_path + suffix + ".json"

    # Save the captured image
    cv2.imwrite(img_path, image)

    # Modify and save the image with the specified width and height
    modify_img(img_path, img_path, 640, 640)

    try:
        # Capture temperature and humidity data
        data = {"temp": mydht11.humidity, "humi": mydht11.temperature}

        # Save the data to a JSON file
        with open(json_path, "w") as f:
            json.dump(data, f)

        # Set flag indicating successful JSON file creation
        j_count = 1
    except RuntimeError as error:
        print(error.args[0])
    finally:
        pass

    # Delay for 3 seconds
    time.sleep(3)

    try:
        # Upload the modified image to Amazon S3
        s3.upload_file(img_path, "", img_path)

        # Remove the local image file
        os.remove(img_path)

        # Upload JSON file if created
        if j_count == 1:
            s3.upload_file(json_path, "", json_path)
            os.remove(json_path)
    except Exception as e:
        print(e)

    # Reset the JSON file creation flag
    j_count = 0
