#!/usr/bin/env python
"""This script defines AudioPlayer class for Ensikello application"""

from kivy.core.audio import SoundLoader


class AudioPlayer(SoundLoader):
    """Implements a simple queued wav audio player"""

    queue = []
    playing = None

    def play_queue(self, *_):
        """Plays the first filename in the queue and calls itself
        recursively when done."""

        if len(self.queue) > 0:
            filename = self.queue.pop(0)
            if filename:
                print "playing from queue: %s" % filename
                sound = SoundLoader.load(filename)
                if sound:
                    sound.bind(on_stop=self.play_queue)
                    sound.play()
                    self.playing = sound
        else:
            self.playing = None

    def reset(self):
        """Clears the queue and stops playing"""

        if self.playing is not None:
            print "reset"
            self.queue = []
            self.playing.stop()
            self.playing = None

    def queued_play(self, filename):
        """Appends filename into queue and starts playing if needed"""

        self.queue.append(filename)
        if self.playing is None:
            self.play_queue()

    @staticmethod
    def play(filename):
        """Plays a file directly without queuing"""

        print "playing: %s" % filename
        sound = SoundLoader.load(filename)
        sound.play()

    def __init__(self):
        """Sets class variables to initial state"""

        self.queue = []
        self.playing = None
