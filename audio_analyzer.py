from pyaudio import PyAudio, paInt16
from threading import Thread
import numpy as np
import sys


class AudioAnalyzer(Thread):
    """ This AudioAnalyzer reads the microphone and finds the frequency of the loudest tone.
         Used tohether with the SharedQueue to share the output with a app thread.

        while True:
            freq = queue.get()
            print("loudest frequency:", q_data, "nearest note:", a.frequency_to_note_name(q_data, 440))
            time.sleep(0.02) """

    SAMPLING_RATE = 48000
    CHANNELS = 1
    CHUNK_SIZE = 1024  # number of samples
    BUFFER_TIMES = 50  # number of chnuks in buffer 
    PADDING = 3  # times the buffer length

    
    NOTES = {
    "E2": 82,
    "A2": 110,
    "D3": 147,
    "G3": 196,
    "B3": 247,
    "E4": 330
    }

    def __init__(self, queue, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)

        self.queue = queue  # queue should be instance of SharedQueue
        self.buffer = np.zeros(self.CHUNK_SIZE * self.BUFFER_TIMES)
        self.hanning_window = np.hanning(len(self.buffer))
        self.running = False

        try:
            self.audio_object = PyAudio()
            self.stream = self.audio_object.open(format=paInt16,
                                                 channels=self.CHANNELS,
                                                 rate=self.SAMPLING_RATE,
                                                 input=True,
                                                 output=False,
                                                 frames_per_buffer=self.CHUNK_SIZE)
        except Exception as e:
            sys.stderr.write('Error: Line {} {} {}\n'.format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e))
            return

    @staticmethod
    def get_note(frequency):
        """ Find the minimum absolute value of the difference between each note and the frequency"""
        notes = AudioAnalyzer.NOTES
        return min(notes.keys(), key=lambda note: abs(notes[note] - frequency))

    @staticmethod
    def get_hint(note, freq):
        """ Get a tighten or loosen hint"""
        notes = AudioAnalyzer.NOTES
        note_freq = notes[note]
    
        diff = note_freq - freq 

        if abs(diff) < 1:
            return "🤌 In tune 🤌"

        hint = ""
        if diff < 0 :
           hint = "👇 Losen string 👇"
        elif diff > 0:
            hint = "👆 Tighten string 👆"
        else:
            hint = "🤌 In tune 🤌"

        return hint

    @staticmethod
    def get_note_and_hint(freq):
        note = AudioAnalyzer.get_note(freq)
        hint = AudioAnalyzer.get_hint(note, freq)
        return note,hint
 
    def run(self):
        """ 
        Main function where the microphone buffer gets read and proccessed.
        Output is placed on an instance of "shared_queue".
        """

        self.running = True

        while self.running:
            try:
                # read microphone data
                data = self.stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                data = np.frombuffer(data, dtype=np.int16)

                # Roll data in buffer to the left 
                self.buffer[:-self.CHUNK_SIZE] = self.buffer[self.CHUNK_SIZE:]
                # append from the stream
                self.buffer[-self.CHUNK_SIZE:] = data

                # apply a hanning windown to smoothen the curve. This esensially taters the curve to 0 at each end.
                hanning_window_buffer = self.buffer * self.hanning_window

                ## apply padding at the end of the buffer for a smoother transition between buffer chunks
                padding = np.pad(hanning_window_buffer, (0, len(self.buffer) * self.PADDING),"constant")
                
                # apply a Fast Fourier transform to extract frequencies 
                fft = np.fft.fft(padding)
                
                # Use the absolute values - in audio perspective we only consider real numbers
                fft_magnitude = abs(fft)

                # only use the first half of the fft output data because Nyquist Theorem
                fft_magnitude = fft_magnitude[:int(len(fft_magnitude) / 2)]

                # apply a HPS (Harmonic Product Spectrum) to collaps hamonics frequencies into one pitch
                magnitude_data_orig = np.copy(fft_magnitude)
                for downsample_factor in range(2, 4):
                    hps_len = int(np.ceil(len(fft_magnitude) / downsample_factor))
                     # multiply every downsample_factor'th element - 2 and 3 in this case
                    downsampled = magnitude_data_orig[::downsample_factor]
                    if len(downsampled) < hps_len:
                            # Pad it with zeros to match potentially lower ceiling length
                            downsampled = np.pad(downsampled, (0, hps_len - len(downsampled)), 'constant')
                    fft_magnitude[:hps_len] *= downsampled

                # get the corresponding frequency array
                frequencies = np.fft.fftfreq(int((len(fft_magnitude) * 2) / 1),
                                             1. / self.SAMPLING_RATE)

                # set magnitude of all frequencies below 60Hz to zero to further reduce the noise in the final output
                for i, freq in enumerate(frequencies):
                    if freq > 60:
                        fft_magnitude[:i - 1] = 0
                        break

                # put the frequency of the loudest tone into the queue
                self.queue.put(round(frequencies[np.argmax(fft_magnitude)], 2))

            except Exception as e:
                sys.stderr.write('Error: Line {} {} {}\n'.format(sys.exc_info()[-1].tb_lineno, type(e).__name__, e))

        self.stream.stop_stream()
        self.stream.close()
        self.audio_object.terminate()


    def stop(self):
        """Stop the audio analysis and close resources."""
        self.running = False

if __name__ == "__main__":
    # Only for testing:
    from shared_queue import SharedQueue
    import time

    q = SharedQueue()
    a = AudioAnalyzer(q)
    a.start()
    try:
        while True:
            q_data = q.get()
            if q_data is not None:
                print( f"freq : {q_data}, note/hint:{a.get_note_and_hint(q_data)}")
                time.sleep(0.02)
    except KeyboardInterrupt:
        a.stop()
        a.join()
