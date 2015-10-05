#!/usr/bin/env python
"""This script defines a snowflake emitting widget"""

from kivy.uix.image import Image
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.animation import Animation
import random

RESOURCES = "/sdcard/btsync/ensikello"


class RotatingImage(Image): #pylint:disable=too-many-public-methods
    """Defines a rotating image class with necessary class variables"""

    layout = ObjectProperty()
    animation = None
    angle = NumericProperty()
    index = NumericProperty()


class Snowflakes(object): #pylint:disable=too-many-public-methods
    """Defines a Snowflakes class which is able to emit snowflakes into
    layout by using a basic widget recycling mechanism"""

    layout = None
    flakes = []
    flake_animations = []
    flake_index = 0
    flake_side_minimum = None
    flake_side_maximum = None

    def create_snowflake(self):
        """Creates a snowflake. It's acceptable to create these only
        in application startup"""

        flake = RotatingImage(layout=self.layout)
        flake.source = "%s/snowflakes/snowflake%d.png" % (
            RESOURCES, self.flake_index)
        flake.index = self.flake_index
        flake.opacity = 0
        self.flakes.append(flake)
        self.layout.add_widget(flake)

    def reset_snowflake(self, flake):
        """Resets properties of one individual snowflake"""

        self.flake_side_minimum = self.layout.width / 7
        self.flake_side_maximum = self.layout.width / 3
        if flake.animation is not None:
            flake.animation.stop(flake)
        side = random.randrange(
            self.flake_side_minimum,
            self.flake_side_maximum)
        flake.size = side, side
        flake.x = random.randrange(-self.flake_side_maximum, self.layout.width)
        flake.y = self.layout.height
        self.layout.remove_widget(flake)
        self.layout.add_widget(flake)
        flake.opacity = 1
        flake.animation = \
            Animation(y=-self.flake_side_maximum,
        duration=5 + (self.flake_side_maximum * 1.01 / side) * 5) & \
            Animation(opacity=0, duration=10) & \
            Animation(angle=random.randrange(-360, 360),
        duration=random.randrange(10, 50))
        flake.animation.start(flake)

    def emit(self):
        """Emits one snowflake"""

        # Use widget recycling with pre-created snowflakes
        if self.flake_index == len(self.flakes):
            self.flake_index = 0
        flake = self.flakes[self.flake_index]
        self.reset_snowflake(flake)
        self.flake_index = self.flake_index + 1

    def init(self, layout):
        """Initializes class variables and does startup operations"""

        self.layout = layout

        # Create snowflakes which will be used via widget recycling later on
        for flake_index in range(12):
            self.create_snowflake()
            self.flake_index = flake_index
