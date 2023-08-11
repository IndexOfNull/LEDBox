from common.plugin import PluginBase
from common.exc import PluginAlreadyRegistered, PluginNotRegistered
from PIL import Image

from importlib import import_module

class Layout():

    def __init__(self, display_manager, *, screen_width = 64, screen_height = 64):
        self._plugins: list[PluginBase] = [] # Map plugin-ids -> plugin
        self._plugin_coordinates: dict[PluginBase, tuple(int, int, int, int)] = {}
        self._canvas = Image.new("RGB", (screen_width, screen_height))
        self.visible = False
        self._display_manager = display_manager

    @property
    def canvas(cls) -> Image:
        '''
        Called when the parent display manager asks for a frame. Should return a frame the display manager can render
        '''
        return cls._canvas

    def frame_requested(self) -> Image:
        '''
        Called when the parent DisplayManager asks for a frame
        '''
        self.draw()
        return self._canvas

    # TODO: Maybe make plugin parameter a string and resolve to an import automatically?
    def add_plugin(self, plugin: str | PluginBase, *, width: int, height:int, x:int = 0, y:int = 0) -> PluginBase:
        '''
        Registers a plugin.

        Initializes the plugin with a canvas based on its qualified path.

        Instances of PluginBase can be directly registered.
        Useful if one instance of a plugin needs to appear in multiple layouts (same-layout instancing is not supported).
        You will have to manually create a canvas call the plugin's setup() if you do this.
        '''

        if isinstance(plugin, str):
            plugin_module = import_module(plugin)
            plugin_canvas = Image.new("RGB", (width, height))
            plugin_instance = plugin_module.setup(plugin_canvas)
        elif isinstance(plugin, PluginBase):
            plugin_instance = plugin
            if plugin_instance.canvas.width != width or plugin_instance.canvas.height != height:
                raise Exception("Plugin's canvas does not match passed width and height")

        if plugin_instance in self._plugins:
            raise PluginAlreadyRegistered("Plugin has already been added to this layout")

        # TODO: Check for overlap

        self._plugins.append(plugin_instance)
        self._plugin_coordinates[plugin_instance] = (x, y, x + width, y + height)
        return plugin_instance

    def remove_plugin(self, plugin: PluginBase, *, redraw = True):
        if not plugin in self._plugins:
            raise PluginNotRegistered("Plugin is not registered in this layout")

        plugin.on_teardown()
        self._plugins.remove(plugin)
        del self._plugin_coordinates[plugin]

        if redraw:
            self.draw()

    def draw(self, *, redraw = False) -> Image:
        '''
        Draws a frame using all of the plugin canvases.
        
        redraw will ask plugins to update their frames

        Returns the Layout's canvas
        '''
        self._canvas.paste( (0, 0, 0), (0, 0, self._canvas.width, self._canvas.height)) # Fill entire screen with black

        for plugin in self._plugins:
            if redraw:
                plugin_canvas = plugin.draw()
            else:
                plugin_canvas = plugin.canvas

            try:
                self._canvas.paste(plugin_canvas, self._plugin_coordinates[plugin])
            except:
                print(f"{plugin} failed to paste onto layout. This is probably because the plugin illegally changed the size of its frame.")

        return self._canvas


    def refresh_plugin_frame(self, plugin):
        self._canvas.paste(plugin.canvas, self._plugin_coordinates[plugin])

    def activated(self):
        '''
        Called when the layout is being unhidden. This is called before a fresh draw when switching layouts.
        '''
        pass

    def deactivated(self):
        '''
        Called when the layout is being hidden, usually when switching to a different layout
        '''
        pass
