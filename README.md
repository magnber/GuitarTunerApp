# YOUR PROJECT TITLE

#### Video Demo: <URL HERE>

#### Description:

This is a guitar tuner app that features a manual and autiatic mode for tuning a guitar in to a standard pitch of E2, A2, D3, G3, B3, and E4.

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

This app captures audio from the computer's default microphone, processes it and tries to match the found frequency with the cloeses frequency of a default tuned guitar string, before providing the user with instructions on how to get the string in tune.

### Files and modules

**audio_analyser.py**

Class that handles everything releated to capturing and processing the audio.
The processing is defined under the header **Audio Processing** bellow.
The class inherrits from Thread to separate the processing of the audio from the output queue and rendering client.

**shared_queue.py**

Thread safe queue that handles the transfer of the processed data from the AudioAnalyser class to the client. This is needed to handle concurrency.

**recorder.py**

Class with methodes to record and play back audiofiles.

**app.py**

Contains a simple PyQt5 client UI that renders the feedback to the user. The programs three main parts are orchestrated from this file.

The ui consists of three main parts; AppSetup, QueueListener and TunerUi.

Breakdown:

- AppsSetup holds and instance of of the SharedQueue and AudioAnalyzer to separate the instanciation and handling of running processes from the rendering of ui.
- QueueListener listens for new events on the queue and emits these to a data_receiver
- TunerUi handlest the rendering of the ui. The class sets up the ui components and connects the listener to the queue, and listeners data_receiver method to the update_ui method before starting the listenerThread.
- The QueueListener loops while the program is running, looking for new events in the queue (SharedQueue)

**Audio Processing**

While recording, the audio is processed in chunks. Processing is done to filter out noise and to smoothen the input, making the output of the transformation easier to read. Figuring out how to process the audio inpout and what methodes to apply was the most timeconsuming part of this project. At the time of writing, the best results have been achieved by implementing these steps:

1. Using a gliding buffer that shifts the data to the left and replaces the oldest chunk. Simply processing the data in realtime proved challenging because, as the program grew in complexity, the streams IO overflow loss became to high resulting in data loss and slow output. Accepting some loss and adding the buffer solved this issue.

2. Apply a Hanning window to the whole buffer, tapering the edges to zero. Applying a Hanning Window reduces the problem with spectral leakage during the fourier transform.

3. Apply a zero padding at the end of each buffer to further separate one chunk from another.

4. Perform a FFT (Fast Fourier Transform). A Fourier transformation transforms audio signals to spectral components. Or in other words transforms amplitune over time, to power over hertz.

5. Use only absolute values. The FFT produces both real and imaginary numbers. In a frequency distribution we only care about the real (absolute) values, measured in Hz. Imaginary numbers does not give any additional information in this context.

6. Apply a Harmonic Product Spectrum to reduce the harmonics detected in the FFT. A hps is a technique used to identify the fundamental frequency of a sound by exploiting the harmonic structure of the sound. Harmonics are integer multiples of the fundamental pitch, because of this we can reduce the number of harmonics by downsizing the samles and multiplying the sample by itself, resulting in a fewer samples with more predominant pitches. The highest pitch (most powerful) is ultimately the one we are after.

7. Remove all frequencies below 60 to further reduce the noice of the output.

The audio_analyser file contains the code that performs the audio processing, supplemented by a thread shared queue that is used to distribute the results to the client.

**Userfeedback**

The audioanalyser does most of the lifting, the client simply needs to refresh and update the ui based on the data it receives.
The output provides the estimated frequency of the note that is being played, the closest note and a hint indicating if the user should thighten or losen the string. When the string is tune "in tune" is displayed.

**Retrospective**
The method for creating this project has been iterative with trial and error. Besides some basic knowledge of how to play a guitar and what the strings was called I previously had little knowledge about music theroy or the physics behind a fourier transformation. The implementation reached now is the result of trying to apply multiple different methodes of processing the audio input, before, during and after the Fourier transform, until finally reaching this that can be used as a guitar tuner.

The initial idea was to create a chord recognizer that could run in in the browser. From this starting point the initial stack was setup with a Flask back-end, some JavaScript and HTML to render the client in a browser. Creating the functionality to recongize a chord proved to be more timeconsuming than initially estimated, so much so that I decieded to setteled for a tuner.
To send the data from the client to the server i used a websocket, but found that the dataloss and lag was to big to create a working app. I therefor settled on a local app, resulting in what the project is at the time of writing this.
