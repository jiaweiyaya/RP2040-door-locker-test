import rp2
import utime
from machine import Pin

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW) 
def PWM1():
    pull(noblock) .side(0)      # 非阻塞读取，同时设置side为0
    mov(x, osr)                 # 将OSR数据存入X（占空比值）
    mov(y, isr)                 # 将ISR数据存入Y（PWM周期最大值）
    label("pwmloop")
    jmp(x_not_y, "skip")        # 如果X != Y，跳转到skip
    nop()         .side(1)      # 设置side为1（输出高电平）
    label("skip")
    jmp(y_dec, "pwmloop")       # Y减1，如果Y不为0则循环

#PIO控制需要的函数: 
def caculateFreq(pioFreq, PWMFreq):    #pioFreq是要计算的pio的pio频率; PWMFreq是需要输出的PWM的频率
    return int(pioFreq / PWMFreq / 2)

#舵机控制需要的函数: 
def caculateMem(duty, maxCnt):    #duty为0.0-1.0表示占空比0.0%-100.0%; maxCntMem为寄存器最大值
    return int(maxCnt * duty)

def caculatePWMHighDuty(highTime, dutyTime):    #highTime是一个周期内的高电平时长(ms); dutyTime是一个周期的时长(ms)
    return highTime / dutyTime

def caculateDegreeDutyTime(degree, highTime0, highTime180):    #degree是舵机的角度(0-180度); highTime0是舵机0度的高电平时长; highTime180是舵机180度的高电平时长
    return ((highTime180 - highTime0) * (degree / 180) + highTime0)

#PWM1参数: 
pio1Freq = 100000000
PWM1Freq = 50
PWM1Pin = 0

PWM1Ctrl = rp2.StateMachine(0, PWM1, freq=pio1Freq, sideset_base=Pin(PWM1Pin))
PWMCnt = caculateFreq(pio1Freq, PWM1Freq)
PWM1Ctrl.put(PWMCnt)             # 将max_count放入TX FIFO
PWM1Ctrl.exec("pull()")          # 将数据从TX FIFO拉到OSR
PWM1Ctrl.exec("mov(isr, osr)")   # 将OSR数据复制到ISR
PWM1Ctrl.active(1)               # PWM1状态机开启

while True:
    utime.sleep_ms(500)
    PWM1Ctrl.put(caculateMem(caculatePWMHighDuty(caculateDegreeDutyTime(0, 0.5, 2.5), 1000 / PWM1Freq), PWMCnt))
    utime.sleep_ms(500)
    PWM1Ctrl.put(caculateMem(caculatePWMHighDuty(caculateDegreeDutyTime(180, 0.5, 2.5), 1000 / PWM1Freq), PWMCnt))
    
    # for i in range(181):
    #     utime.sleep_ms(20)
    #     PWM1Ctrl.put(caculateMem(caculatePWMHighDuty(caculateDegreeDutyTime(i, 0.5, 2.5), 1000 / PWM1Freq), PWMCnt))
    #     print(i, '度')
    # for i in range(181, 0, -1):
    #     utime.sleep_ms(20)
    #     PWM1Ctrl.put(caculateMem(caculatePWMHighDuty(caculateDegreeDutyTime(i, 0.5, 2.5), 1000 / PWM1Freq), PWMCnt))
    #     print(i, '度')
    # break

#PWM1关闭
PWM1Ctrl.active(0)