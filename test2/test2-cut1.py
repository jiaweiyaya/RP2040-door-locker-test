import rp2
import utime
from machine import Pin

@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW) 
def pwm_10():
    set(pins, 1) [9]
    set(pins, 0) [19]
    nop() [19]
    nop() [19]
    nop() [19]
    nop() [9]

while True:
    sm = rp2.StateMachine(0, pwm_10, freq=20000, set_base=Pin(25))
    sm.active(1)
    utime.sleep(1)
    sm.active(0)