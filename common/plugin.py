

from PIL import Image

class PluginBase():

    def __init__(self, canvas: Image, display_manager):
        self._canvas: Image = canvas # Shared between Layout and Plugin (passed by reference)
        self.display_manager = display_manager # Reference to the parent window manager

    @property
    def canvas(cls) -> Image:
        return cls._canvas

    def draw(self) -> Image:
        '''
        Draws the canvas of this plugin.

        Any caller of this function should use the return value instead of the value of self.canvas
        While self._canvas may not necessarily be side-effected, users should note the possibility.
        '''
        pass

    def screen_updated(self):
        '''
        Called right after the screen updates.
        '''
        return None

    def teardown(self):
        '''
        Called when this plugin is unloaded
        '''
        pass

    def animating_start(self):
        '''
        Called when the plugin's frame starts animating.
        Not automatically called when transitioning off screen (see on_animating_out_start)

        Currently not used
        '''
        pass

    def animating_finish(self):
        '''
        Called when the plugin's frame stops animating.
        Not automatically called when transitioning off screen (see on_animating_out_finsih)

        Currently not used
        '''
        pass


    def animating_out_start(self):
        '''
        Called when the plugin's frame is begins transitioning off screen

        Currently not used
        '''
        pass

    def animating_out_finish(self):
        '''
        Called when the plugin's frame is done transitioning off screen

        Currently not used
        '''
        pass