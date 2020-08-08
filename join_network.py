import time
import network



def join(SSID,PASS):
    wlan=network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID,PASS)

    #wait till connected
    while not wlan.isconnected():
        time.sleep(1)
        print("Waiting for Wifi connection...")

    print("Successfully connected to ->", SSID)
