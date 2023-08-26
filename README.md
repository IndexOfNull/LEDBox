# LED Box

![The box working!](https://i.imgur.com/AKVpUSN.jpg)
*Can you guess the album?*

This is the software for my LED picture frame. It's written in Python and uses the awesome [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) library. The main goal of this software is to provide a extensible system that can display a variety of images or data.

To drive my LED panels, I use a Raspberry Pi 2B and an Adafruit RGB LED matrix HAT.

# Installation and Configuration

This runs as a simple python script. You'll need to install the [rpi-rgb-led-matrix](https://github.com/hzeller/rpi-rgb-led-matrix) to your system. Also, you'll need to install the Python packages in the `requirements.txt` file. If you want it to run on boot, I've included a simple systemd unit file you can modify and install.

As for configuring the LED library, you can set options in the `run.py` file. You should refer to the rpi-rgb-led-matrix repository for specific information about each configuration options.

# Architecture

First, I must (again) address that this software is written in Python. If you're familiar with Python, you know it's terrible for concurrency (dang GIL). To help work around this, I use `asyncio` to make efficient use of free CPU time. One side-effect of this is that frames are rendered on demand rather than at a fixed rate. If you're only displaying a clock with a blinking colon symbol, you'll be running at about 1fps and have plenty of time for I/O. If you're displaying an animated gif, the framerate will be higher, but time-consuming I/O calls may get in the way, causing stutter. What this all means is that this software works great when you have relatively infrequent updates occuring (e.g. clock, weather, calendar, etc), but performance breaks down when refresh rate increases.

With that out of the way, I'll explain the three main parts of this software: the DisplayManager, Layouts, and Plugins.

### DisplayManager

The display manager is a class that contains multiple layouts. You can essentially treat it like a top-level singleton. Primarily, its job is to switch between layouts and handle executing callbacks when that happens. It is also what plugins and layouts call upon to request a frame be drawn.

### Layouts

A layout primarily contains plugins and how those plugins' should be drawn on screen. In the base layout implementation, it locates plugins using a bounding box. In the current implementation, only one layout is visible at a time, so you can treat them similar to slides on a slideshow.

### Plugins

Plugins are what draw interesting things on the screen. They are given a high degree of autonomy; their main responsibility is to supply a frame when asked by the parent layout (note: the parent layout may have been asked by the display manager). However, a plugin must also take care to supply an image of the right size. Generally, unless you modify the `resize_requested` function, the plugin should always have real time information about the dimensions of the frames it should draw.

An important note is that the relationship from plugins to layouts is one-to-many. That is, the same instance of a plugin can appear in more than one layout. For that reason, plugins purposefully do not have direct access to the current layout. However, this and carefully remembering image size allows for an important feature; plugins have no need to copy their state when the current displayed layout switches. That is, if you have a plugin instance counting down from 60 and a layout change occurs, the plugin need not make any effort to ensure its state is transferred to another instance of the same plugin.

Plugins can also do background work by registering tasks with asyncio. The only stipulation with this is that plugins should take care to pause or tear down their background tasks when `deactivated()` callback is called.

# CAD Files

![View of the box](https://i.imgur.com/BRWBvdj.png)

The Fusion 360 project needed to build this project is in the root of this repository. If you wish to make one yourself, you'll need access to a 3D printer and a laser cutter. The side panels (the parts with the tabs) are 3D printed, and the rest is laser cut. The front panel is a piece of frosted acryllic mounted with the frosted side facing the LED panels. The LED panels I used can be purchased on AliExpress [here](https://www.aliexpress.us/item/2251832646266595.html).

The panels and Raspberry Pi all mount with M2.5 screws. For securing the top and side panels together, I used some random screws I found that happened to fit. The acryllic panel should be hot glued to the front bezel (do not use superglue, it will fog the acryllic and LEDs).