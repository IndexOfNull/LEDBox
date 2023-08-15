from common.plugin import PluginBase

from PIL import Image, ImageFont, ImageDraw
from datetime import datetime

class ClockPlugin(PluginBase):

    def __init__(self, dim, display_manager):
        super().__init__(dim, display_manager)
        self.show_seconds = False

    async def draw(self):
        dt = datetime.now()
        text = f"{dt.hour}:{dt.minute}" + (f":{dt.second}" if self.show_seconds else "")
        font = ImageFont.load("assets/unscii-8.pil")
        text_dimensions = font.getbbox(text)[2:] # First two items of bounding box are just zeroes

        multiline = text_dimensions[0] > self._width
        if multiline: # Switch to multi-line
            time_components = text.split(":")
            bboxes = [font.getbbox(x)[2:] for x in time_components]
            v_spacing = 0 # pixels
            canvas_width = max([box[0] for box in bboxes])
            canvas_height = sum([box[1] for box in bboxes]) + v_spacing * (len(time_components) - 1)

            font_canvas = Image.new("RGB", (canvas_width, canvas_height))
            draw = ImageDraw.Draw(font_canvas)

            cur_y = 0
            for text, bbox, ind in zip(time_components, bboxes, range(len(time_components))):
                draw.text((0, cur_y), text=text, fill=(15*(ind), 60*(ind+1), 60*(ind+2)), font=font)
                cur_y += bbox[1] + v_spacing
        else:
            font_canvas = Image.new("RGB", (text_dimensions[0], text_dimensions[1]))
            draw = ImageDraw.Draw(font_canvas)
            draw.text((0, 0), text=text, fill=(255, 255, 255), font=font)

        final_canvas = Image.new("RGB", self._canvas_size)
        final_canvas.paste(font_canvas, (0, 0))
        return final_canvas

def setup(dim, display_manager):
    return ClockPlugin(dim, display_manager)

if __name__ == "__main__":
    p = setup((64, 64), None)
    img = p.draw()
    img.show()