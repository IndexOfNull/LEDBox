from common.plugin import PluginBase
from PIL import Image
import asyncio
import aiohttp
from io import BytesIO
from random import choice

class TestPlugin(PluginBase):

    '''
    A basic plugin implementation that renders colored squares.
    In this example, we maintain a single canvas rather than
    create one for each draw() call.
    '''

    def __init__(self, dimensions, display_manager):
        self.display_manager = display_manager
        self._canvas: Image = Image.new("RGB", dimensions)
        self.dimensions = dimensions
        self._images = []
        self._current_image_ind = 0
        self.hold_time = 10
        asyncio.create_task(self.scroller_loop())

    @property
    def images(cls):
        return cls.images

    def add_image(self, image:str, *, encoding = None):
        with open(image, 'rb') as f:
            img = Image.open(f).convert("RGBA")
            self._images.append(img)
            return img

    async def draw(self) -> Image:
        try:
            return self._images[self._current_image_ind]
        except IndexError:
            return None

    async def resize_requested(self, width, height):
        self._canvas = self._canvas.resize((width, height))

    async def scroller_loop(self):
        while True:
            await asyncio.sleep(self.hold_time)
            self._current_image_ind += 1
            if self._current_image_ind == len(self._images):
                self._current_image_ind = 0
            await self.display_manager.request_immediate_draw()

        

def setup(dimensions, display_manager):
    return TestPlugin(dimensions, display_manager)