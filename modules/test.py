from common.plugin import PluginBase
from PIL import Image
import asyncio, random
class TestPlugin(PluginBase):

    '''
    A basic plugin implementation that renders colored squares.
    In this example, we maintain a single canvas rather than
    create one for each draw() call.
    '''

    def __init__(self, dimensions, display_manager):
        self.display_manager = display_manager
        self._canvas: Image = Image.new("RGB", dimensions)

        self._canvas.paste( (0, 0, 255), (0, 0, self._canvas.width//2, self._canvas.height//2) )
        self._canvas.paste( (255, 0, 255), (self._canvas.width//2, 0, self._canvas.width, self._canvas.height//2) )
        self._canvas.paste( (255, 255, 0), (0, self._canvas.height//2, self._canvas.width//2, self._canvas.height) )
        self._canvas.paste( (127, 127, 127), (self._canvas.width//2, self._canvas.height//2, self._canvas.width, self._canvas.height) )

        #asyncio.create_task(self.draw_loop())

    async def draw(self) -> Image:
        return self._canvas

    async def resize_requested(self, width, height):
        self._canvas = self._canvas.resize((width, height))

    # async def draw_loop(self):
    #     while True:
    #         print("Requesting draw")
    #         await asyncio.sleep(random.randint(3,10))
    #         await self.display_manager.request_plugin_immediate_draw(self)
    #         self._canvas = self._canvas.rotate(30)
        

def setup(dimensions, display_manager):
    return TestPlugin(dimensions, display_manager)