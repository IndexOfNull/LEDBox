import common.display_manager as dm
import time
import asyncio

# For some reason importlib throws a fit when I don't do this ¯\_(ツ)_/¯
from modules import test, httptest

matrix = None
try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.brightness = 50
    options.hardware_mapping = 'adafruit-hat-pwm'
    options.pixel_mapper_config = 'U-mapper;Rotate:180'

    matrix = RGBMatrix(options = options)
except ImportError:
    pass

display_manager = dm.DisplayManager(matrix, width=64, height=64)

async def main():
    l = display_manager.new_layout()
    p = l.add_plugin("modules.test", width = 32, height = 32, x = 10, y = 10)
    p = l.add_plugin("modules.httptest", width = 30, height = 38, x = 64-30, y = 64-38)

    l2 = display_manager.new_layout()
    l2.add_plugin(p, width = 16, height = 16, x = 32, y = 32)

    await display_manager.switch_layout(l)

    end_time = 0
    while True:
        start_time = time.perf_counter()
        await display_manager.update_display()
        interframe_time = time.perf_counter() - end_time
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f"Frame time: {total_time*1000} ms, {1/total_time} fps, {interframe_time} dT")
        await asyncio.sleep(1)
        # print("Changing plugin coords")
        # await l.change_plugin_coords(p, x = randint(0, 32), y = randint(0, 32))

if __name__ == "__main__":
    asyncio.run(main())
