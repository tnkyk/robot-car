from infrastructure.motor import Motor
import sys
import termios
import tty

def getch():
    """1文字だけ即時取得する関数（Enter不要）"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)  # 端末をrawモードに（エコーもオフ）
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)  # 端末設定を復元
    return ch

def main():
    dcMotor = Motor()
    # キーボードの入力を取得してモーターを制御する
    while True:
        print("w:前進、s:後進、a:左、d:右、e:ストップ、'q' でプログラム終了。")
        key = getch()
        if key == 'w':
            print("click FORWARD")
            dcMotor.move(Motor.FORWARD,20)
        elif key == 's':
            dcMotor.move(Motor.BACKWARD,20)
        elif key == 'a':
            dcMotor.move(Motor.LEFT,70)
        elif key == 'd':
            dcMotor.move(Motor.RIGHT,70)
        elif key == 'e':
            dcMotor.move(Motor.STOP,0)
        elif key == 'q':
            dcMotor.move(Motor.STOP,0)
            break
        else:
            print("Invalid command")

if __name__ == "__main__":
    main()