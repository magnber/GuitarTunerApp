import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import pyqtSignal, QObject, QThread, Qt, QUrl
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from audio_analyser import AudioAnalyzer
from shared_queue import SharedQueue
import os

class QueueListener(QObject):
    data_received = pyqtSignal(object)

    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.running = True

    def pull_queue(self):
        while self.running:
            data = self.queue.get()
            if data is not None:
                self.data_received.emit(data)
            # Hack to give the UI time to update, and the analyser time to update the feed
            time.sleep(0.03)
    
class TunerUi(QMainWindow):


    def __init__(self, queue):
        super().__init__()
        self.setWindowTitle("Guitar Tuner")
        self.setGeometry(100, 100, 400, 200)
        self.player = QMediaPlayer()

        self.setup_ui()

        # Data listener setup
        self.listener = QueueListener(queue)
        self.listenerThread = QThread()
        self.listener.moveToThread(self.listenerThread)
        self.listenerThread.started.connect(self.listener.pull_queue)
        self.listener.data_received.connect(self.update_ui)
        self.listenerThread.start()

    def setup_ui(self):
         # widget and layout
        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)

        font = QFont("Arial", 24, QFont.Bold)
        color = QColor(255, 255, 255)  # White color
        palette = QPalette()
        palette.setColor(QPalette.WindowText, color)

        # Note label
        self.pitchLabel = QLabel("Closest Pitch: -", self)
        self.pitchLabel.setFont(font)
        self.pitchLabel.setPalette(palette)
        self.pitchLabel.setAlignment(Qt.AlignCenter)

        # Frequency label
        self.frequency = QLabel("Frequency: 0 Hz", self)
        self.frequency.setFont(font)
        self.frequency.setPalette(palette)
        self.frequency.setAlignment(Qt.AlignCenter)

        # Hint label
        self.hint = QLabel("", self)
        self.hint.setFont(font)
        self.hint.setPalette(palette)
        self.hint.setAlignment(Qt.AlignCenter)

        # Set background color 
        self.main_widget.setAutoFillBackground(True)
        bgPalette = self.main_widget.palette()
        bgPalette.setColor(QPalette.Background, QColor(40, 44, 52))
        self.main_widget.setPalette(bgPalette)
        
        # Replay Button
        self.replayButton = QPushButton('Replay Sound', self)
        self.replayButton.clicked.connect(self.replay_sound)

        layout.addWidget(self.pitchLabel)
        layout.addWidget(self.frequency)
        layout.addWidget(self.hint)
        layout.addWidget(self.replayButton)

    def update_ui(self, data):
        note, hint  = AudioAnalyzer.get_note_and_hint(data)

        # Update labels
        self.pitchLabel.setText(f"Closest Pitch: {note}")
        self.frequency.setText(f"Frequency: {data}")
        self.hint.setText(f"{hint}")
    
    def replay_sound(self):
        print("button clicked")
        # Method to handle playback
        file_path = os.path.abspath("./audio_files/A2.wav")
        url = QUrl.fromLocalFile(file_path)
        content = QMediaContent(url)
        self.player.setMedia(content)
        self.player.play()


    def closeEvent(self, event):
        self.listener.running = False
        self.listenerThread.quit()
        self.listenerThread.wait()
        super().closeEvent(event)

if __name__ == "__main__":
    queue = SharedQueue()
    app = QApplication(sys.argv)
    window = TunerUi(queue)
    window.show()

    analyzer = AudioAnalyzer(queue)
    analyzer.start()

    sys.exit(app.exec_())
