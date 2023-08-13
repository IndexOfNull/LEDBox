import common.display_manager as dm
from time import sleep

display_manager = dm.DisplayManager(width=64, height=64)

l = display_manager.new_layout()
p = l.add_plugin("modules.test", width = 32, height = 32, x = 10, y = 10)
l.change_plugin_coords(p, x = 0, width = 48, height = 16, y = 32)

l2 = display_manager.new_layout()
l2.add_plugin(p, width = 16, height = 16, x = 32, y = 32)

display_manager.switch_layout(l)
display_manager.switch_layout(l2)