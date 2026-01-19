# Ultimate Companion Cube
# Built for Myrtarous by Mutual_Inductance

# libraries and modules
import board
import digitalio
import time
import touchio  # for capacitive touch sensor
from adafruit_debouncer import Debouncer  # for capacitive touch sensor
from rainbowio import colorwheel  # for neopixel output
import neopixel  # for neopixel output
from os import getenv  # for wifi
import ipaddress  # for wifi
import wifi  # for wifi
import socketpool  # for wifi
import adafruit_connection_manager
import adafruit_requests
import microcontroller
from adafruit_io.adafruit_io import IO_HTTP, AdafruitIO_RequestError

# WIFI
#  Get WiFi details, ensure these are setup in settings.toml
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")
aio_username = getenv("ADAFRUIT_AIO_USERNAME")
aio_key = getenv("ADAFRUIT_AIO_KEY")

if None in [ssid, password]:
    raise RuntimeError(
        "WiFi settings are kept in settings.toml, "
        "please add them there. The settings file must contain "
        "'CIRCUITPY_WIFI_SSID', 'CIRCUITPY_WIFI_PASSWORD', "
        "at a minimum."
    )
print()
print("Connecting to WiFi")

#  connect to your SSID
try:
    wifi.radio.connect(ssid, password)
except TypeError:
    print("Could not find WiFi info. Check your settings.toml file!")
    raise
print("Connected to WiFi")

pool = socketpool.SocketPool(wifi.radio)

#  prints MAC address to REPL
print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

#  prints IP address to REPL
print(f"My IP address is {wifi.radio.ipv4_address}")

#  pings Google
ipv4 = ipaddress.ip_address("8.8.4.4")
print("Ping google.com: %f ms" % (wifi.radio.ping(ipv4) * 1000))

# ADAFRUIT IO
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)

# Initialize an Adafruit IO HTTP API object
io = IO_HTTP(aio_username, aio_key, requests)

light_on = 1
light_off = 0
try:
    # Get the 'light' feed from Adafruit IO
    light_feed = io.get_feed("light")
except AdafruitIO_RequestError:
    # If no 'light' feed exists, create one
    light_feed = io.create_new_feed("light")


# LIGHTS
pixel_pin = board.GP6
num_pixels = 8
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.3, auto_write=False, pixel_order=(1, 0, 2, 3)
)


def colorwheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3, 0)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3, 0)


def color_chase(color, wait):
    for i in range(num_pixels):
        pixels[i] = color
        time.sleep(wait)
        pixels.show()
        print(color)
    time.sleep(0.5)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(num_pixels):
            rc_index = (i * 256 // num_pixels) + j
            pixels[i] = colorwheel(rc_index & 255)
        pixels.show()
        time.sleep(wait)


WHITE = (255, 255, 255, 255)
RED = (255, 0, 0, 0)
YELLOW = (255, 150, 0, 0)
GREEN = (0, 255, 0, 0)
CYAN = (0, 255, 255, 0)
BLUE = (0, 0, 255, 0)
PURPLE = (180, 0, 255, 0)
IRIS = (102, 0, 255, 0)
MAGENTA = (153, 0, 255, 0)
PINK = (204, 0, 255, 0)
FUSCHIA = (255, 0, 204, 0)
CORAL = (255, 0, 153, 0)
ROSE = (255, 0, 102, 0)
LIGHTRED = (255, 0, 53, 0)


# TOUCHPAD
touch_pad = touchio.TouchIn(board.GP19, digitalio.Pull.UP)
touch_deb = Debouncer(touch_pad)

# main loop
while True:
    # Get data from 'digital' feed
    print("getting data from IO...")
    feed_data = io.receive_data(light_feed["key"]) 
    
    # Check if data is ON or OFF
    if int(feed_data["value"]) == 1:
        print("received <- ON\n")
        pixels.fill(ROSE)
        pixels.show()
        time.sleep(5)  # will this work if I need it to be listening for a touch on the light_feed? 
    elif int(feed_data["value"]) == 0:
        print("received <= OFF\n")

    # check for touch
    touch_deb.update()
    
    if touch_deb.rose:  # using rose to sense only when someone touches the lamp.
        pixels.fill(ROSE)
        pixels.show()
        print("sending to adafruitIO")
        io.send_data(light_feed["key"], light_on)
        time.sleep(5)
        io.send_data(light_feed["key"], light_off)
    # Increase or decrease to change the speed of the solid color change.
    #    time.sleep(5)
    #    pixels.fill(MAGENTA)
    #    pixels.show()
    #    time.sleep(5)
    else:
        pixels.fill(WHITE)
        pixels.show()
        time.sleep(.2)
#    color_chase(PURPLE, .08)
#    color_chase(MAGENTA, .08)
#    color_chase(IRIS, .08)
#    color_chase(FUSCHIA, .08)
#    color_chase(CORAL, .08)
#    color_chase(ROSE, .08)
#    color_chase(LIGHTRED, .08)
#    color_chase(RED, .08)
#    color_chase(LIGHTRED, .08)
#    color_chase(ROSE, .08)
#    color_chase(CORAL, .08)
#    color_chase(FUSCHIA, .08)
#    color_chase(IRIS, .08)
#    color_chase(MAGENTA, .08)
# Increase the number to slow down the color chase
#    color_chase(YELLOW, .08)
#    color_chase(GREEN, .08)
#    color_chase(CYAN, .08)
#    color_chase(BLUE, .08)

#    rainbow_cycle(0)  # Increase the number to slow down the rainbow
