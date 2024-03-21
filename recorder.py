import sounddevice as sd
import numpy as np

class AudioHandler:
    def __init__(self, sample_rate=48000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.audio_data = None

    def record_audio(self, duration=5):
        """
        Record audio from the default microphone/input device for a given duration.

        :param duration: Duration of the recording in seconds.
        """
        print("Recording...")
        self.audio_data = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, channels=self.channels, dtype='float64')
        sd.wait()  # Wait until recording is finished
        print("Recording done.")

    def play_audio(self):
        """
        Play back the recorded audio data through the default output device.
        """
        if self.audio_data is not None:
            sd.play(self.audio_data, samplerate=self.sample_rate)
            sd.wait()  # Wait until playback is finished
    


if __name__ == "__main__":
    # for testing purposes
    audio_handler = AudioHandler()

    audio_handler.record_audio(duration=5)
    audio_handler.play_audio()
