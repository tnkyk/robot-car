from time import sleep
import pigpio
import time
import pimygpio
from pigpio import pi

#PWMパラメータ
duty = 0 #デューティー比を%で指定
freq = 100 #PWM周波数をHzで指定

def setupL298N(pi: pi):
    pi.set_mode(pimygpio.PI_GPIO.L298N_IN_1, pigpio.OUTPUT)
    pi.set_mode(pimygpio.PI_GPIO.L298N_IN_2, pigpio.OUTPUT)
    pi.set_mode(pimygpio.PI_GPIO.L298N_IN_3, pigpio.OUTPUT)
    pi.set_mode(pimygpio.PI_GPIO.L298N_IN_4, pigpio.OUTPUT)



#IN1、IN2の制御信号
pi.write(pimygpio.PI_GPIO.L298N_IN_1, 0)
pi.write(pimygpio.PI_GPIO.L298N_IN_2, 1)
pi.write(pimygpio.PI_GPIO.L298N_IN_3, 1)
pi.write(pimygpio.PI_GPIO.L298N_IN_4, 0)

#モーターを駆動
while True:
  
    #デューティサイクル計算
    cnv_dutycycle = int((duty * 1000000 / 100))
    #PWMを出力
    pi.hardware_PWM(pimygpio.PI_GPIO.PWM_PIN_1, freq, cnv_dutycycle)
    pi.hardware_PWM(pimygpio.PI_GPIO.PWM_PIN_2, freq, cnv_dutycycle)
    #dutyを変更
    if up_flag == True:
        if duty == 100:
            up_flag = False
        else:
            duty += 1
    else:
        if duty == 0:
            up_flag = True
        else:
            duty -=1
    
    time.sleep(0.05)