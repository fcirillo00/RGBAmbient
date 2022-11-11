# RGBAmbient
PC Ambient lights for unaddressable RGB LED strips.

## How it works
On your PC, at a frequency set by the user, a screenshot is taken and a RGB value is derived from it and sent to a serial port. Here, an external device like an ESP8266 or an Arduino listens for the value and sets the LED strip color accordingly.

Here's an example circuit:

<img width=60% src="https://user-images.githubusercontent.com/93737876/201392261-178b7c83-0259-4180-a16d-4c78c44b6896.png">

In the ```example``` directory there's also an Arduino sketch you can use.

RGB values are sent as 4 bytes, where the first one is a prefix ('a' in this case) to synchronize the communication and the other 3 are integers.
At the first value received, the microcontroller does a little fade animation to turn on the LEDs. If the communication stops and values are not received for a certain time, a fade animation turns off the LEDs.

## How to use
Connect your microcontroller to USB and run RGBAmbient.py on your PC. A tray icon should appear, right-click on it and write your COM port in the settings.

## Features
- Basic graphic interface for configuration
- Adjustable LED brightness
- Two modes of operation:
  - ```interpolation``` (interpolate the image to a single pixel to get the RGB value)
  - ```average``` (do an average of all pixels)
- Logarithmic mode to brigthen the lower values
- In ```average``` mode, give more weight to the borders of the screen
- Turn on and off the lights from the tray icon

![image](https://user-images.githubusercontent.com/93737876/201398738-d9f35ba3-21ce-4bc7-92b2-3486c6a2050c.png)

