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
CUT = 13 # cut mode - yellow
GREEN = [ 123, 23, 64, 22, 76, 87, 21, 122 ]
DRUM_BANKS = [69, 79, 35, 19, 83]

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
launchpad_fx = [25, 26, 27, 28, 35, 36, 37, 38, 45, 46, 47, 48]
launchpad_mutes = [15, 16, 17, 18]

class HoloController:
    def __init__(self):
        self.current_scene = None
        self.live = True
        self.shift = False
        self.holo_loops = [None]*NUMBER_LOOPS
        self.holo_scenes = [None]*8
        self.mutes = [False]*4
        self.drum_bank = 0
        self.overdub = False
        self.cut = False
        self.toggleLive()
        self.clear()
    def clear(self):
        for i in range(11, 89):
            launchOut.send_message([NOTE_ON, i, 0])
        for i in launchpad_scenes:
            launchOut.send_message([CONTROL_CHANGE, i, 0])
        for i in launchpad_functions[:-3]:
            launchOut.send_message([CONTROL_CHANGE, i, 0])
        self.holo_loops = [None]*NUMBER_LOOPS
        self.holo_scenes = [None]*8
        for i in range(len(launchpad_mutes)):
            launchOut.send_message([NOTE_ON, launchpad_mutes[i], EMPTY if self.mutes[i] else RECORDING])
        for i in launchpad_drums:
            launchOut.send_message([NOTE_ON, i, DRUM_BANKS[self.drum_bank]])
        launchOut.send_message([CONTROL_CHANGE, 99, 69])
    def toggleLive(self):
        # switch to / from programming / Live mode
        launchOut.send_message([240, 0, 32, 41, 2, 12, 14, 1 if self.live else 0, 247])
        self.live = not self.live
    def toggleOverdub(self):
        self.overdub = not self.overdub
        holoOut.send_message([CONTROL_CHANGE, 97, 127 if self.overdub else 0])
        launchOut.send_message([CONTROL_CHANGE, 97, RECORDING if self.overdub else EMPTY])
        # print('overdub mode', self.overdub)
    def toggleCut(self):
        self.cut =  not self.cut
        holoOut.send_message([CONTROL_CHANGE, 96, 127 if self.overdub else 0])
        launchOut.send_message([CONTROL_CHANGE, 96, CUT if self.cut else EMPTY])
        # print('overdub mode', self.cut)
    def exit(self):
        self.toggleLive()
    def __call__(self, event, data=None):
        message, deltatime = event
        # print(data, message)
        if message[0] == NOTE_ON and data == 0:
            if message[2] > 0:
                # print('note on', message)
                if message[1] in launchpad_notes:
                    l = launchpad_notes.index(message[1])
                    holoOut.send_message([NOTE_ON, l, message[2]])
                    if not self.shift:
                        if self.cut:
                            
                            if self.holo_loops[l] in (0, None):
                                # FreeWheeling doesn't start loops in cut mode if they are paused, recording, or don't exist. This is a fix for that.
                                holoOut.send_message([CONTROL_CHANGE, 118, 0])
                                holoOut.send_message([NOTE_ON, l, message[2]])
                                holoOut.send_message([CONTROL_CHANGE, 118, 127])
                            if self.holo_loops[l] == None:
                                # in this case, we should be recording
                                launchOut.send_message([NOTE_ON | 0x2, message[1], RECORDING])
                                self.holo_loops[l] = 0
                                
                            else:
                                # we should be playing
                                launchOut.send_message([NOTE_ON | 0x2, message[1], GREEN[message[2] >> 4]])
                                self.holo_loops[l] = message[2]
                            
                        else:
                            if self.holo_loops[l] == None:
                                # no existing loop - start recording
                                # red - pulsing
                                launchOut.send_message([NOTE_ON | 0x2, message[1], RECORDING])
                                self.holo_loops[l] = 0
                            elif self.holo_loops[l] == -1:
                                # loop currently overdubbing
                                # play at proper volume
                                launchOut.send_message([NOTE_ON | 0x2, message[1], GREEN[message[2] >> 4]])
                                self.holo_loops[l] = message[2]
                            elif self.holo_loops[l] == 0:
                                # loop paused (or recording)
                                if self.overdub:
                                    # start overdubbing
                                    launchOut.send_message([NOTE_ON | 0x2, message[1], RECORDING])
                                    self.holo_loops[l] = -1
                                else:
                                    # start playing
                                    # green - pulsing
                                    launchOut.send_message([NOTE_ON | 0x2, message[1], GREEN[message[2] >> 4]])
                                    self.holo_loops[l] = message[2]
                            else:
                                if self.overdub:
                                    # overdub loop
                                    launchOut.send_message([NOTE_ON, message[1], RECORDING])
                                    self.holo_loops[l] = -1
                                else:
                                    # loop playing - stop
                                    # light blue - static
                                    launchOut.send_message([NOTE_ON, message[1], STOPPED])
                                    self.holo_loops[l] = 0
                    else:
                        # shift mode
                        # erase loop
                        self.holo_loops[l] = None
                        launchOut.send_message([NOTE_ON, message[1], EMPTY])
                elif message[1] in launchpad_drums:
                    fluidOut.send_message([NOTE_ON | 0x9, 36 + launchpad_drums.index(message[1]) + self.drum_bank*16, message[2]])
                    launchOut.send_message(message)
                elif message[1] in launchpad_fx:
                    pass
                elif message[1] in launchpad_mutes:
                        # mute / unmute inputs 1-4
                        n = 15 - message[1]
                        self.mutes[n] = not self.mutes[n]
                        holoOut.send_message([CONTROL_CHANGE, 41 + message[1], 0 if self.mutes[n] else 127])
                        launchOut.send_message([NOTE_ON, message[1], EMPTY if self.mutes[n] else RECORDING])
                else:
                    launchOut.send_message(message)
            else:
                # note off
                if message[1] in launchpad_drums:
                    fluidOut.send_message([NOTE_ON | 0x9, 36 + launchpad_drums.index(message[1]) + self.drum_bank*16, message[2]])
                    launchOut.send_message([NOTE_ON, message[1], DRUM_BANKS[self.drum_bank]])
        elif message[0] == CONTROL_CHANGE and data == 0:
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
                            launchOut.send_message([CONTROL_CHANGE, launchpad_scenes[self.current_scene], STOPPED])
                        self.current_scene = s
                        launchOut.send_message([CONTROL_CHANGE | 0x2, launchpad_scenes[self.current_scene], GREEN[-1]])
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
                                if scene[l] in (0, None):
                                    launchOut.send_message([NOTE_ON, launchpad_notes[l], STOPPED]) 
                                else:
                                     launchOut.send_message([NOTE_ON | 0x2, launchpad_notes[l], GREEN[scene[l] >> 4]])

                        print('recalled scene')
                        print(self.holo_loops)
                    else:
                        # store scene
                        print('storing scene', s)
                        print(self.holo_loops)
                        if self.current_scene != None:
                            # deactavate current scene - lights only
                            launchOut.send_message([CONTROL_CHANGE, launchpad_scenes[self.current_scene], STOPPED])
                        self.current_scene = s

                        self.holo_scenes[s] = self.holo_loops.copy()
                        launchOut.send_message([CONTROL_CHANGE, message[1], GREEN[-1]])

            elif message[1] in launchpad_functions:
                if message[1] == 98:
                    # caputre midi button
                    # enable shift functionality
                    self.shift = False if message[2] == 0 else True
                    holoOut.send_message(message)
                    launchOut.send_message(message)
                if self.shift:
                    if message[1] == 95:
                        # erase + session = delete-pulse
                        print('deleting pulse')
                        holoOut.send_message([CONTROL_CHANGE, 108, 0])
                        self.clear()
                else:
                    # normal mode
                    if message[1] == 91 and message[2] == 127:
                        # drum bank increment
                        self.drum_bank = min(self.drum_bank + 1, 3)
                        for i in launchpad_drums:
                            launchOut.send_message([NOTE_ON, i, DRUM_BANKS[self.drum_bank]])
                    elif message[1] == 92 and message[2] == 127:
                        # drum bank decrement
                        self.drum_bank = max(self.drum_bank - 1, -1)
                        for i in launchpad_drums:
                            launchOut.send_message([NOTE_ON, i, DRUM_BANKS[self.drum_bank]])
                    elif message[1] == 96:
                        # note button
                        # momentary cut mode - normal on release
                        self.toggleCut()
                    elif message[1] == 97 and message[2] == 127:
                        # note button
                        # toggle overdub on button press
                        self.toggleOverdub()
                    elif message[1] == 95:
                        # session button
                        # tap-pulse
                        if message[2] == 127:
                            holoOut.send_message([CONTROL_CHANGE, 95, 127])
                        launchOut.send_message([CONTROL_CHANGE, 95, message[2]])
                        
        elif message[0] & CONTROL_CHANGE and data == 1:
            print('pano midi', message)
            if message[1] == 113 and self.overdub != bool(message[2]) :
                # record button: overdub mode
                self.toggleOverdub()
            elif message[1] == 118:
                # mode button: cut mode
                self.toggleCut()


if __name__ == '__main__':
    try:
        holoOut, p = open_midioutput('FreeWheeling:FreeWheeling IN 1', client_name='holoOut')
        holoIn, p = open_midiinput('FreeWheeling:FreeWheeling OUT 1', client_name='holoIn')
        launchOut, p = open_midioutput('Launchpad X:Launchpad X MIDI 2', client_name='launchOut')
        launchIn, p = open_midiinput('Launchpad X:Launchpad X MIDI 2', client_name='launchIn')
        fluidOut, p = open_midioutput('FLUID Synth (ElectricMayhem)', client_name='ElectricMayhem', interactive=False)
        panoIn, p = open_midiinput('Virtual Raw MIDI 0-0', client_name='panoIn', interactive=False)

    except Exception as e:
        print('error opening ports')
        print(e)
    hc = HoloController()
    launchIn.set_callback(hc, 0)
    panoIn.set_callback(hc, 1)
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print('')
    finally:
        hc.exit()
        print("hub out!")
        
