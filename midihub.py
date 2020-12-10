import rtmidi
from time import time, sleep
from collections import deque
from rtmidi.midiutil import open_midioutput, open_midiinput
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, POLY_AFTERTOUCH, CONTROL_CHANGE

EMPTY = 0 # black
RECORDING = 5 # red
PLAYING = 21 # green
STOPPED = 43 # navy
SCENE = 53 #ED63FA
SCENE_EMPTY = 55 #77567A
GREEN = [ 123, 23, 64, 22, 76, 87, 21, 122 ]


launchpad_notes = []
n = 81
for y in range(4):
    for x in range(8):
        launchpad_notes.append(n + x)
    n -= 10
print('loop map:')
print(launchpad_notes)

holo_loops = [None]*32
# self.map = deque([])
holo_scenes = [None]*8

class HoloController:
    def __init__(self):
        # self.map = deque([])
        self.live = True
        self.shift = False
        self.toggleLive()
        # self.clear()
    def clear(self):
        for i in range(11, 89):
            launchOut.send_message([NOTE_ON, i, 0])
        holo_loops = [None]*32
    def toggleLive(self):
        # switch to / from programming / Live mode
        launchOut.send_message([240, 0, 32, 41, 2, 12, 14, 1 if self.live else 0, 247])
        self.live = not self.live
    def __call__(self, event, data=None):
        message, deltatime = event
        if message[0] == NOTE_ON:
            if message[2] > 0:
                print('note on', message)
                if message[1] in launchpad_notes:
                    l = launchpad_notes.index(message[1])
                    holoOut.send_message([NOTE_ON, l, message[2]])
                    if not self.shift:
                        if holo_loops[l] == None:
                            # no existing loop - start recording
                            launchOut.send_message([NOTE_ON, message[1], RECORDING])
                            holo_loops[l] = 0
                        elif holo_loops[l] == 0:
                            # loop paused (or recording) - start playing
                            launchOut.send_message([NOTE_ON, message[1], GREEN[message[2] >> 4]])
                            holo_loops[l] = message[2]
                        else:
                            # loop playing - stop
                            launchOut.send_message([NOTE_ON, message[1], STOPPED])
                            holo_loops[l] = 0
                    else:
                        # shift mode
                        # erase loop
                        holo_loops[l] = 0
                        launchOut.send_message([NOTE_ON, message[1], EMPTY])
                else:
                    launchOut.send_message(message)
            else:
                # note off
                pass
        elif message[0] == CONTROL_CHANGE:
            print('control change', message)
            if message[1] == 89:
                # scene 1
                self.clear()
                holoOut.send_message()
            elif message[1] == 98:
                # caputre midi button
                self.shift = False if message[2] == 0 else True
                holoOut.send_message(message)
            launchOut.send_message(message)


if __name__ == '__main__':
    midiin = rtmidi.MidiIn()
    midiout = rtmidi.MidiOut()
    try:
        holoOut, p = open_midioutput('FreeWheeling:FreeWheeling IN 1', client_name='holoOut')
        holoIn, p = open_midiinput('FreeWheeling:FreeWheeling OUT 1', client_name='holoIn')
        launchOut, p = open_midioutput('Launchpad X:Launchpad X MIDI 2', client_name='launchOut')
        launchIn, p = open_midiinput('Launchpad X:Launchpad X MIDI 2', client_name='launchIn')
    except Exception as e:
        print('error opening ports')
        print(e)

    out_ports = midiout.get_ports()
    print('out ports:')
    print(out_ports)
    in_ports = midiin.get_ports()
    print('in ports:')
    print(in_ports)

    launchIn.set_callback(HoloController())
    # launchIn.set_error_callback(print)
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print('')
    finally:
        print("hub out!")
        midiin.close_port()
        del midiin
