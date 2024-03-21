import sys
import time
from PyQt5.QtWidgets import QStackedWidget, QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject, QThread, Qt, QUrl
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from audio_analyzer import AudioAnalyzer
from shared_queue import SharedQueue
import os

class AppSetup():
    def __init__(self):
        self.queue = SharedQueue()
        self.analyzer = AudioAnalyzer(self.queue)
        self.analyzer_running = False

    def start_analyzer(self):
        if not self.analyzer_running:
            self.analyzer.start()
            self.analyzer_running = True

    def stop_analyzer(self):
        if self.analyzer_running:
            self.analyzer.stop()  # Make sure the stop method properly cleans up the thread
            self.analyzer.join()  # Wait for the thread to finish
            self.analyzer_running = False


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
            # Hack to give the UI time to update, and the analyzer time to update the feed
            time.sleep(0.03)
    
class TunerUi(QMainWindow):
    def __init__(self, app_setup):
        super().__init__()
        self.setWindowTitle("Guitar Tuner")
        self.setGeometry(100, 100, 400, 200)
        self.player = QMediaPlayer()
        
        
        self.mode = "manual"  # Starting mode
        self.app_setup = app_setup
        self.setup_ui_layout_defaults()
        self.main_widget = QWidget(self)  # Central widget
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)  # Main layout

        self.create_toggle_button()
        self.main_layout.addWidget(self.toggleModeButton, alignment=Qt.AlignCenter)  # Center the toggle button

        self.stack = QStackedWidget(self)
        self.manual_widget = QWidget()  # Page for manual mode
        self.automatic_widget = QWidget()  # Page for automatic mode

        self.setup_manual_ui()
        self.setup_automatic_ui()

        self.stack.addWidget(self.manual_widget)
        self.stack.addWidget(self.automatic_widget)

        self.main_layout.addWidget(self.stack)  
       

        self.listener = QueueListener(app_setup.queue)
        # Data listener setup
        self.listenerThread = QThread()
        self.listener.moveToThread(self.listenerThread)
        self.listenerThread.started.connect(self.listener.pull_queue)
        self.listener.data_received.connect(self.update_ui)
        self.listenerThread.start() 

    def create_toggle_button(self):
        # This method creates the toggle button and connects it to the toggle_mode slot
        self.toggleModeButton = QPushButton('Switch to Automatic', self)
        self.toggleModeButton.clicked.connect(self.toggle_mode)

    def setup_ui_layout_defaults(self):
        self.font = QFont("Arial", 24, QFont.Bold)
        self.color = QColor(255, 255, 255)  # White color
        self.palette = QPalette()
        self.palette.setColor(QPalette.WindowText, self.color)
        
    def setup_automatic_ui(self):
        layout = QVBoxLayout(self.automatic_widget)
        # Note label
        self.pitchLabel = QLabel("Closest Pitch: -", self)
        self.pitchLabel.setFont(self.font)
        self.pitchLabel.setPalette(self.palette)
        self.pitchLabel.setAlignment(Qt.AlignCenter)

        # Frequency label
        self.frequency = QLabel("Frequency: 0 Hz", self)
        self.frequency.setFont(self.font)
        self.frequency.setPalette(self.palette)
        self.frequency.setAlignment(Qt.AlignCenter)

        # Hint label
        self.hint = QLabel("", self)
        self.hint.setFont(self.font)
        self.hint.setPalette(self.palette)
        self.hint.setAlignment(Qt.AlignCenter)

        
        layout.addWidget(self.pitchLabel)
        layout.addWidget(self.frequency)
        layout.addWidget(self.hint)

    def setup_manual_ui(self):

        layout = QVBoxLayout(self.manual_widget)
        self.string_buttons = {
            'E2': './audio_files/E2.wav',
            'A2': './audio_files/A2.wav',
            'D3': './audio_files/D3.wav',
            'G3': './audio_files/G3.wav',
            'B3': './audio_files/B3.wav',
            'E4': './audio_files/E4.wav'
        }

        for string_note, file_path in self.string_buttons.items():
            btn = QPushButton(string_note, self)
            btn.clicked.connect(lambda _, path=file_path: self.replay_sound(path))
            layout.addWidget(btn)

    def update_ui(self, data):
        note, hint  = AudioAnalyzer.get_note_and_hint(data)

        # Update labels
        self.pitchLabel.setText(f"Closest Pitch: {note}")
        self.frequency.setText(f"Frequency: {data}")
        self.hint.setText(f"{hint}")

    def enable_auto_features(self):
        self.app_setup.start_analyzer()
        
    def disable_auto_features(self):
        self.app_setup.stop_analyzer()

    def toggle_mode(self):
        if self.mode == "automatic":
            self.mode = "manual"
            self.stack.setCurrentWidget(self.manual_widget)
            self.toggleModeButton.setText('Switch to Automatic')
            self.disable_auto_features()
        else:
            self.mode = "automatic"
            self.stack.setCurrentWidget(self.automatic_widget)
            self.toggleModeButton.setText('Switch to Manual')
            self.enable_auto_features()

    
    def replay_sound(self,path):
        # Method to handle playback
        file_path = os.path.abspath(path)
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
    app_setup = AppSetup()
    app = QApplication(sys.argv)
    window = TunerUi(app_setup)
    window.show()

    sys.exit(app.exec_())
