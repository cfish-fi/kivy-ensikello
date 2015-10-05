#!/usr/bin/env python
"""This script defines Ensikello entry point and main logic"""

import datetime

import kivy
kivy.require('1.7.0')

from kivy.utils import platform
from kivy.config import Config
Config.set('kivy', 'log_enable', '0')
if platform == 'android':
    Config.set('kivy', 'log_level', 'critical')
else:
    Config.set('kivy', 'log_level', 'info')
    Config.set('graphics', 'width', '800')
    Config.set('graphics', 'height', '480')
Config.set('graphics', 'multisamples', '0')
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty
from kivy.clock import Clock
from audioplayer import AudioPlayer
from snowflakes import Snowflakes
from datetime import datetime
from kivy.uix.image import Image
from kivy.uix.label import Label
import clocksettings
from kivy.vector import Vector
from itertools import izip, cycle, tee
import os
import os.path

# globals
RESOURCES = "/sdcard/btsync/ensikello"


class WeekLabel(Label): #pylint:disable=too-many-public-methods
    """Defines a label which displays weekdays"""

    day = NumericProperty(0)


class FullImage(Image): #pylint:disable=too-many-public-methods
    """Defines an image which extends to the full canvas"""

    pass


class DragArea(Label): #pylint:disable=too-many-public-methods
    """Defines a class which implements a draggable area for changing bg"""

    app = None
    touch_start_pos = None

    @staticmethod
    def pairwise(seq):
        """Returns the current and the next items in sequence"""

        current_item, next_item = tee(seq)
        next(next_item)
        return izip(current_item, next_item)

    def on_touch_down(self, touch):
        """Starts to track dragging if initiated within DragArea"""

        if self.collide_point(*touch.pos):
            touch.grab(self)
            self.touch_start_pos = (0, touch.y)
            return True

    def on_touch_move(self, touch):
        """Changes background opacity based on dragged distance"""

        if touch.grab_current is self:
            drag_distance = Vector((0, touch.y)).distance(self.touch_start_pos)
            self.app.layout.ids.bg.opacity = max(
                0, 1 - (1.0 / (self.app.layout.height * 0.3) * drag_distance))
            self.app.layout.ids.bg.y = touch.y - self.touch_start_pos[1]

    def on_touch_up(self, touch):
        """If dragged far enough, loads the next/previous bg"""

        touch.ungrab(self)
        if self.app.layout.ids.bg.opacity == 0:
            self.app.update_backgrounds()
            direction = "next"
            if touch.y < self.touch_start_pos[1]:
                direction = "previous"
            for elem, next_elem in self.pairwise(cycle(self.app.backgrounds)):
                if direction == "next" and elem == self.app.config.get(
                        self.app.mode, 'background'):
                    self.app.config.set(self.app.mode, 'background', next_elem)
                    self.app.on_config_change(
                        self.app.config, self.app.mode, 'background', next_elem)
                    self.app.config.write()
                    break
                elif direction == "previous" and \
                     next_elem == self.app.config.get(
                         self.app.mode, 'background'):
                    self.app.config.set(
                        self.app.mode, 'background', elem)
                    self.app.on_config_change(
                        self.app.config, self.app.mode, 'background', elem)
                    self.app.config.write()
                    break
        self.app.layout.ids.bg.opacity = 1
        self.app.layout.ids.bg.y = 0


class ClockLayout(FloatLayout): #pylint:disable=too-many-public-methods
    """Defines a clock layout, consisting of needles"""

    pass


class ClockApp(App): #pylint:disable=too-many-public-methods,too-many-instance-attributes
    """Defines the main class for Ensikello"""

    use_kivy_settings = False

    layout = None
    snowflakes = None
    audioplayer = None
    clocksettings = None
    backgrounds = []

    hours_needle_angle = NumericProperty(0)
    minutes_needle_angle = NumericProperty(0)
    seconds_needle_angle = NumericProperty(0)
    microseconds_needle_angle = NumericProperty(0)
    day = NumericProperty(0)
    mode = "not_set"  # shall be "day" or "night"
    hour = None
    puoli = False

    def say_day(self, *args):
        """Plays queued wav files to indicate the current day of the week"""

        if self.layout.ids.week.collide_point(*args[1].pos): #pylint:disable=star-args

            if self.config.get(self.mode, 'audio_enabled') == '0' or \
                self.audioplayer.playing is not None:
                return

            self.audioplayer.reset()
            self.audioplayer.queued_play("%s/audio/tanaan_on.wav" % RESOURCES)
            self.audioplayer.queued_play(
                "%s/audio/d%d.wav" %
                (RESOURCES, self.day))

    def say_time(self, *args):
        """Plays queued wav files to indicate time (nearest 30 minutes)"""

        if self.layout.ids.clock.collide_point(*args[1].pos): #pylint:disable=star-args

            if self.config.get(self.mode, 'audio_enabled') == '0' or \
               self.audioplayer.playing is not None:
                return

            self.audioplayer.reset()
            self.audioplayer.queued_play("%s/audio/kello_on.wav" % RESOURCES)
            if self.puoli:
                self.audioplayer.queued_play("%s/audio/puoli.wav" % RESOURCES)
            self.audioplayer.queued_play(
                "%s/audio/%d.wav" %
                (RESOURCES, self.hour))

            return True

    def set_mode(self, mode):
        """Sets the mode of the application to night or day"""

        self.mode = mode
        self.layout.ids.bg.source = "%s/background/%s" % (
            RESOURCES, self.config.get(mode, 'background'))
        self.layout.ids.moon.source = "%s/clock/%s" % (RESOURCES, "moon2.png")
        self.layout.ids.frame.source = "%s/clock/%sclock_bg.png" % (
            RESOURCES, mode)
        self.layout.ids.hour.source = "%s/clock/%sclock_hour_needle.png" % (
            RESOURCES, mode)
        self.layout.ids.minute.source = "%s/clock/%sclock_minute_needle.png" % (
            RESOURCES, mode)
        self.layout.ids.second.source = "%s/clock/%sclock_second_needle.png" % (
            RESOURCES, mode)
        self.update_layout()

    def update_layout(self):
        """Updates layout based on the current mode"""

        add_clock = remove_clock = add_moon = remove_moon = False

        clock_in_layout = self.layout.ids.clock.parent == self.layout
        if clock_in_layout == False and self.config.get(
                self.mode, 'clock_visible') == '1':
            add_clock = True
        elif clock_in_layout and self.config.get(
            self.mode, 'clock_visible') == '0':
            remove_clock = True

        moon_in_layout = self.layout.ids.moon.parent == self.layout
        if self.mode == "day" and moon_in_layout:
            remove_moon = True
        elif self.mode == "night":
            if moon_in_layout == False and self.config.get(
                    self.mode, 'moon_visible') == '1':
                add_moon = True
            elif moon_in_layout and self.config.get(
                self.mode, 'moon_visible') == '0':
                remove_moon = True

        if add_clock:
            self.layout.add_widget(self.layout.ids.clock)

        if remove_clock:
            self.layout.remove_widget(self.layout.ids.clock)

        if add_moon:
            self.layout.add_widget(self.layout.ids.moon)

        if remove_moon:
            self.layout.remove_widget(self.layout.ids.moon)

    def tick(self, _):
        """The application ticks once per second for updating clock
        needles and emitting snowflakes"""

        self.day = datetime.today().weekday()
        now = datetime.now()

        # set day or night mode
        now_time_string = "%d:%d" % (now.hour, now.minute)
        now_time = datetime.strptime(now_time_string, '%H:%M')
        start_time = datetime.strptime(
            self.config.get(
                'night', 'start_time'), '%H:%M')
        stop_time = datetime.strptime(
            self.config.get(
                'night', 'stop_time'), '%H:%M')
        if now_time >= stop_time and now_time <= start_time:
            if self.mode != "day":
                self.set_mode("day")
        else:
            if self.mode != "night":
                self.set_mode("night")

        # calculate angles of clock needles, with precise hour
        hour = now.hour
        if hour > 12:
            hour = hour - 12
        self.hours_needle_angle = 360 - (0.5 * (60 * hour + now.minute))
        self.minutes_needle_angle = 360 - (6 * now.minute)
        self.seconds_needle_angle = 360 - (6 * now.second)

        # set approx hour
        minute = now.minute
        puoli = False
        if minute > 15:
            hour = hour + 1
            if minute < 45:
                puoli = True
            if hour > 12:
                hour = hour - 12
        if hour == 0:
            hour = 12
        self.hour = hour
        self.puoli = puoli

        # emit a snowflake for each tick
        if self.snowflakes is None:
            self.snowflakes = Snowflakes()
            self.snowflakes.init(self.layout)
        self.snowflakes.emit()

    def build_settings(self, settings):
        """Called when creating settings. Implemented in clocksettings.py"""

        clocksettings.build_settings(settings, self.config, self.backgrounds)

    def on_config_change(self, config, section, key, value):
        """Called when settings have changed. Updates layout if needed"""

        if config is self.config:
            token = (section, key)
            if token == (self.mode, 'clock_visible'):
                self.update_layout()
            elif token == (self.mode, 'moon_visible'):
                self.update_layout()
            elif token == (self.mode, 'background'):
                self.layout.ids.bg.source = "%s/background/%s" % (
                    RESOURCES, self.config.get(self.mode, 'background'))
                self.update_layout()

    def build_config(self, config):
        """Called to create a config file. Implemented in clocksettings.py"""

        clocksettings.build_config(config)

    def update_backgrounds(self):
        """Populates background file list again from file system"""

        bgpath = "%s/background" % RESOURCES
        self.backgrounds = []
        for _, _, files in os.walk(bgpath):
            for bgfile in files:
                self.backgrounds.append(bgfile)
        self.backgrounds = sorted(self.backgrounds)

    def build(self):
        """Called in application start"""

        self.update_backgrounds()

        # initialize objects
        self.layout = ClockLayout()
        self.layout.ids.drag_area.app = self
        self.audioplayer = AudioPlayer()

        # start ticking
        Clock.schedule_interval(self.tick, 1 / 1.)
        return self.layout

if __name__ == '__main__':
    ClockApp().run()
