from pimygpio import PI_GPIO
from dcMortorL298N import setupL298N

def setupHardWare(pi):
    setupL298N(pi)

def main():
    pi = PI_GPIO().pi
    setupHardWare(pi)

if __name__ == "__main__":
    main()