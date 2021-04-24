from machine import Pin, PWM

def digital_write(__pin=5, value=1):
    p = Pin(__pin, Pin.OUT)

    value = int(value)
    
    if value: p.on()
    else: p.off()
    

def analog_write(__pin=2, value=300):
    pwm = PWM(Pin(__pin), freq=20000)
    pwm.duty(int(value))
    
    
