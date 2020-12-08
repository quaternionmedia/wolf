import rtmidi
from time import time, sleep

midiout = rtmidi.MidiOut()
midiin = rtmidi.MidiIn()

out_ports = midiout.get_ports()
in_ports = midiin.get_ports()

# if out_ports:
#     midiout.open_port(0)
# else:
midiout.open_virtual_port("hub")

if in_ports:
    midiin.open_port(2)
else:
    midiin.open_virtual_port("My virtual output")

# with midiin:

class MidiHandler:
    def __init__(self):
        # self.port = port
        self.startTime = time()
        self.wallclock = self.startTime
    def __call__(self, event, data=None):
        message, deltatime = event
        self.wallclock += deltatime
        print(self.wallclock, message)

midiin.set_callback(MidiHandler())
try:
    while True:
        sleep(.01)
except KeyboardInterrupt:
    print('')
finally:
    print("Exit.")
    midiin.close_port()
    del midiin