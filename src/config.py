import configparser

#### config VARIABLES ####
configini = configparser.ConfigParser()

config_def = {
    "monitor": 1,
    "refresh_rate" : 15,
    "mode" : 'interpolation',
    "global_brightness" : 1.0,
    "red_brightness": 1.0,
    "green_brightness": 1.0,
    "blue_brightness": 1.0,
    "downscale_factor" : 60,
    "weight_borders" : 1,
    "border_size": 30,
    "logarithmic" : False,
    "coef" : 0.03,
    "prefix" : 'a',
    "COM_port" : 'COM6',
    "baudrate" : 9600,
    "debug": False
}

config_descriptions = {
    "monitor": "monitor to use (primary is 1)",
    "downscale_factor" : "screenshot downscale factor, a higher value is faster but less accurate",
    "global_brightness" : "from 0 to 1",
    "red_brightness" : "from 0 to 1",
    "green_brightness" : "from 0 to 1",
    "blue_brightness" : "from 0 to 1",
    "border_size": "percentage of screen that is a border from 0 to 100 (requires a restart)",
    "mode" : "'interpolation' (recommended) or 'average' of rgb values",
    # "median_ignore_center" : "ignore the center in median mode (1 is true, 0 is false)",
    "weight_borders" : "in average mode, select a value higher than 1 to give more weight to the borders (requires a restart)",
    "logarithmic" : "values are sent with a logarithmic curve, so that lower values are brighter (1 is true, 0 is false)",
    "coef" : "coefficient for logarithmic output, higher means steeper logarithmic curve",
    "prefix" : "prefix for communication syncing (requires a restart)",
    "COM_port" : "COM port of your microcontroller (requires a restart)",
    "baudrate" : "baudrate of serial communication (requires a restart)",
    "refresh_rate" : "Refresh rate (Hz)",
    "debug": "if True, prints rgb values"
}

configini.read('config.ini')
config = config_def
try:
    # pippo = configini["DEFAULT"]["downscale_factor"]
    config_temp = configini["DEFAULT"]
    for name,value in config_def.items():
        if isinstance(config_def[name], float):
            config[name] = float(config_temp[name])
        elif isinstance(config_def[name], bool):
            config[name] = True if config_temp[name] == 'True' or config_temp[name] == '1' else False
        elif isinstance(config_def[name], int):
            config[name] = int(config_temp[name])
        elif isinstance(config_def[name], str):
            config[name] = str(config_temp[name])
except Exception as e:
    print(e)
    print("No config file found")
    configini['DEFAULT'] = config_def
    with open('config.ini', 'w') as configfile:
        configini.write(configfile)
    config = config_def
