from common.layout import Layout

class DisplayManager():

    def __init__(self, *, width = 64, height = 64):
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

    def update_display(self, *, redraw = False):
        if self._current_layout is None:
            raise Exception("No layout is currently selected")

        canvas = self._current_layout.draw(redraw = redraw)
        canvas.show()
        # TODO: Push this image onto an LED screen

    def switch_layout(self, layout):
        if not layout in self._layouts:
            raise Exception("Layout must be properly registered in order to switch to it")
        
        if self._current_layout is not None:
            self._current_layout.deactivated()
        
        self._current_layout = layout # This will be the same layout instance as in self._layouts because of the guards above
        self._current_layout.activated()
        self.update_display(redraw = True)
        

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

