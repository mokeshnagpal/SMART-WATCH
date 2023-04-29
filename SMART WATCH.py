from machine import SoftI2C,Pin,ADC
import ssd1306
from bmp180 import BMP180
from time import time,localtime
import BlynkLib
import network
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

bus = SoftI2C(scl=Pin(22), sda=Pin(21), freq=100000)
bmp180 = BMP180(bus)
bmp180.oversample_sett=2
bmp180.baseline = 101325

SSID = 'MAJESTIC MOKSH'
PASS = 'Mokesh12345' 
BLYNK_AUTH = "8sFjFSiNs0AVvf4juMRc2Y63NLQLuAdq"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
try:
    wifi.connect(SSID, PASS)

    while not wifi.isconnected():
        pass
    blynk.virtual_write(0,'Connected to WiFi')
    sleep(1)
    blynk.virtual_write(0,('IP address: '+str(wifi.ifconfig()[0])))
    sleep(1)
except Exception as e:
    pass


RL_VALUE = 10000
VREF = 3.3
PREHEAT_TIME = 600
R0_VALUE = 10000
TEMP_OFFSET = 0
PPM_PER_VOLT = 1000 / VREF
PPM_CURVE = [2.3, 0.53, -0.44]


display=t=hr=mi=sec=k=b=x=y=time_hr=time_last=tlm=tmq=0
temp=p=altitude=temperature=voltage=lm_35=ppm=0

blynk = BlynkLib.Blynk(BLYNK_AUTH)
@blynk.on("V0")
def v0_write_handler(value):
    global hr
    hr=value[0]
@blynk.on("V1")
def v1_write_handler(value):
    global hr
    mi=value[0]
@blynk.on("V2")
def v2_write_handler(value):
    global sec
    sec=value[0]
    
    
blynk.virtual_write(1,0)
touch=Pin(18,Pin.IN)
button=Pin(4,Pin.IN,pull=Pin.PULL_DOWN)
buzz=Pin(14,Pin.OUT)
#analog_pin = ADC(Pin(13))
lm35_pin = ADC(Pin(34))
class MQ135:
    def __init__(self, analog_pin, RL_VALUE, VREF, R0_VALUE, PPM_CURVE, PPM_PER_VOLT):
        self.analog_pin = analog_pin
        self.RL_VALUE = RL_VALUE
        self.VREF = VREF
        self.R0_VALUE = R0_VALUE
        self.PPM_CURVE = PPM_CURVE
        self.PPM_PER_VOLT = PPM_PER_VOLT

    def get_correction_factor(self, humidity, temperature):
        return 1.0 / ((1.0 / self.PPM_CURVE[0]) * (humidity / 33.0) * self.PPM_CURVE[1] * (temperature / 33.0) * self.PPM_CURVE[2])

    def get_resistance(self):
        adc_value = self.analog_pin.read()
        voltage = adc_value * self.VREF / 4096.0
        resistance = self.RL_VALUE * (self.VREF - voltage) / voltage
        return resistance

    def get_corrected_resistance(self, humidity, temperature):
        return self.get_resistance() / self.get_correction_factor(humidity, temperature)

    def get_ppm(self, humidity, temperature):
        resistance = self.get_corrected_resistance(humidity, temperature)
        ppm = self.PPM_PER_VOLT * (resistance / self.R0_VALUE) ** -1.16
        return ppm
#mq135 = MQ135(analog_pin, RL_VALUE, VREF, R0_VALUE, PPM_CURVE, PPM_PER_VOLT)

def alarm():
    for i in range(10):
        buzz.value(1)
        sleep(2)
        buzz.value(0)
        sleep(1)
while True:
    if (touch.value()==1):
        display=display+1
        while(touch.value()==1):
            pass
    if(display==4):
        display=0
    if display==0:
        oled.fill(0)
        oled.text("Local Time:", 0, 0)
        oled.text(str(localtime()[3]) + ":" + str(localtime()[4]) + ":" + str(localtime()[5]), 0, 20)
        oled.text("or", 0, 30)
        if(localtime()[3]>12):
            time_last="PM"
            time_hr=localtime()[3]-12
        else:
            time_last="AM"
        oled.text(str(time_hr) + ":" + str(localtime()[4]) + ":" + str(localtime()[5])+" "+str(time_last), 0, 40)
        oled.show()
    elif display==1:
        if(button.value()==1):
            k=k+1;
            b=1
            while(button.value()==1):
                pass
        if(k%2==1 and b==1):
            t=time()+x
            b=0
        oled.fill(0)
        x=time()-t
        if(k%2==0 and b==1):
            y=x
            b=0
        if(k%2==0):
            oled.text("Last data :", 0, 30)
            oled.text(str(y), 0, 45)
            x=0
        
        
        oled.text("Stop watch:", 0, 0)
        if(t!=0):
            oled.text(str(x),0,15)
        else:
            oled.text(str(0),0,15)
        oled.show()
    elif display==2:
        temp = bmp180. temperature
        p = bmp180.pressure/101325
        altitude = bmp180.altitude
        oled.fill(0)
        oled.text("Temp Reading:", 0, 0)
        oled.text(str(round(temp, 1)) + " C", 0, 10)
        oled.text("Pres Reading:", 0, 20)
        oled.text(str(round(p, 2)) + " Pa", 0, 30)
        oled.text("Alt Reading:", 0, 40)
        oled.text(str(round(altitude, 1)) + " m", 0, 50)
        oled.show()
    elif display==3:
        if(time()-tlm>5):
            lm35_value = lm35_pin.read()
            tlm=time()  
            voltage = (lm35_value / 4095.0) * VREF
            temperature = (voltage - TEMP_OFFSET) * 100.0
            oled.fill(0)
            oled.text("Temperature:", 0, 10)
            oled.text(str(temperature),0,20)
            oled.show()
    '''elif display==4:
        oled.fill(0)
        if(time()-tmq>60):
            ppm = mq135.get_ppm(60, temp)
            oled.text("PPM:", 0, 10)
            oled.text(str(ppm),0,20)
        else:
            oled.text("Calibrating", 0, 10)
        oled.show()'''
    if(localtime()[3]==hr and localtime()[4]==mi and localtime()[5]==sec):
        alarm()