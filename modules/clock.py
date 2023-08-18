from common.plugin import PluginBase

from PIL import Image, ImageFont, ImageDraw
from datetime import datetime
import asyncio

class ClockPlugin(PluginBase):

    def __init__(self, dim, display_manager):
        super().__init__(dim, display_manager)
        self.show_seconds = False
        self._show_colon = False
        self.update_task = None

    async def draw(self):
        dt = datetime.now()
        text = f"{dt.hour:02d}:{dt.minute:02d}" + (f":{dt.second:02d}" if self.show_seconds else "")
        font = ImageFont.load("assets/unscii-8-alt.pil")
        text_dimensions = font.getbbox(text)[2:] # First two items of bounding box are just zeroes

        multiline = text_dimensions[0] > self._width
        if multiline: # Switch to multi-line
            time_components = text.split(":")
            bboxes = [font.getbbox(x)[2:] for x in time_components]
            v_spacing = 0 # pixels
            canvas_width = max([box[0] for box in bboxes])
            canvas_height = sum([box[1] for box in bboxes]) + v_spacing * (len(time_components) - 1)

            font_canvas = Image.new("RGBA", (canvas_width, canvas_height))
            draw = ImageDraw.Draw(font_canvas)

            cur_y = 0
            for text, bbox, ind in zip(time_components, bboxes, range(len(time_components))):
                draw.text((0, cur_y), text=text, fill=(15*(ind), 60*(ind+1), 60*(ind+2)), font=font)
                cur_y += bbox[1] + v_spacing
        else:
            font_canvas = Image.new("RGBA", (text_dimensions[0], text_dimensions[1]))
            draw = ImageDraw.Draw(font_canvas)
            if not self._show_colon:
                text = text.replace(':', ' ')
            draw.text((0, 0), text=text, fill=(0, 0, 0), font=font)

        final_canvas = Image.new("RGBA", self._canvas_size)
        final_canvas.paste(font_canvas, (0, 0), font_canvas)
        return final_canvas
    
    async def activated(self):
        print("Clock plugin activated")
        self.update_task = asyncio.create_task(self.update_loop())

    async def deactivated(self):
        print("Clock plugin deactivated")
        if self.update_task:
            self.update_task.cancel()

    async def update_loop(self):
        while True:
            await asyncio.sleep(1)
            self._show_colon = not self._show_colon
            await self.display_manager.request_immediate_draw()

def setup(dim, display_manager):
    return ClockPlugin(dim, display_manager)

if __name__ == "__main__":
    p = setup((64, 64), None)
    img = p.draw()
    img.show()