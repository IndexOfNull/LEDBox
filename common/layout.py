from common.module_base import ModuleBase
from common.exc import PluginAlreadyRegistered
from PIL import ImageDraw, Image

class Layout():

    def __init__(self, window_manager, *, screen_width = 64, screen_height = 64):
        self._plugins: dict[str, ModuleBase] = {} # Map plugin-ids -> plugin
        self._plugin_coordinates: dict[ModuleBase, tuple(int, int, int, int)] = {}
        self._canvas = Image.new("RGB", (screen_width, screen_height))
        self._image_draw = ImageDraw.Draw()
        self._window_manager = window_manager

    @property
    def canvas(cls) -> Image:
        '''
        Called when the parent window manager asks for a frame. Should return a frame the window manager can render
        '''
        return cls._canvas

    def add_plugin(self, plugin: ModuleBase, *, width: int, height:int, x:int = 0, y:int = 0):
        '''
        Registers a plugin 
        '''
        if plugin in self._plugins:
            raise PluginAlreadyRegistered("Plugin has already been added to this layout")

        # TODO: Check for overlap

        self._plugins[plugin] = plugin
        self._plugin_coordinates[plugin] = (x, y, x + width, y + height)

    def draw(self) -> Image:
        '''
        Draws a fresh frame using all of the plugin canvases.

        Returns the Layout's canvas
        '''
        self._canvas.paste( (0, 0, 0), (0, 0, self._canvas.width, self._canvas.height)) # Fill entire screen with black

        for plugin in self._plugins.values():
            self._canvas.paste(plugin.canvas, self._plugin_coordinates[plugin])

        return self._canvas

    def update_plugin_frame(self, plugin):
        self._canvas.paste(plugin.canvas, self._plugin_coordinates[plugin])
