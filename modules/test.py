from common.plugin import PluginBase
from PIL import Image

class TestPlugin(PluginBase):

    '''
    A basic plugin implementation that renders colored squares.
    In this example, we maintain a single canvas rather than
    create one for each draw() call.
    '''

    def __init__(self, dimensions, display_manager):
        self.display_manager = display_manager
        self._canvas: Image = Image.new("RGB", dimensions)

    def draw(self) -> Image:
        self._canvas.paste( (0, 0, 255), (0, 0, self._canvas.width//2, self._canvas.height//2) )
        self._canvas.paste( (255, 0, 255), (self._canvas.width//2, 0, self._canvas.width, self._canvas.height//2) )
        self._canvas.paste( (255, 255, 0), (0, self._canvas.height//2, self._canvas.width//2, self._canvas.height) )
        self._canvas.paste( (127, 127, 127), (self._canvas.width//2, self._canvas.height//2, self._canvas.width, self._canvas.height) )
        return self._canvas

    def resize_requested(self, width, height):
        print("Test plugin: Resize requested")
        self._canvas = self._canvas.resize((width, height))

    def screen_updated(self):
        print('Test plugin: Screen updated!')

def setup(dimensions, display_manager):
    return TestPlugin(dimensions, display_manager)