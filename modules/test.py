from common.plugin import PluginBase
from PIL import Image

class TestPlugin(PluginBase):

    def __init__(self, canvas: Image):
        self._canvas: Image = canvas

    def draw(self) -> Image:
        self._canvas.paste( (0, 0, 255), (0, 0, self._canvas.width//2, self._canvas.height//2) )
        self._canvas.paste( (255, 0, 255), (self._canvas.width//2, 0, self._canvas.width, self._canvas.height//2) )
        self._canvas.paste( (255, 255, 0), (0, self._canvas.height//2, self._canvas.width//2, self._canvas.height) )
        self._canvas.paste( (127, 127, 127), (self._canvas.width//2, self._canvas.height//2, self._canvas.width, self._canvas.height) )
        return self._canvas

def setup(canvas):
    return TestPlugin(canvas)