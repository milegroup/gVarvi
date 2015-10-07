# gVarvi
 Graphical tool for heart rate Variability Analysis in Response to audioVisual stImuli. gVarvi supports all heart 
 rate monitors that use [ANT+] (http://www.thisisant.com/) protocol and
 [Polar Wearlink®+](http://www.polar.com/en/products/accessories/Polar_WearLink_transmitter_with_Bluetooth) over 
 Bluetooth. gVARVI is fully functional on Linux Systems. Windows support is experimental.
 
 To work propertly, gVarvi needs some external software:
 
 * [Python] (https://www.python.org/downloads/) (version 2)
 * [wxPython] (http://wxpython.org/download.php)
 * [PyGame] (www.pygame.org/)
 * [PyBluez] (https://pypi.python.org/pypi/PyBluez/)
 * [Matplotlib] (http://matplotlib.org/)
 * [PyUSB] (http://sourceforge.net/projects/pyusb/) (1.0.0a2 or later)
 * [Pyserial] (https://pypi.python.org/pypi/pyserial)
 * [msgpack-python] (https://pypi.python.org/pypi/msgpack-python/)
 * [VLC] (http://www.videolan.org/vlc/)
 
 If you want to use Pygame instead of VLC for video playback you need to change this line
```python
     from player.VideoPresentationPlayerVLC import VideoPresentationPlayer
```
 by this one
```python
     from player.VideoPresentationPlayerPygame import VideoPresentationPlayer
````
 at [VideoPresentation] (gvarvi/activities/VideoPresentation.py) module. Notice that Pygame only supports MPG video 
 format (more info [here] (http://www.pygame.org/docs/ref/movie.html))
 
 Binaries for debian based distributions are available [here] (https://github.com/milegroup/gVarvi/tree/master/dist)
