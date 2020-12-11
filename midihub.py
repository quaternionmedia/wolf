import rtmidi
from time import time, sleep
from collections import deque
from rtmidi.midiutil import open_midioutput, open_midiinput
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, POLY_AFTERTOUCH, CONTROL_CHANGE
from operator import xor

NUMBER_LOOPS = 32

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
launchpad_scenes = [89, 79, 69, 59, 49, 39, 29, 19]
launchpad_functions = [91, 92, 93, 94 , 95, 96, 97, 98]
launchpad_drums = [11, 12, 13, 14, 21, 22, 23, 24, 31, 32, 33, 34, 41, 42, 43, 44]
launchpad_fx = [15, 16, 17, 18, 25, 26, 27, 28, 35, 36, 37, 38, 45, 46, 47, 48]


class HoloController:
    def __init__(self):
        self.current_scene = None
        self.live = True
        self.shift = False
        self.toggleLive()
        self.clear()
        self.holo_loops = [None]*NUMBER_LOOPS
        self.holo_scenes = [None]*8
    def clear(self):
        for i in range(11, 89):
            launchOut.send_message([NOTE_ON, i, 0])
        for i in launchpad_scenes:
            launchOut.send_message([NOTE_ON, i, 0])
        for i in launchpad_functions:
            launchOut.send_message([NOTE_ON, i, 0])
        self.holo_loops = [None]*NUMBER_LOOPS
        self.holo_scenes = [None]*8
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
                        if self.holo_loops[l] == None:
                            # no existing loop - start recording
                            launchOut.send_message([NOTE_ON, message[1], RECORDING])
                            self.holo_loops[l] = 0
                        elif self.holo_loops[l] == 0:
                            # loop paused (or recording) - start playing
                            launchOut.send_message([NOTE_ON, message[1], GREEN[message[2] >> 4]])
                            self.holo_loops[l] = message[2]
                        else:
                            # loop playing - stop
                            launchOut.send_message([NOTE_ON, message[1], STOPPED])
                            self.holo_loops[l] = 0
                    else:
                        # shift mode
                        # erase loop
                        self.holo_loops[l] = None
                        launchOut.send_message([NOTE_ON, message[1], EMPTY])
                elif message[1] in launchpad_drums:
                    bitwigOut.send_message([NOTE_ON, 36 + launchpad_drums.index(message[1]), message[2]])
                    launchOut.send_message(message)
                elif message[1] in launchpad_fx:
                    pass
                else:
                    launchOut.send_message(message)
            else:
                # note off
                if message[1] in launchpad_drums:
                    bitwigOut.send_message([NOTE_ON, 36 + launchpad_drums.index(message[1]), message[2]])
                    launchOut.send_message(message)
        elif message[0] == CONTROL_CHANGE:
            print('control change', message)
            if message[1] in launchpad_scenes and message[2] == 127:
                # scene button pressed
                s = launchpad_scenes.index(message[1])
                if self.shift:
                    # erase scene
                    print('erasing scene', s)
                    self.holo_scenes[s] = None
                    launchOut.send_message([NOTE_ON, message[1], EMPTY])
                else:
                    # normal mode - no shift
                    if self.holo_scenes[s]:
                        # recall scene
                        print('recalling scene', s)
                        if self.current_scene != None:
                            # deactavate current scene - lights only
                            launchOut.send_message([NOTE_ON, launchpad_scenes[self.current_scene], STOPPED])
                        self.current_scene = s
                        launchOut.send_message([NOTE_ON, launchpad_scenes[self.current_scene], GREEN[-1]])
                        scene = self.holo_scenes[s]
                        print(self.holo_scenes[s])
                        for l in range(NUMBER_LOOPS):
                            if self.holo_loops[l] != None:
                                # loop exists
                                if scene[l] != self.holo_loops[l]:
                                    # loop needs to be changed
                                    print(f'changing loop {l} from {self.holo_loops[l]} to {scene[l]}')
                                    if scene[l] in (0, None):
                                        if self.holo_loops[l] > 0:
                                            # stop loop
                                            print('stop loop', l)
                                            holoOut.send_message([NOTE_ON, l, self.holo_loops[l]])
                                            self.holo_loops[l] = 0
                                    elif scene[l] != None and self.holo_loops[l] == 0:
                                        # start loop
                                        print('start loop', l)
                                        holoOut.send_message([NOTE_ON, l, scene[l]])
                                        self.holo_loops[l] = scene[l]
                                    else:
                                        # change volume on this loop
                                        # need to send message twice to fweelin
                                        print('changing volume of loop')
                                        holoOut.send_message([NOTE_ON, l, scene[l] or self.holo_loops[l]])
                                        sleep(.01)
                                        holoOut.send_message([NOTE_ON, l, scene[l] or self.holo_loops[l]])
                                        self.holo_loops[l] = scene[l]
                                launchOut.send_message([NOTE_ON, launchpad_notes[l], STOPPED if scene[l] in (0, None) else GREEN[scene[l] >> 4]])
                                
                        print('recalled scene')
                        print(self.holo_loops)
                    else:
                        # store scene
                        print('storing scene', s)
                        print(self.holo_loops)
                        if self.current_scene != None:
                            # deactavate current scene - lights only
                            launchOut.send_message([NOTE_ON, launchpad_scenes[self.current_scene], STOPPED])
                        self.current_scene = s

                        self.holo_scenes[s] = self.holo_loops.copy()
                        launchOut.send_message([NOTE_ON, message[1], GREEN[-1]])
                
            elif message[1] in launchpad_functions:
                if message[1] == 98:
                    # caputre midi button
                    # enable shift functionality
                    self.shift = False if message[2] == 0 else True
                    holoOut.send_message(message)
                if self.shift:
                    if message[1] == 95:
                        # erase + session = delete-pulse
                        print('deleting pulse')
                        holoOut.send_message([CONTROL_CHANGE, 108, 0])
                        self.clear()
                else:
                    # normal mode
                    pass


if __name__ == '__main__':
    midiin = rtmidi.MidiIn()
    midiout = rtmidi.MidiOut()
    try:
        holoOut, p = open_midioutput('FreeWheeling:FreeWheeling IN 1', client_name='holoOut')
        holoIn, p = open_midiinput('FreeWheeling:FreeWheeling OUT 1', client_name='holoIn')
        launchOut, p = open_midioutput('Launchpad X:Launchpad X MIDI 2', client_name='launchOut')
        launchIn, p = open_midiinput('Launchpad X:Launchpad X MIDI 2', client_name='launchIn')
        bitwigOut, p = open_midioutput('Virtual Raw MIDI 6-0', client_name='LaunchpadBitwig')
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
