from PIL import Image

class PluginBase():

    def __init__(self, canvas: Image):
        self._canvas = canvas # Shared between Layout and Plugin (passed by reference)
        #self.window_manager = window_manager # Reference to the parent window manager

    @property
    def canvas(cls) -> Image:
        return cls._canvas

    def on_frame_requested(self, *, fresh = False):
        '''
        Called when the parent WindowManager asks this plugin to render data
        '''
        raise NotImplemented()

    def draw(self) -> Image:
        '''
        Draws the canvas of this plugin.
        '''
        pass

    def on_screen_updated(self):
        '''
        Called right after the screen updates.
        '''
        return None

    def on_animating_start(self):
        '''
        Called when the plugin's frame starts animating.
        Not automatically called when transitioning off screen (see on_animating_out_start)

        Currently not used
        '''
        pass

    def on_animating_finish(self):
        '''
        Called when the plugin's frame stops animating.
        Not automatically called when transitioning off screen (see on_animating_out_finsih)

        Currently not used
        '''
        pass


    def on_animating_out_start(self):
        '''
        Called when the plugin's frame is begins transitioning off screen

        Currently not used
        '''
        pass

    def on_animating_out_finish(self):
        '''
        Called when the plugin's frame is done transitioning off screen

        Currently not used
        '''
        pass

    def on_teardown(self):
        '''
        Called when this plugin is unloaded
        '''
        pass