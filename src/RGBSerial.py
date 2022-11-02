from mss import mss
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

SCT = mss()
MONITOR = SCT.monitors[config["monitor"]]

def np_flip(im):
    """ Most efficient np version as of now. """
    frame = np.array(im, dtype=np.uint8)
    return np.flip(frame[:, :, :3], 2)

# get resolution data
test = np.array(SCT.grab(MONITOR))

resolution_y = test.shape[0]
resolution_x = test.shape[1]
width = int(resolution_x/config["downscale_factor"])
height = int(resolution_y/config["downscale_factor"])
rgb_coef = 255/np.log1p(config["coef"]*255)
prefix_bytes = config["prefix"].encode()
height_center_left = int( (height-height*config["center_size"] ) / 2 )
height_center_right = int( (height+height*config["center_size"]) /2 )
width_center_left = int( (width-width*config["center_size"] ) / 2 )
width_center_right = int( (width+width*config["center_size"] ) / 2 )

##########################
# create numpy masks for weight_borders and ignore_center
test = cv2.resize(np_flip(SCT.grab(MONITOR)), (width,height))

ignore_center = np.full_like(test, fill_value=config["weight_borders"], dtype=np.uint8)
for i in range(height):
    for j in range(width):
        if i in range(height_center_left, height_center_right) and j in range (width_center_left, width_center_right):
            ignore_center[i][j] = 1

median_nocenter = np.full_like(test, fill_value=0, dtype=np.uint8)
for i in range(height):
    for j in range(width):
        if i in range(height_center_left, height_center_right) and j in range (width_center_left, width_center_right):
            median_nocenter[i][j] = 1 if config["median_ignore_center"] else 0
##########################

def get_average_rgb ():
    screen = SCT.grab(MONITOR)
    screen = cv2.resize(np_flip(screen), (width,height))
    weight = np.where(screen > 100, 5, 1)
    weight *= ignore_center
    return np.average(screen, axis=(0,1), weights=ignore_center)

def get_median_rgb ():
    screen = SCT.grab(MONITOR)
    screen = cv2.resize(np_flip(screen), (width,height))
    screen = np.ma.array(screen, mask=median_nocenter)
    return np.ma.median(screen, axis=(0,1))

def get_rgb ():
    if config["mode"]=='median':
        r,g,b = get_median_rgb() 
    elif config["mode"] == 'average':
        r,g,b = get_average_rgb()
    if (config["logarithmic"]):
        r = int(np.log1p(config["coef"] * r) * rgb_coef * config["global_brightness"] * config["red_brightness"]) 
        g = int(np.log1p(config["coef"] * g) * rgb_coef * config["global_brightness"] * config["green_brightness"])
        b = int(np.log1p(config["coef"] * b) * rgb_coef * config["global_brightness"] * config["blue_brightness"])
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
        self.old_rgb = [0,0,0]
        self.stop_var = False
        self.t1 = Thread()
    
    def send_rgb (self,r,g,b):
        self.s.write(prefix_bytes)
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
                r,g,b = get_rgb()
                self.send_rgb(r,g,b)
                if config["debug"]:
                    print([r,g,b]) 
                time.sleep(1/config["refresh_rate"])
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
    tooltip = 'RGBSerial'
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
                config[name] = True if values[event+'-IN-'] == 'True' or values[event+'-IN-'] == '1' else False
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