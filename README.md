# RGBAmbient
PC Ambient lights for unaddressable RGB led strips.

## How it works
On your PC, at a frequency set by the user, a screenshot is taken and a RGB value is derived from it and sent to a serial port. Here, an external device like an ESP8266 or an Arduino listens for the value and sets the led strip color accordingly.

Here's an example circuit:

<img width=60% src="https://user-images.githubusercontent.com/93737876/201392261-178b7c83-0259-4180-a16d-4c78c44b6896.png">

In the ```example``` directory there's also an Arduino sketch to test the application.

## How to use
Connect your microcontroller to USB and run RGBAmbient on your PC. A tray icon should appear, right-click on it and in the settings write your COM port.

## Features
- Basic graphic interface for configuration
- Adjustable LED brightness
- Two modes of operation:
  - ```interpolation``` (interpolate the image to a single pixel to get the RGB value)
  - ```average``` (do an average of all pixels)
- Logarithmic mode to brigthen the lower values
- In ```average``` mode, give more weight to the borders of the screen
