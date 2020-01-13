#!/usr/bin/env python3
import alsaaudio
import numpy as np
import aubio
import matplotlib.pyplot as plt
import rtmidi
from rtmidi.midiconstants import (ALL_SOUND_OFF, CONTROL_CHANGE)

# constants
samplerate = 44100
win_s = 2048
hop_s = win_s // 2
framesize = hop_s
VOL_OFFSET = .8

# find input
pcms = alsaaudio.pcms(alsaaudio.PCM_CAPTURE)
print(pcms)

# set up audio input
recorder = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, device='pulse')
recorder.setperiodsize(framesize)
recorder.setrate(samplerate)
recorder.setformat(alsaaudio.PCM_FORMAT_FLOAT_LE)
recorder.setchannels(1)

# create aubio pitch detection (first argument is method, "default" is
# "yinfft", can also be "yin", "mcomb", fcomb", "schmitt").
pitcher = aubio.pitch("default", win_s, hop_s, samplerate)
# set output unit (can be 'midi', 'cent', 'Hz', ...)
# pitcher.set_unit("Hz")
# ignore frames under this level (dB)
pitcher.set_silence(-20)

# midi
midiout = rtmidi.MidiOut()
midiout.open_virtual_port(__name__)
last_midi = 0
active_midis = set()

print("Starting to listen, press Ctrl+C to stop")

# main loop
while True:
    try:
        # read data from audio input
        _, data = recorder.read()
        # convert data to aubio float samples
        samples = np.fromstring(data, dtype=aubio.float_type)
        #plt.plot(samples)
        #plt.show()
        if len(samples):
            # pitch of current frame
            freq = pitcher(samples)[0]
            try:
                note = aubio.freq2note(freq)
                midi = aubio.note2midi(note)
                volume = np.sum(samples**2)/len(samples)
                vel = (volume - VOL_OFFSET) / (1 - VOL_OFFSET) * 112
                if volume > VOL_OFFSET:
                    print("{:3} {}".format(note, volume))
                    if last_midi != midi:
                        midiout.send_message([0x90, midi, vel])  # note on
                        print("midi: " + str(midi))
                    last_midi = midi
                elif volume < .6:
                    midiout.send_message([CONTROL_CHANGE, ALL_SOUND_OFF, 0])
                    last_midi = 0
            except ValueError:
                print("warn: ValueError")
    except KeyboardInterrupt:
        print("Ctrl+C pressed, exiting")
        break

del midiout

