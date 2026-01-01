from enum import Enum

class PI_GPIO(Enum):
    def __init__(self):
        pass
    # L298NのGPIO定義
    L298N_IN_1 = 22 # モーター1/2の回転方向を制御
    L298N_IN_2 = 23 # モーター1/2の回転方向を制御
    L298N_IN_3 = 20 # モーター3/4の回転方向を制御
    L298N_IN_4 = 26 # モーター3/4の回転方向を制御
    PWM_PIN_1 = 13 # モーター1/2の速度をPWMで制御するためのピン
    PWM_PIN_2 = 19 # モーター3/4の速度をPWMで制御するためのピン