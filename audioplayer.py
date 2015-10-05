from kivy.core.audio import SoundLoader

class AudioPlayer(SoundLoader):
    queue = []
    playing = None

    def play_queue(self, *args):
        if len(self.queue) > 0:
            filename = self.queue.pop(0)
            if filename:
                print "playing from queue: %s"%filename
                sound = SoundLoader.load(filename)
                if sound:
                    sound.bind(on_stop=self.play_queue)
                    sound.play()
                    self.playing = sound
        else:
            self.playing = None

    def reset(self):
        if self.playing != None:
            print "reset"
            self.queue = []
            self.playing.stop()
            self.playing = None

    def queued_play(self, filename):
        self.queue.append(filename)
        if self.playing == None:
            self.play_queue()

    def play(self, filename):
        print "playing: %s"%filename
        sound = SoundLoader.load(filename)
        sound.play()
