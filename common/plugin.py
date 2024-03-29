
from PIL import Image

class PluginBase():
   
    '''
    A base class for plugins. Basic implementations may only need
    to implement draw(). Plugins may create new Image instances for
    each frame rendered, or continuously update a single instance.
    This base class is configured to do the former.

    Remember: plugins must not resize their own windows!
    '''
 
    def __init__(self, dimensions: tuple[int, int], display_manager):
        # self._canvas: Image = canvas # Shared between Layout and Plugin (passed by reference)
        self._canvas_size = dimensions # Do not directly mutate
        self._width = dimensions[0] # Do not directly mutate
        self._height = dimensions[1]
        self.display_manager = display_manager # Reference to the parent window manager

    async def draw(self) -> Image:
        '''
        Draws the canvas of this plugin.
        This size of the returned canvas must match what the calling layout is expecting
        (i.e., plugins may not directly determine their own size).

        Any caller of this function should use the return value instead of the value of self.canvas
        While self._canvas may not necessarily be side-effected, users should note the possibility.

        Because of this, plugins have the freedom to generate a new canvas on each draw() call.
        Plugins may also continuously mutate a single canvas if they wish to do so.
        '''
        pass

    async def screen_updated(self):
        '''
        Called right after the screen updates.

        Plugins should not request a screen update (max recursion depth issue).
        '''
        return None

    async def teardown(self):
        '''
        Called when this plugin is unloaded
        '''
        pass

    async def resize_requested(self, width, height):
        '''
        Called when the parent layout requests a resize
        or when switching to a layout containing this plugin in a different size.

        Subclasses must properly resize their canvas in this function to avoid errors.
        Subclasses may also use super().resize_requested for convenience
        '''
        #self._canvas = self._canvas.resize((width, height))
        self._canvas_size = (width, height)
        self._width = width
        self._height = height

    async def deactivated(self):
        '''
        Called when this plugin is no longer visible.
        
        This can be triggered as the result of a layout switch only when moving from
        a layout where this plugin instance is visible to one where it is not.
        '''

    async def activated(self):
        '''
        Called when this plugin becomes visible.
        
        This can be triggered as the result of a layout switch
        only when the current layout contains this plugin instance where the previous layout did not .
        '''

    async def layout_switched(self, previous_layout, current_layout):
        '''
        Called when the layout has switched to a different layout also containing this plugin instance.
        This function is not called if the destination layout does not contain this plugin instance.
        '''
        pass

    async def request_draw(self):
        '''
        Asks the display manager to ask the currently active layout to request a draw
        '''
        await self.display_manager.request_plugin_immediate_draw(self)