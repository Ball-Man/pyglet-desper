"""Synchronize pyglet graphics with desper ``Transform`` components.

High level graphic abstractions in pyglet (e.g. ``Sprite``) make use
of specific properties to handle and transform vertices. Most commonly,
positional properties (``Sprite.x``, ``Sprite.y``, etc.).
Due to the variety of existing graphical classes, the risk in handling
these properties directly is the injection in the project's
structure of strong dependencies based on pyglet objects and types.

To prevent this, a connection (or synchronization) between pyglet
classes and :class:`desper.Transform2D` is proposed (as pyglet
abstractions are mostly 2D, 3D support will be discussed in the future).
"""
import desper
import pyglet


@desper.event_handler(desper.ON_REMOVE_EVENT_NAME)
class GraphicSync2D(desper.Controller):
    """Base class for pyglet graphical components synchronization.

    It encapsules management of position, rotation and scale by using
    the most common related pyglet properites, synchronizing them
    with the :class:`desper.Transform2D`. In particular:

    - ``x`` and ``y`` for updating position.
    - ``rotation`` for updating rotation.
    - ``scale_x`` and ``scale_y`` for updating scale.

    Even though all these interactions are defined, they are not
    enabled. In fact, this component does nothing on its own, but
    defines base behaviours that can be exploited by specialized
    subclasses. This is done since not all the graphical components
    support the same transformations. Actually, most of them only
    support repositioning with ``x`` and ``y``, or with
    the ``position`` tuple.

    In particular, to enable a connection
    with :class:`desper.Transform2D` it is advisable to subclass this
    component and apply to it the :func:`desper.event_handler`
    decorator, enabling the desired event connections (any of
    :attr:`desper.ON_POSITION_CHANGE_EVENT_NAME`,
    :attr:`desper.ON_ROTATION_CHANGE_EVENT_NAME`,
    :attr:`desper.ON_SCALE_CHANGE_EVENT_NAME`, i.e.
    ``'on_position_change'``, ``'on_rotation_change'``,
    ``'on_scale_change'``). Override homonymous methods to define
    custom behaviour.

    Moreover, the :attr:`desper.ON_REMOVE_EVENT_NAME`
    (i.e. ``'on_remove'``) event is automatically handled, calling on
    the referred graphical component the :func:`delete` method
    (e.g. :meth:`pyglet.Sprite.delete`), which is fundamental to
    correctly delete vertices of graphical components when removed in
    real time.
    """
    deleted = False

    def __init__(self, component_type: type):
        self.component_type = component_type

    def on_add(self, entity, world: desper.World):
        """Subscribe to :class:`desper.Transform2D` for events."""
        super().on_add(entity, world)

        transform = world.get_component(entity, desper.Transform2D)
        assert transform is not None, (
            'A Transform2D component must be added first '
            f'for {self.__class__} to work')
        transform.add_handler(self)

        # Apply immediately supported transformations
        if desper.ON_POSITION_CHANGE_EVENT_NAME in self.__events__:
            self.on_position_change(transform.position)

        if desper.ON_ROTATION_CHANGE_EVENT_NAME in self.__events__:
            self.on_rotation_change(transform.rotation)

        if desper.ON_SCALE_CHANGE_EVENT_NAME in self.__events__:
            self.on_scale_change(transform.scale)

    def on_remove(self, entity, world: desper.World):
        """Clear vertices from memory."""
        if not self.deleted:
            self.deleted = True
            self.get_component(self.component_type).delete()

    def on_position_change(self, new_position: desper.math.Vec2):
        """Event handler: update graphical component position."""
        self.get_component(self.component_type).position = new_position

    def on_rotation_change(self, new_rotation: float):
        """Event handler: update graphical component rotation."""
        self.get_component(self.component_type).rotation = new_rotation

    def on_scale_change(self, new_scale: desper.math.Vec2):
        """Event handler: update graphical component's scale.

        Possibly only supported by :class:`pyglet.sprite.Sprite`.
        """
        self.get_component(self.component_type).update(scale_x=new_scale[0],
                                                       scale_y=new_scale[1])


@desper.event_handler(desper.ON_POSITION_CHANGE_EVENT_NAME,
                      desper.ON_ROTATION_CHANGE_EVENT_NAME,
                      desper.ON_SCALE_CHANGE_EVENT_NAME)
class SpriteSync(GraphicSync2D):
    """Synchronize :class:`desper.Transform2D` with pyglet ``Sprite``.

    Handles all transformation events.

    The :attr:`desper.ON_REMOVE_EVENT_NAME`
    (i.e. ``'on_remove'``) event is automatically handled, calling on
    the referred ``Sprite`` component the :func:`delete` method,
    which is fundamental to correctly delete vertices of graphical
    components when removed in real time.

    This also means that ideally a ``Sprite`` instance and its
    associated ``SpriteSync`` shall be added, removed from the world in
    an entangled fashion.

    Target class (``component_type``) defaults to
    :class:`pyglet.sprite.Sprite`, but can be specialized to get
    extra performance during component resolution (e.g. by specifying
    :class:`pyglet-desper.Sprite`).

    See :class:`GraphicSync2D` for more info.
    """

    def __init__(self, component_type: type = pyglet.sprite.Sprite):
        super().__init__(component_type)

    def on_add(self, entity, world):
        """Custom handler for better performance."""
        self.entity = entity
        self.world = world

        transform = world.get_component(entity, desper.Transform2D)
        assert transform is not None, (
            'A Transform2D component must be added first '
            f'for {self.__class__} to work')
        transform.add_handler(self)

        # Apply immediately supported transformations
        # Stack them and apply in one go for better performance
        transformations = {}

        transformations['x'] = transform.position[0]
        transformations['y'] = transform.position[1]

        transformations['rotation'] = transform.rotation

        transformations['scale_x'] = transform.scale[0]
        transformations['scale_y'] = transform.scale[1]

        self.get_component(self.component_type).update(**transformations)

    def on_position_change(self, new_position: desper.math.Vec2):
        """Event handler: update graphical component position."""
        self.get_component(self.component_type).position = (*new_position, 0.)


@desper.event_handler(desper.ON_POSITION_CHANGE_EVENT_NAME)
class PositionSync2D(GraphicSync2D):
    """Synchronize :class:`desper.Transform2D` position with graphics.

    Handles the :attr:`desper.ON_POSITION_CHANGE_EVENT_NAME` event.

    The :attr:`desper.ON_REMOVE_EVENT_NAME`
    (i.e. ``'on_remove'``) event is automatically handled, calling on
    the referred graphical component the :func:`delete` method,
    which is fundamental to correctly delete vertices of graphical
    components when removed in real time.

    This also means that ideally a graphical instance and its
    associated ``PositionSync2D`` shall be added, removed from the world
    in an entangled fashion.

    See :class:`GraphicSync2D` for more info.
    """


@desper.event_handler(desper.ON_POSITION_CHANGE_EVENT_NAME,
                      desper.ON_ROTATION_CHANGE_EVENT_NAME)
class PositionRotationSync2D(GraphicSync2D):
    """Same as :class:`PositionSync2D` but also synchronizes rotation.

    See :class:`PositionSync2D`.
    """


def arc_sync_component() -> PositionRotationSync2D:
    """Get a sync component for :class:`pyglet.shapes.Arc`s.

    See :class:`PositionRotationSync2D`.
    """
    return PositionRotationSync2D(pyglet.shapes.Arc)


def circle_sync_component() -> PositionSync2D:
    """Get a sync component for :class:`pyglet.shapes.Circle`s.

    See :class:`PositionSync2D`.
    """
    return PositionSync2D(pyglet.shapes.Circle)


def ellipse_sync_component() -> PositionRotationSync2D:
    """Get a sync component for :class:`pyglet.shapes.Ellipse`s.

    See :class:`PositionRotationSync2D`.
    """
    return PositionRotationSync2D(pyglet.shapes.Ellipse)


def sector_sync_component() -> PositionRotationSync2D:
    """Get a sync component for :class:`pyglet.shapes.Sector`s.

    See :class:`PositionRotationSync2D`.
    """
    return PositionRotationSync2D(pyglet.shapes.Sector)


def line_sync_component() -> PositionSync2D:
    """Get a sync component for :class:`pyglet.shapes.Line`s.

    See :class:`PositionSync2D`.
    """
    return PositionSync2D(pyglet.shapes.Line)


def rectangle_sync_component() -> PositionRotationSync2D:
    """Get a sync component for :class:`pyglet.shapes.Rectangle`s.

    See :class:`PositionRotationSync2D`.
    """
    return PositionRotationSync2D(pyglet.shapes.Rectangle)


def borderedrectangle_sync_component() -> PositionRotationSync2D:
    """Get a sync component for :class:`pyglet.shapes.BorderedRectangle`s.

    See :class:`PositionRotationSync2D`.
    """
    return PositionRotationSync2D(pyglet.shapes.BorderedRectangle)


def triangle_sync_component() -> PositionSync2D:
    """Get a sync component for :class:`pyglet.shapes.Triangle`s.

    See :class:`PositionSync2D`.
    """
    return PositionSync2D(pyglet.shapes.Triangle)


def star_sync_component() -> PositionRotationSync2D:
    """Get a sync component for :class:`pyglet.shapes.Star`s.

    See :class:`PositionRotationSync2D`.
    """
    return PositionRotationSync2D(pyglet.shapes.Star)


def polygon_sync_component() -> PositionRotationSync2D:
    """Get a sync component for :class:`pyglet.shapes.Polygon`s.

    See :class:`PositionRotationSync2D`.
    """
    return PositionRotationSync2D(pyglet.shapes.Polygon)


def htmllabel_sync_component() -> PositionRotationSync2D:
    """Get a sync component for :class:`pyglet.text.HTMLLabel`.

    See :class:`PositionRotationSync2D`.
    """
    return PositionRotationSync2D(pyglet.text.HTMLLabel)


def documentlabel_sync_component() -> PositionRotationSync2D:
    """Get a sync component for :class:`pyglet.text.DocumentLabel`.

    See :class:`PositionRotationSync2D`.
    """
    return PositionRotationSync2D(pyglet.text.DocumentLabel)


def label_sync_component() -> PositionRotationSync2D:
    """Get a sync component for :class:`pyglet.text.Label`.

    See :class:`PositionRotationSync2D`.
    """
    return PositionRotationSync2D(pyglet.text.Label)
