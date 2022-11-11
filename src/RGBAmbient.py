from mss import mss, windows
import numpy as np
import time
from serial import Serial
from serial import SerialException
from threading import Thread
import PySimpleGUI as sg
from psgtray import SystemTray
import sys
import cv2
from config import config, config_descriptions, configini

# prevent flickering
windows.CAPTUREBLT = 0

SCT = mss()
MONITOR = SCT.monitors[config["monitor"]]

def bgra2rgb(im):
    """ Convert frame from BGRA to RGB """
    frame = np.array(im, dtype=np.uint8)
    return np.flip(frame[:, :, :3], 2)

###########################
# Constants initialization
test = np.array(SCT.grab(MONITOR))
WIDTH = int(test.shape[1]/config["downscale_factor"])
HEIGHT = int(test.shape[0]/config["downscale_factor"])
RGB_COEF = 255/np.log1p(config["coef"]*255)
PREFIX_BYTES = config["prefix"].encode()
HEIGHT_CENTER_LEFT = int( (HEIGHT-HEIGHT*config["center_size"] ) / 2 )
HEIGHT_CENTER_RIGHT = int( (HEIGHT+HEIGHT*config["center_size"]) /2 )
WIDTH_CENTER_LEFT = int( (WIDTH-WIDTH*config["center_size"] ) / 2 )
WIDTH_CENTER_RIGHT = int( (WIDTH+WIDTH*config["center_size"] ) / 2 )

test = cv2.resize(bgra2rgb(SCT.grab(MONITOR)), (WIDTH,HEIGHT))
CENTER_MASK = np.full_like(test, fill_value=config["weight_borders"], dtype=np.uint8)
for i in range(HEIGHT):
    for j in range(WIDTH):
        if i in range(HEIGHT_CENTER_LEFT, HEIGHT_CENTER_RIGHT) and j in range (WIDTH_CENTER_LEFT, WIDTH_CENTER_RIGHT):
            CENTER_MASK[i][j] = 1
##########################

def get_average_rgb ():
    screen = SCT.grab(MONITOR)
    screen = cv2.resize(bgra2rgb(screen), (WIDTH,HEIGHT))
    weight = np.where(screen > 100, 5, 1) # give more weight to bright pixels
    weight *= CENTER_MASK
    return np.average(screen, axis=(0,1), weights=CENTER_MASK)

def get_interpolation_rgb():
    screen = SCT.grab(MONITOR)
    screen = cv2.resize(bgra2rgb(screen), (1,1), interpolation=cv2.INTER_AREA)[0][0]
    return screen

def get_rgb ():
    if config["mode"]=='interpolation':
        r,g,b = get_interpolation_rgb() 
    elif config["mode"] == 'average':
        r,g,b = get_average_rgb()
    if (config["logarithmic"]):
        r = int(np.log1p(config["coef"] * r) * RGB_COEF * config["global_brightness"] * config["red_brightness"]) 
        g = int(np.log1p(config["coef"] * g) * RGB_COEF * config["global_brightness"] * config["green_brightness"])
        b = int(np.log1p(config["coef"] * b) * RGB_COEF * config["global_brightness"] * config["blue_brightness"])
    else:
        r = int(r * config["global_brightness"] * config["red_brightness"])
        g = int(g * config["global_brightness"] * config["green_brightness"])
        b = int(b * config["global_brightness"] * config["blue_brightness"])
    return r,g,b

class RGB_Serial():
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.s = Serial()
        self.stop_var = False
        self.t1 = Thread()
    
    def send_rgb (self,r,g,b):
        self.s.write(PREFIX_BYTES)
        self.s.write(r.to_bytes(length=1, signed=False, byteorder='little'))
        self.s.write(g.to_bytes(length=1, signed=False, byteorder='little'))
        self.s.write(b.to_bytes(length=1, signed=False, byteorder='little'))

    def try_connection (self):
        while (True):
            if self.stop_var:
                break
            try:
                self.s = Serial(port = self.port, baudrate = self.baudrate)
                break
            except SerialException:
                if config["debug"]:
                    print("Port not found, waiting 10 seconds...")
                time.sleep(10)

    def stop(self):
        self.stop_var = True
        if self.t1.is_alive():
            self.t1.join()
        self.s.close()

    def main (self):
        self.try_connection()
        while (not self.stop_var):
            try: 
                start = time.time()
                r,g,b = get_rgb()
                self.send_rgb(r,g,b)
                if config["debug"]:
                    print([r,g,b]) 
                sleep_time = 1/config["refresh_rate"] - (time.time() - start)
                time.sleep(sleep_time if sleep_time > 0 else 0)
            except SerialException:
                print("Cant find serial port")
                self.s.close()
                self.try_connection()
            except OSError:
                time.sleep(5)

    def run (self):
        self.stop_var = False
        if not self.t1.is_alive():
            self.t1 = Thread(target = self.main)
            self.t1.start()


def main():
    menu = ['', ['Turn on', 'Turn off', '---', 'Settings', 'Exit']]
    tooltip = 'RGBAmbient'
    layout = [[sg.Text('Some settings may require a restart')]]
    
    for name, value in config.items():
        layout.append( [sg.T(name, tooltip=config_descriptions[name]), sg.Input(value, key=name+'-IN-', s=(10,1)), sg.B('Set', key=name)] )

    layout.append( [sg.Multiline(size=(60,10), reroute_stdout=True, reroute_cprint=False, write_only=True, key='-OUT-')] )
    layout.append([sg.B("Save", tooltip='Save config'), sg.B("Clear", tooltip='Clear output'), sg.B("Exit")])
    window = sg.Window(tooltip, layout, finalize=True, enable_close_attempted_event=True)
    window.hide()
    tray = SystemTray(menu, single_click_events=False, window=window, tooltip=tooltip, icon=sg.DEFAULT_BASE64_ICON)
    
    rgb = RGB_Serial(config["COM_port"], config["baudrate"])
    rgb.run()
    while (True):
        event, values = window.read()
        if event == tray.key:
            #sg.cprint(f'System Tray Event = ', values[event], c='white on red')
            event = values[event]       # use the System Tray's event as if was from the window
        if event in ('Settings', sg.EVENT_SYSTEM_TRAY_ICON_DOUBLE_CLICKED):
            window.un_hide()
            window.bring_to_front()
        elif event == sg.WIN_CLOSE_ATTEMPTED_EVENT:
            window.hide()
            tray.show_icon()
        elif event == 'Turn on':
            rgb.run()
        elif event == 'Turn off':
            rgb.stop()
        elif event in config.keys():
            if isinstance(config[event], float):
                config[event] = float(values[event+'-IN-'])
            elif isinstance(config[event], bool):
                config[event] = True if values[event+'-IN-'] == 'True' or values[event+'-IN-'] == '1' else False
            elif isinstance(config[event], int):
                config[event] = int(values[event+'-IN-'])
            else:
                config[event] = values[event+'-IN-']
        elif event == "Clear":
            window.find_element('-OUT-').Update('')
        elif event == "Save":
            configini['DEFAULT'] = config
            with open('config.ini', 'w') as configfile:
                configini.write(configfile)
        elif event == "Exit":
            try:
                rgb.stop()
                rgb.s.close()
            except:
                sys.exit(1)
            tray.close()
            window.close()
            break



if __name__ == "__main__":
    main()