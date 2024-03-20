# YOUR PROJECT TITLE

#### Video Demo: <URL HERE>

#### Description:

This is a guitar tuner app. The app currently only features standard tuning for E2, A2, D3, G3, B3, E4.

### Running the app

Optional: Set up a virtual environment

**Installation**

Python3 is required

`pip3 install -r requirements.txt`

**Starting the app**
To run the app, open a terminal and stay at the root of the project, then type:
`python3 app.py`

**Testing**
The app can also be run in the terminal by running (from root):
`python3 audio_processor/audio_analyser.py`

## About the app

This app captures audio from the computer's default microphone, processes it and tries to find the cloeses frequency of a default tuned guitar.

**Audio Recording**
A recording is started and maintained by AudioAnalyser, in the audio_analyser.py file.

**Audio Processing**
While recording, the audio is processed in chunks. Processing is done to filter out noise and to smoothen the input, making the output of the transformation easier to read. Figouring out how to process the audio inpout and what methodes to apply was the most timeconsuming part of this project. At the time of writing, the best results have been achieved by implementing these steps:

1. Using a gliding buffer that shifts the data to the left and replaces the oldest chunk

2. Apply a Hanning window to the whole buffer, tapering the edges to 0

3. Apply a 0 padding at the end of each buffer to further separate one chunk from another

4. Perform a Fourier transform and use the absolute values. A Fourier transformation returns both real and imaginary numbers, for the sake of a frequency distribution we only care about the real (absolute) values

5. Apply a Harmonic Product Spectrum to reduce the harmonics into one pitch
6. Remove all frequencies below 60 to further reduce noise

The audio_analyser file contains the code that performs the audio processing, supplemented by a thread shared queue that is used to distribute the results to the client.

**Userfeedback**
The audioanalyser does most of the lifting, the client simply needs to refresh and update the ui based on the data it receives.
The output provides the estimated frequency of the note that is being played, the closest note and a hint indicating if the user should thighten or losen the string. When the string is tune "in tune" is displayed.

**Files and Modules**
The audio_processor folder contains the modules for the back-end.

### audio_analyser.py

class that handles everything releated to capturing and processing the sound.
The class contains both static and instance methodes, providing and interface to controlling the processing of an audiostream. The class inherrits from Thread, and can therefor be started by calling instance.start, starting a new thread for the instance of the class.

### shared_queue.py

Custom thread safe queue that handles the transfer of the processed data from the audio_analyser class to the client.

### app.py

Contains a simple PyQt5 client UI that renders the feedback to the user. The programs three main parts are orchestrated from this file.

Breakdown:

- The QueueListener loops while the program is running, looking for new events in the queue (SharedQueue)
- The TunerUi sets up the UI components and the hooks connects the listener to the queue, and listeners data_receiver method to the update_ui method and starts the listenerThread.
- The above points makes it so that the back-end can run independently of the client, and the client only needs to listen for new event on the queue.
- To start the program we only need to start the analyser and pass the information on to the queue.

**Footnotes**
The method for creating this project has been iterative with trial and error. Besides some basic knowledge of how to play a guitar and what the strings was called I previously had little knowledge about music theroy. The implementation I know deliver is the result of trying to apply multiple different methodes of processing the audio input, before, during and after the Fourier transform.

I've leverage "the internet", read articles, watched YouTube videos, used AI, and looked at similar solutions in other repositories, to reach a final program that worked.
