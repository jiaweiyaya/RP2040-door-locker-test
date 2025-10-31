import rp2
import utime
from machine import Pin

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW) 
def pwm_prog():
    pull(noblock) .side(0)      # 非阻塞读取，同时设置side为0
    mov(x, osr)                 # 将OSR数据存入X（占空比值）
    mov(y, isr)                 # 将ISR数据存入Y（PWM周期最大值）
    label("pwmloop")
    jmp(x_not_y, "skip")        # 如果X != Y，跳转到skip
    nop()         .side(1)      # 设置side为1（输出高电平）
    label("skip")
    jmp(y_dec, "pwmloop")       # Y减1，如果Y不为0则循环

def caculateFreq(pioFreq, PWMFreq):    #pioFreq是要计算的pio的pio频率; PWMFreq是需要输出的PWM的频率
    return int(pioFreq / PWMFreq / 2)

def caculateMem(duty, maxCnt):    #duty为0.0-1.0表示占空比0.0%-100.0%; maxCntMem为寄存器最大值
    return int(maxCnt * duty)

def caculatePWMHighDuty(highTime, dutyTime):    #highTime是一个周期内的高电平时长(ms); dutyTime是一个周期的时长(ms)
    return highTime / dutyTime

pio1Freq = 100000000
PWM1Freq = 50

pwm_sm = rp2.StateMachine(0, pwm_prog, freq=pio1Freq, sideset_base=Pin(25))
PWMCnt = caculateFreq(pio1Freq, PWM1Freq)
pwm_sm.put(PWMCnt)             # 将max_count放入TX FIFO
pwm_sm.exec("pull()")          # 将数据从TX FIFO拉到OSR
pwm_sm.exec("mov(isr, osr)")   # 将OSR数据复制到ISR
pwm_sm.active(1)               # 启动状态机

while True:
    pwm_sm.put(caculateMem(caculatePWMHighDuty(0.5, 1000 / PWM1Freq), PWMCnt))