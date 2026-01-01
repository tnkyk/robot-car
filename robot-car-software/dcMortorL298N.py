from time import sleep
import pigpio
import time
import pimygpio
from pigpio import pi

def setupL298N(myPi: pi):
    myPi.set_mode(pimygpio.PI_GPIO.L298N_IN_1, pigpio.OUTPUT)
    myPi.set_mode(pimygpio.PI_GPIO.L298N_IN_2, pigpio.OUTPUT)
    myPi.set_mode(pimygpio.PI_GPIO.L298N_IN_3, pigpio.OUTPUT)
    myPi.set_mode(pimygpio.PI_GPIO.L298N_IN_4, pigpio.OUTPUT)

class Motor:
    def __init__(self):
        self.myPi = pigpio.pi()
        setupL298N(self.myPi)
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4
    STOP = 5

    def move(self, direction, speed):
        cnv_dutycycle = int((speed * 1000000 / 100))
        match direction:
            case Motor.FORWARD:
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_1, 0)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_2, 1)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_3, 0)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_4, 1)
                self.myPi.hardware_PWM(pimygpio.PI_GPIO.PWM_PIN_1, 100, cnv_dutycycle)
                self.myPi.hardware_PWM(pimygpio.PI_GPIO.PWM_PIN_2, 100, cnv_dutycycle)
            case Motor.BACKWARD:
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_1, 1)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_2, 0)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_3, 1)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_4, 0)
                self.myPi.hardware_PWM(pimygpio.PI_GPIO.PWM_PIN_1, 100, cnv_dutycycle)
                self.myPi.hardware_PWM(pimygpio.PI_GPIO.PWM_PIN_2, 100, cnv_dutycycle)
            case Motor.LEFT:
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_1, 1)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_2, 0)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_3, 0)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_4, 1)
                self.myPi.hardware_PWM(pimygpio.PI_GPIO.PWM_PIN_1, 100, cnv_dutycycle)
                self.myPi.hardware_PWM(pimygpio.PI_GPIO.PWM_PIN_2, 100, cnv_dutycycle)
            case Motor.RIGHT:
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_1, 0)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_2, 1)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_3, 1)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_4, 0)
                self.myPi.hardware_PWM(pimygpio.PI_GPIO.PWM_PIN_1, 100, cnv_dutycycle)
                self.myPi.hardware_PWM(pimygpio.PI_GPIO.PWM_PIN_2, 100, cnv_dutycycle)
            case Motor.STOP:
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_1, 0)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_2, 1)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_3, 0)
                self.myPi.write(pimygpio.PI_GPIO.L298N_IN_4, 1)
                self.myPi.hardware_PWM(pimygpio.PI_GPIO.PWM_PIN_1, 100, 0)
                self.myPi.hardware_PWM(pimygpio.PI_GPIO.PWM_PIN_2, 100, 0)