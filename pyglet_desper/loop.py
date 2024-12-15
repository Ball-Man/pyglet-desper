from typing import Optional
import functools

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
        self._current_world.process(dt)

    def loop(self):
        """Execute main loop.

        Internally, the main pyglet loop is started
        with ``pyglet.app.run()``.

        To properly start the loop, use :meth:`start`.
        """
        # Keep rescheduling the main loop until all windows are closed
        while pyglet.app.windows and not pyglet.app.event_loop.has_exit:
            try:
                if self.interval is None:
                    pyglet.app.run()
                else:
                    pyglet.app.run(self.interval)

            except desper.SwitchWorld as ex:
                self.switch(ex.world_handle, ex.clear_current, ex.clear_next)

            # Prevent window redraw from scheduling multiple times
            pyglet.clock.unschedule(pyglet.app.event_loop._redraw_windows)

    def switch(self, world_handle: desper.Handle[desper.World],
               clear_current=False, clear_next=False):
        """Switch world and ensure correct dispatching of events.

        See :meth:`Loop._switch` for the basic behaviour.
        """
        super().switch(world_handle, clear_current, clear_next)

        pyglet.clock.unschedule(self.iteration)
        if self.interval is None:
            pyglet.clock.schedule(self.iteration)
        else:
            pyglet.clock.schedule_interval(self.iteration, self.interval)

        world_handle().dispatch_enabled = True

    @functools.cache
    def _generate_window_handler(self, event_name: str):
        """Generate a handler for a :class:`pyglet.window.Window`.

        Results are cached so that disconnecting the handler is
        possible.
        """

        def dispatch(*args, **kwargs):
            if self.current_world is not None:
                self.current_world.dispatch(event_name, *args, **kwargs)

        return dispatch

    def connect_window_events(self, window: pyglet.window.Window,
                              *event_names: str):
        """Connect pyglet events to desper's event system.

        Events specified through ``event_names`` are connected so
        that when dispatched from ``window``, they will be also
        dispatched by :attr:`current_world`. In this way, desper event
        handlers (:func:`event_handler`) can nimbly receive pyglet
        events.
        """
        handlers = [self._generate_window_handler(event)
                    for event in event_names]

        window.set_handlers(**dict(zip(event_names, handlers)))

    def disconnect_window_events(self, window: pyglet.window.Window,
                                 *event_names: str):
        """Disconnect pyglet events from desper's event system.

        Specified event names will no longer be propagated to the
        current world (:attr:`current_world`). Antagonistic with respect
        to :meth:`connect_window_events`.
        """
        handlers = [self._generate_window_handler(event)
                    for event in event_names]

        window.remove_handlers(**dict(zip(event_names, handlers)))
