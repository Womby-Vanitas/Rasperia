import mycamera
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.metrics import MeanSquaredError
from gpiozero import DigitalOutputDevice
from gpiozero import PWMOutputDevice

PWMA = PWMOutputDevice(18)
AIN1 = DigitalOutputDevice(22)
AIN2 = DigitalOutputDevice(27)

PWMB = PWMOutputDevice(23)
BIN1 = DigitalOutputDevice(25)
BIN2 = DigitalOutputDevice(24)

def motor_go(speed):
    AIN1.value = 0
    AIN2.value = 1
    PWMA.value = speed+0.02
    BIN1.value = 0
    BIN2.value = 1
    PWMB.value = speed+0.02

def motor_back(speed):
    AIN1.value = 1
    AIN2.value = 0
    PWMA.value = speed
    BIN1.value = 1
    BIN2.value = 0
    PWMB.value = speed
    
def motor_left(speed):
    AIN1.value = 1
    AIN2.value = 0
    PWMA.value = 0.0
    BIN1.value = 0
    BIN2.value = 1
    PWMB.value = speed
    
def motor_right(speed):
    AIN1.value = 0
    AIN2.value = 1
    PWMA.value = speed
    BIN1.value = 1
    BIN2.value = 0
    PWMB.value = 0.0

def motor_stop():
    AIN1.value = 0
    AIN2.value = 1
    PWMA.value = 0.0
    BIN1.value = 1
    BIN2.value = 0
    PWMB.value = 0.0

speedSet = 0.38

def img_preprocess(image):
    height, _, _ = image.shape
    image = image[int(height/2):,:,:]
    image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
    image = cv2.GaussianBlur(image, (3,3), 0)
    image = cv2.resize(image, (200,66)) 
    image = image / 255
    return image

def main():
    camera = mycamera.MyPiCamera(640,480)
    model_path = '/home/pi/AI_CAR/model/lane_navigation_final.h5'
    model = load_model(model_path, custom_objects={'mse': MeanSquaredError()})
    
    carState = "stop"
    
    while( camera.isOpened()):
        
        keValue = cv2.waitKey(1)
        
        if keValue == ord('q') :
            break
        elif keValue == 82 :
            print("go")
            carState = "go"
        elif keValue == 84 :
            print("stop")
            carState = "stop"
        
        _, image = camera.read()
        image = cv2.flip(image,-1)
        cv2.imshow('Original', image)
        
        preprocessed = img_preprocess(image)
        cv2.imshow('pre', preprocessed)
        
        X = np.asarray([preprocessed])
        steering_angle = int(model.predict(X)[0])
        print("predict angle:",steering_angle)
        
        if carState == "go":
            if steering_angle >= 80 and steering_angle <= 92:
                print("go")
                motor_go(speedSet)
            elif steering_angle > 92:
                print("right")
                motor_right(speedSet)
            elif steering_angle < 80:
                print("left")
                motor_left(speedSet)
        elif carState == "stop":
            motor_stop()
        
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    main()
    PWMA.value = 0.0
    PWMB.value = 0.0

