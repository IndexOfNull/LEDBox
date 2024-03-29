from common.plugin import PluginBase
from common.exc import PluginAlreadyRegistered, PluginNotRegistered
from PIL import Image

from importlib import import_module
import asyncio
import random

class Layout():

    def __init__(self, display_manager, *, screen_width = 64, screen_height = 64):
        self._plugins: list[PluginBase] = []
        self._plugin_coordinates: dict[PluginBase, tuple(int, int, int, int)] = {}
        self._plugin_z_index: dict[PluginBase, int] = {}
        self._canvas = Image.new("RGB", (screen_width, screen_height))
        self._visible = False
        self._display_manager = display_manager
        self.debug_borders = False

    @property
    def plugins(cls):
        return cls._plugins

    def frame_requested(self) -> Image:
        '''
        Called when the parent DisplayManager asks for a frame
        '''
        self.draw()
        return self._canvas

    # TODO: Maybe make plugin parameter a string and resolve to an import automatically?
    def add_plugin(self, plugin: str | PluginBase, *, width: int, height:int, x:int = 0, y:int = 0, z_index:int = 0, **kwargs) -> PluginBase:
        '''
        Registers a plugin.

        Initializes the plugin with a canvas based on its qualified path.

        Instances of PluginBase can be directly registered.
        Useful if one instance of a plugin needs to appear in multiple layouts (same-layout instancing is not supported).
        You will have to manually create a canvas call the plugin's setup() if you do this.
        '''

        if isinstance(plugin, str):
            plugin_module = import_module(plugin)
            plugin_instance = plugin_module.setup((width, height), self._display_manager, **kwargs)
        elif isinstance(plugin, PluginBase):
            plugin_instance = plugin

        if plugin_instance in self._plugins:
            raise PluginAlreadyRegistered("Plugin has already been added to this layout")

        # TODO: Check for overlap

        self._plugins.append(plugin_instance)
        self._plugin_coordinates[plugin_instance] = (x, y, x + width, y + height)
        self._plugin_z_index[plugin_instance] = z_index
        return plugin_instance

    async def remove_plugin(self, plugin: PluginBase, *, redraw = True):
        if not plugin in self._plugins:
            raise PluginNotRegistered("Plugin is not registered in this layout")

        await plugin.teardown()
        self._plugins.remove(plugin)
        del self._plugin_coordinates[plugin]

        if redraw:
            self.draw()

    def get_plugin(self, plugin: PluginBase):
        '''
        Returns a plugin instance if it exists within the layout
        '''
        if plugin not in self._plugins:
            return None
        return plugin

    def _get_z_ordered_plugin_list(self, *, pairs:bool = False, reverse:bool = False):
        '''
        Returns member plugins ordered by their z-index. Pairs will return (z-index, plugin) tuples.
        '''
        sorted_plugins = [(z_ind, plugin) for plugin, z_ind in self._plugin_z_index.items()]
        sorted_plugins.sort(key = lambda x: x[0], reverse = reverse)
        if pairs:
            return sorted_plugins
        else:
            return [plugin for _, plugin in sorted_plugins]

    async def draw(self) -> Image:
        '''
        Draws a frame using all of the plugin canvases.

        Returns the Layout's canvas
        '''
        self._canvas.paste( (0, 0, 0), (0, 0, self._canvas.width, self._canvas.height)) # Fill entire screen with black

        tasks = {} # Make a copy dict in case plugins gets mutated asyncronously, i guess
        sorted_plugins = self._get_z_ordered_plugin_list() # Get plugins in order by their z-index. Code below asumes this is the draw order

        for plugin in sorted_plugins:
            tasks[plugin] = asyncio.wait_for(plugin.draw(), timeout=0.1) # 100 ms to draw

        canvases = await asyncio.gather(*tasks.values(), return_exceptions = True)
        for canvas, plugin in zip(canvases, tasks.keys()):
            if not canvas:
                continue
            if isinstance(canvas, Exception):
                print(f"Warning: {plugin} draw() call returned an exception and could not be composited:", canvas)
                continue # Skip compositiing a plugin if it's draw function has errored

            try:
                coords = self._plugin_coordinates[plugin]
                if self.debug_borders:
                    border_w = 1 # pixel
                    border_im = Image.new("RGB", (canvas.width + border_w * 2, canvas.height + border_w * 2), tuple(random.sample(range(0, 255), 3)))
                    border_im.paste(canvas, (border_w, border_w))
                    canvas = border_im
                    coords = (coords[0]-border_w, coords[1]-border_w, coords[2]+border_w, coords[3]+border_w)
                self._canvas.paste(canvas, coords, (canvas if canvas.mode == "RGBA" else None))
            except Exception as e:
                print(f"{plugin} failed to paste onto layout. This is probably because the plugin illegally changed the size of its frame: {e}")

        return self._canvas

    async def screen_updated(self):
        '''
        Called right after the screen updates.
        Only called if the current layout is active.
        Subclasses should take care to call screen_updated on registered plugins.
        Subclasses can use super().screen_updated to achieve this

        Subclasses should also take care to not trigger another screen update with this function (infinite loop).
        '''
        # TODO: Rewrite to call all coroutines at once
        tasks = [plugin.screen_updated() for plugin in self._plugins]
        await asyncio.gather(*tasks, return_exceptions = True)

    async def change_plugin_coords(self, plugin: PluginBase, *, x:int = None, y:int = None, width:int = None, height:int = None, z_index:int = None, redraw = False):
        old_coords = self._plugin_coordinates[plugin]
        old_width = abs(old_coords[2] - old_coords[0])
        old_height = abs(old_coords[3] - old_coords[1])
        new_coords = list(old_coords)

        # Take care of shifting along x and y before worrying about updating x2 and y2 for width and height
        if x is not None:
            new_coords[0] = x
            new_coords[2] = x + old_width
        if y is not None:
            new_coords[1] = y
            new_coords[3] = y + old_height
        if width is not None:
            new_coords[2] = new_coords[0] + width
        if height is not None:
            new_coords[3] = new_coords[1] + height

        new_width = (width if width is not None else old_width)
        new_height = (height if height is not None else old_height)

        if z_index is not None:
            self._plugin_z_index[plugin] = z_index

        self._plugin_coordinates[plugin] = tuple(new_coords)
        await plugin.resize_requested(new_width, new_height)
        if redraw:
            await self._display_manager.request_immediate_draw()

    async def handle_plugin_changeover(self):
        '''
        Called when this layout becomes active (before activated is called)
        Notifies plugins that this layout is visible and asks them to resize accordingly.

        This function is separated for the convenience of subclasses.
        '''
        tasks = []
        for plugin, dimensions in self._plugin_coordinates.items():
            width = abs(dimensions[2] - dimensions[0])
            height = abs(dimensions[3] - dimensions[1])
            tasks.append(plugin.resize_requested(width, height))
        await asyncio.gather(*tasks, return_exceptions = True)

    # This is kind of janky and arguably it would be better to 
    async def plugin_draw_requested(self, plugin: PluginBase) -> Image:
        '''
        Called by the display manager when a plugin requests a screen draw. Partial redraw will redraw only the passed plugin (can cause z-index issues)
        '''
        plugin = self.get_plugin(plugin)
        if not plugin:
            return

        canvas = await plugin.draw()
        self._canvas.paste( (0, 0, 0), self._plugin_coordinates[plugin])
        self._canvas.paste(canvas, self._plugin_coordinates[plugin])
        return self._canvas

    async def activated(self, previous_layout):
        '''
        Called when the layout is being unhidden. This is called before a fresh draw when switching layouts.
        '''
        self._visible = True

    async def deactivated(self, next_layout):
        '''
        Called when the layout is being hidden, usually when switching to a different layout
        '''
        self._visible = False
