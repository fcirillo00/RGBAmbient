import configparser

#### config VARIABLES ####
configini = configparser.ConfigParser()

config_def = {
"monitor": 1,                      # monitor to use (primary is 1)
"downscale_factor" : 60,           # downscale of screenshot
"global_brightness" : 1.0,         # from 0 to 1
"red_brightness": 1.0,             # from 0 to 1
"green_brightness": 1.0,           # from 0 to 1
"blue_brightness": 1.0,            # from 0 to 1
"center_size": 0.7,                # size of center for median_ignore_center and weight_borders
"mode" : 'median',                 # 'median' or 'average' of rgb values
"median_ignore_center" : True,     # ignore the center in median mode
"weight_borders" : 10,             # in average mode, how much the borders of the screen are weighted (normal is 1)
"logarithmic" : True,              # values are sent with a logarithmic curve, so that lower values are brighter
"coef" : 0.03,                     # coefficient for logarithmic output, higher means steeper logarithmic curve
"prefix" : 'a',                    # prefix for communication syncing
"COM_port" : 'COM6',               # rgb values are passed as three uint8 bytes to the serial port, starting with prefix bytes for syncing (example: ['a',100,100,100] )
"baudrate" : 9600, 
"refresh_rate" : 15,               # Refresh rate (Hz)
"debug": False                     # if True, prints rgb values
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
except Exception as e:
    print(e)
    print("No config file found")
    configini['DEFAULT'] = config_def
    with open('config.ini', 'w') as configfile:
        configini.write(configfile)
    config = config_def

config_descriptions = {
    "monitor": "monitor to use (primary is 1)",
    "downscale_factor" : "downscale of screenshot",
    "global_brightness" : "from 0 to 1",
    "red_brightness" : "from 0 to 1",
    "green_brightness" : "from 0 to 1",
    "blue_brightness" : "from 0 to 1",
    "center_size": "size of center for median_ignore_center and weight_borders",
    "mode" : "'median' or 'average' of rgb values",
    "median_ignore_center" : "ignore the center in median mode (1 is true, 0 is false)",
    "weight_borders" : "in average mode, how much the borders of the screen are weighted (select 1 if you want to disable it)",
    "logarithmic" : "values are sent with a logarithmic curve, so that lower values are brighter (1 is true, 0 is false)",
    "coef" : "coefficient for logarithmic output, higher means steeper logarithmic curve",
    "prefix" : "prefix for communication syncing",
    "COM_port" : "rgb values are passed as three uint8 bytes to the serial port, starting with prefix bytes for syncing (example: ['a',100,100,100] )",
    "baudrate" : "",
    "refresh_rate" : "Refresh rate (Hz)",
    "debug": "if True, prints rgb values"
}
#################################