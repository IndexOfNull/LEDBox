from common.plugin import PluginBase

from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
import asyncio

class DebugTextPlugin(PluginBase):

    def __init__(self, dim, display_manager, *, text = '', multiline = True):
        super().__init__(dim, display_manager)
        self.text = text
        self.multiline = multiline

    async def draw(self):
        font_canvas = Image.new("RGBA", self._canvas_size)
        draw = ImageDraw.Draw(font_canvas)
        font = ImageFont.load("assets/fonts/unscii-8-alt.pil")
        if self.multiline:
            draw.multiline_text((0, 0), text=self.text, fill=(255, 255, 255), font=font)
        else:
            draw.text((0, 0), text=self.text, fill=(255, 255, 255), font=font)
        return font_canvas

def setup(dim, display_manager, **kwargs):
    return DebugTextPlugin(dim, display_manager, **kwargs)