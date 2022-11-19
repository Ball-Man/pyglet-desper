from typing import Optional

import desper
import pyglet


class Loop(desper.Loop[desper.World]):
    """Pyglet specific Loop implementation.

    If set, ``interval`` is passed to
    :func:`pyglet.clock.schedule_interval` to define an upper bound
    to the framerate. Common values are ``1 / 60``, ``1 / 75``, etc.
    """

    def __init__(self, interval: Optional[float] = None):
        super().__init__()
        self.interval: Optional[float] = interval

    def iteration(self, dt: float):
        """Single loop iteration."""
        try:
            self._current_world.process(dt)
        except desper.SwitchWorld as ex:
            self.switch(ex.world_handle, ex.clear_current, ex.clear_next)

    def loop(self):
        """Execute main loop.

        Internally, the main pyglet loop is started
        with ``pyglet.app.run()``.

        To properly start the loop, use :meth:`start`.
        """
        pyglet.clock.schedule(self.iteration)

        if self.interval is None:
            pyglet.app.run()
            return

        pyglet.app.run(self.interval)

    def switch(self, world_handle: desper.Handle[desper.World],
               clear_current=False, clear_next=False):
        """Switch world and ensure correct dispatching of events.

        See :meth:`Loop._switch` for the basic behaviour.
        """
        super().switch(world_handle, clear_current, clear_next)

        world_handle().dispatch_enabled = True
