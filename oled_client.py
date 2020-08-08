import machine
import ssd1306
import network
import Terminal


i2c = machine.I2C(-1, machine.Pin(4), machine.Pin(5))
oled = ssd1306.SSD1306_I2C(128,64, i2c)
term = terminal.Terminal(oled)



def intro():
    term.println("ISAblyng V0.1")
    term.println("pow. by Blynk")
    term.println("")
    term.println("IP:" + network.WLAN().ifconfig()[0])

intro()
