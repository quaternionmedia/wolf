import rtmidi
from time import time, sleep
from collections import deque
from rtmidi.midiutil import open_midioutput, open_midiinput
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, POLY_AFTERTOUCH, CONTROL_CHANGE

EMPTY = 0 # black
RECORDING = 5 # red
PLAYING = 21 # green
STOPPED = 1 # grey
SCENE = 53 #ED63FA
SCENE_EMPTY = 55 #77567A


midiin = rtmidi.MidiIn()
midiout = rtmidi.MidiOut()
holoOut, p = open_midioutput('FreeWheeling:FreeWheeling IN 1', client_name='holoOut')
holoIn, p = open_midiinput('FreeWheeling:FreeWheeling OUT 1', client_name='holoIn')
launchOut, p = open_midioutput('Launchpad X:Launchpad X MIDI 2', client_name='launchOut')
launchIn, p = open_midiinput('Launchpad X:Launchpad X MIDI 2', client_name='launchIn')

out_ports = midiout.get_ports()
print('out ports:')
print(out_ports)
in_ports = midiin.get_ports()
print('in ports:')
print(in_ports)

launchpad_loops = {}
n = 81
i = 0
for y in range(4):
    for x in range(8):
        launchpad_loops[n + x] = i
        i += 1
    n -= 10
print('loop map:')
print(launchpad_loops)

class MidiHandler:
    def __init__(self):
        # self.port = port
        self.startTime = time()
        self.wallclock = self.startTime
    def __call__(self, event, data=None):
        message, deltatime = event
        self.wallclock += deltatime
        print(self.wallclock, message)

class HoloController:
    def __init__(self):
        self.loops = [None]*32
        # self.map = deque([])
        self.scenes = [None]*8
        pass
    def __call__(self, event, data=None):
        message, deltatime = event
        if message[0] == NOTE_ON:
            if message[2] > 0:
                print('note on', message)
                if message[1] in launchpad_loops:
                    l = launchpad_loops[message[1]]
                    holoOut.send_message([NOTE_ON, l, message[2]])
                    if self.loops[l] == None:
                        # no existing loop - start recording
                        launchOut.send_message([NOTE_ON, message[1], RECORDING])
                        self.loops[l] = 0
                    elif self.loops[l] == 0:
                        # loop paused (or recording) - start playing
                        launchOut.send_message([NOTE_ON, message[1], PLAYING])
                        self.loops[l] = message[2]
                    else:
                        # loop playing - stop
                        launchOut.send_message([NOTE_ON, message[1], STOPPED])
                        self.loops[l] = 0
                else:
                    launchOut.send_message(message)
            else:
                # note off
                pass
        elif message[0] == CONTROL_CHANGE:
            print('control change', message)
            launchOut.send_message(message)
launchIn.set_callback(HoloController())

try:
    while True:
        sleep(1)
except KeyboardInterrupt:
    print('')
finally:
    print("hub out!")
    midiin.close_port()
    del midiin