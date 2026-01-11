"""モーター制御インフラ"""
from .dcMortorL298N import Motor
from .pimygpio import PI_GPIO

__all__ = ['Motor', 'PI_GPIO']
