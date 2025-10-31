from machine import Pin
import time

# 初始化GPIO25为输出（RP2040板载LED）
led = Pin(25, Pin.OUT)

while True:
    led.value(1)    # 输出高电平
    print("LED亮")
    time.sleep(1)
    
    led.value(0)    # 输出低电平
    print("LED灭")
    time.sleep(1)