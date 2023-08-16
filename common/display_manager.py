from common.layout import Layout
from common.plugin import PluginBase

import asyncio

class DisplayManager():

    def __init__(self, matrix = None, *, width = 64, height = 64):
        self.matrix = matrix
        self._layouts: dict[Layout] = []
        self._screen_width = width
        self._screen_height = height
        self._current_layout = None

    @property
    def layouts(cls):
        return cls._layouts
    
    @property
    def current_layout(cls):
        return cls._current_layout

    async def update_display(self, *, canvas = None):
        '''
        Updates the display. If the canvas parameter is left blank,
        a draw() call will be made on current layout.
        '''

        if self._current_layout is None:
            raise Exception("No layout is currently selected")

        if not canvas:
            canvas = await self._current_layout.draw()

        await self.current_layout.screen_updated()

        if self.matrix:
            self.matrix.SetImage(canvas)

    async def switch_layout(self, layout):
        if not layout in self._layouts:
            raise Exception("Layout must be properly registered in order to switch to it")
        
        # Callbacks on layout member plugins
        shared_plugins = []
        deactivating_plugins = []
        if self._current_layout is not None:
            shared_plugins = [plugin for plugin in self.current_layout.plugins if plugin in layout.plugins] # Plugins shared by both layouts
            
            deactivating_plugins = [plugin for plugin in self.current_layout.plugins if plugin not in shared_plugins]
            deactivation_tasks = [plugin.deactivated() for plugin in deactivating_plugins]
            await asyncio.gather(*deactivation_tasks, return_exceptions = True)

        activating_plugins = [plugin for plugin in layout.plugins if plugin not in shared_plugins]
        activation_tasks = [plugin.activated() for plugin in activating_plugins]
        await asyncio.gather(*activation_tasks, return_exceptions = True)

        layout_switch_tasks = [plugin.layout_switched(self.current_layout, layout) for plugin in shared_plugins + activating_plugins + deactivating_plugins]
        await asyncio.gather(*layout_switch_tasks, return_exceptions = True)

        # Call layout callbacks after we handle plugins
        if self._current_layout is not None:
            await self._current_layout.deactivated(layout)

        previous_layout = self.current_layout
        self._current_layout = layout # This will be the same layout instance as in self._layouts because of the guards above
        await layout.handle_plugin_changeover()
        await layout.activated(previous_layout)
        await self.update_display()
        

    def new_layout(self, layout_cls = None):
        '''
        Initializes a new layout and returns it to the caller.

        layout_cls can be used to specify a custom Layout subclass
        '''
        if not layout_cls:
            layout_cls = Layout

        l = layout_cls(self, screen_width = self._screen_width, screen_height = self._screen_height)
        self._layouts.append(l)
        return l

    # Doing things this way is a bit janky and it may just be better to just call update_display()
    async def request_plugin_immediate_draw(self, plugin: PluginBase):
        '''
        A function for plugins to directly ask for their draw() function to be called.

        Intended for immediate-mode style applications
        '''
        canvas = await self._current_layout.plugin_draw_requested(plugin)
        if canvas:
            await self.update_display(canvas = canvas)
            return True
        return False