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
        self.downloaded_image = None
        self.dimensions = dimensions
        asyncio.create_task(self.draw_loop())

    async def draw(self) -> Image:
        return self.downloaded_image

    async def resize_requested(self, width, height):
        self._canvas = self._canvas.resize((width, height))

    async def draw_loop(self):
        while True:
            print("Requesting draw from httptest plugin")
            await asyncio.sleep(5)
            async with aiohttp.ClientSession() as sess:
                async with sess.get(choice(("https://i.imgur.com/gh586hQ.png", "https://i.imgur.com/vgxKgEJ.png"))) as resp:
                    # Subsequent HTTP requests go pretty fast (~100ms), probably because keep-alive
                    b = BytesIO(await resp.read()) # Consider reading in smaller blocks for larger files to avoid blocking for long periods
                    self.downloaded_image = Image.open(b).resize(self.dimensions) # Ideally your downloaded image will already be the correct dimensions
            await self.display_manager.request_plugin_immediate_draw(self)
        

def setup(dimensions, display_manager):
    return TestPlugin(dimensions, display_manager)