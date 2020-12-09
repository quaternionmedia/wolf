import rtmidi
from time import time, sleep
from collections import deque
from rtmidi.midiutil import open_midioutput, open_midiinput

midiin = rtmidi.MidiIn()
midiout = rtmidi.MidiOut()
holoOut, p = open_midioutput('FreeWheeling:FreeWheeling IN 1 129:0', client_name='holoOut')
holoIn, p = open_midiinput('FreeWheeling:FreeWheeling OUT 1 129:1', client_name='holoIn')
launchOut, p = open_midioutput('Launchpad X:Launchpad X MIDI 2 16:1', client_name='launchOut')
launchIn, p = open_midiinput('Launchpad X:Launchpad X MIDI 2 16:1', client_name='launchIn')

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
        self.loops = deque([], 32)
        self.map = deque([])
        self.scenes = deque([], 8)
        pass
    def __call__(self, event, data=None):
        message, deltatime = event
        print('note on', message)
        if message[0] == 144:
            if message[1] > 0:
                launchOut.send_message(message)
            else:
                # note off
                pass
launchIn.set_callback(HoloController())

try:
    while True:
        sleep(.01)
except KeyboardInterrupt:
    print('')
finally:
    print("hub out!")
    midiin.close_port()
    del midiin