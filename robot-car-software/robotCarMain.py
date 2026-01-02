from pimygpio import PI_GPIO
from dcMortorL298N import Motor

def main():
    dcMotor = Motor()
    # キーボードの入力を取得してモーターを制御する
    while True:
        key = input("Enter command (w: forward, s: backward, a: left, d: right, q: quit): ")
        if key == 'w':
            dcMotor.forward()
        elif key == 's':
            dcMotor.backward()
        elif key == 'a':
            dcMotor.left()
        elif key == 'd':
            dcMotor.right()
        elif key == 'q':
            break
        else:
            print("Invalid command")

if __name__ == "__main__":
    main()