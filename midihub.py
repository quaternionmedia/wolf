import rtmidi
from time import time, sleep
from collections import deque
from rtmidi.midiutil import open_midioutput, open_midiinput
from rtmidi.midiconstants import NOTE_ON, NOTE_OFF, POLY_AFTERTOUCH, CONTROL_CHANGE, PROGRAM_CHANGE
from operator import xor

NUMBER_LOOPS = 32

EMPTY = 0 # black
RECORDING = 5 # red
PLAYING = 21 # green
STOPPED = 43 # navy
CUT = 13 # cut mode - yellow
ERASE = 84 # orange
PULSE = 55 # dim pink
TAP = 53 # bright pink
GREEN = [ 123, 23, 64, 22, 76, 87, 21, 122 ]
DRUM_BANKS = [69, 79, 35, 15, 59]
DRUM_PATCHES = [0, 8, 25, 32]
FX = [4, 11, 12, 16, 20, 28, 36, 44, 52, 55, 59, 69, ]
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
launchpad_drum_patches = [25, 26, 27, 28]
launchpad_fx = [35, 36, 37, 38, 45, 46, 47, 48]
launchpad_mutes = [15, 16, 17, 18]

class HoloController:
    def __init__(self):
        self.current_scene = None
        self.live = True
        self.shift = False
        self.holo_loops = [None]*NUMBER_LOOPS
        self.holo_scenes = [None]*8
        self.mutes = [False]*4
        self.fx = [False]*12
        self.drum_bank = 0
        self.overdub = False
        self.cut = False
        self.tap = False
        self.toggleLive()
        self.clear()
    def clear(self):
        for i in range(11, 89):
            launchOut.send_message([NOTE_ON, i, 0])
        for i in launchpad_scenes:
            launchOut.send_message([CONTROL_CHANGE, i, 0])
        for i in launchpad_functions[:4]:
            launchOut.send_message([CONTROL_CHANGE, i, 0])
        self.holo_loops = [None]*NUMBER_LOOPS
        self.holo_scenes = [None]*8
        for i in range(len(launchpad_mutes)):
            launchOut.send_message([NOTE_ON, launchpad_mutes[i], EMPTY if self.mutes[i] else RECORDING])
        for i in launchpad_drums:
            launchOut.send_message([NOTE_ON, i, DRUM_BANKS[self.drum_bank]])
        launchOut.send_message([CONTROL_CHANGE, 91, DRUM_BANKS[min(self.drum_bank + 1, 3)]])
        launchOut.send_message([CONTROL_CHANGE, 92, DRUM_BANKS[max(self.drum_bank - 1, -1)]])
        launchOut.send_message([CONTROL_CHANGE, 99, 69])
        launchOut.send_message([CONTROL_CHANGE, 95, PULSE])
        launchOut.send_message([CONTROL_CHANGE, 96, CUT if self.cut else EMPTY])
        launchOut.send_message([CONTROL_CHANGE, 97, RECORD if self.overdub else EMPTY])
        self.tap = False

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
        # print('cut mode', self.cut)
    def changeDrumBank(self, bank):
        self.drum_bank = bank
        print('chaning drum bank', self.drum_bank)
        if bank >= -1 and bank <= 3:
            launchOut.send_message([CONTROL_CHANGE, 91, DRUM_BANKS[min(bank + 1, 3)]])
            launchOut.send_message([CONTROL_CHANGE, 92, DRUM_BANKS[max(bank - 1, -1)]])
            for i in launchpad_drums:
                launchOut.send_message([NOTE_ON, i, DRUM_BANKS[bank]])
    def exit(self):
        self.toggleLive()
    def __call__(self, event, data=None):
        message, deltatime = event
        # print(data, message)
        if message[0] == NOTE_ON and data == 0:
            if message[1] in launchpad_notes:
                l = launchpad_notes.index(message[1])
                if message[2]:
                    # note on
                    holoOut.send_message([NOTE_ON, l, message[2]])
                    if not self.shift:
                        # normal (unshifted) mode
                        if self.cut:
                            # cut mode
                            if self.holo_loops[l] in (0, None):
                                # FreeWheeling doesn't start loops in cut mode if they are paused, recording, or don't exist. This is a fix for that.
                                holoOut.send_message([CONTROL_CHANGE, 118, 0])
                                holoOut.send_message([NOTE_ON, l, message[2]])
                                holoOut.send_message([CONTROL_CHANGE, 118, 127])
                            if self.holo_loops[l] == None:
                                # no existing loop. we are recording
                                launchOut.send_message([NOTE_ON | 0x2, message[1], RECORDING])
                                self.holo_loops[l] = 0
                                
                            else:
                                # loop was paused. should be playing now
                                launchOut.send_message([NOTE_ON | 0x2, message[1], GREEN[message[2] >> 4]])
                                self.holo_loops[l] = message[2]
                            
                        else:
                            # normal (non-cut) mode
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
                                # loop is playing
                                if self.overdub:
                                    # overdub loop
                                    launchOut.send_message([NOTE_ON, message[1], RECORDING])
                                    self.holo_loops[l] = -1
                                else:
                                    # stop loop
                                    # light blue - static
                                    launchOut.send_message([NOTE_ON, message[1], STOPPED])
                                    self.holo_loops[l] = 0
                    else:
                        # shift mode
                        # erase loop
                        self.holo_loops[l] = None
                        launchOut.send_message([NOTE_ON, message[1], ERASE])
                else:
                    # note off
                    if self.holo_loops[l] is None:
                        # if we deleted the loop clear the color
                        launchOut.send_message([NOTE_ON, message[1], 0])        
            elif message[1] in launchpad_drums:
                fluidOut.send_message([NOTE_ON | 0x9, 36 + launchpad_drums.index(message[1]) + self.drum_bank*16, message[2]])
                launchOut.send_message([*message[:2], message[2] if message[2] else DRUM_BANKS[self.drum_bank]])
            elif message[1] in launchpad_fx and message[2]:
                f = launchpad_fx.index(message[1])
                self.fx[f] = not self.fx[f]
                bitwigOut.send_message([CONTROL_CHANGE, message[1], 127 if self.fx[f] else 0])
                launchOut.send_message([*message[:2], FX[f] if self.fx[f] else EMPTY])
            elif message[1] in launchpad_drum_patches and message[2]:
                i = launchpad_drum_patches.index(message[1])
                fluidOut.send_message([PROGRAM_CHANGE | 9, DRUM_PATCHES[i]])
                launchOut.send_message(message)
                # clear other patch buttons
                for b in set(launchpad_drum_patches) - {message[1]}:
                    launchOut.send_message([NOTE_ON, b, 0])
            elif message[1] in launchpad_mutes and message[2]:
                    # mute / unmute inputs 1-4
                    n = 15 - message[1]
                    self.mutes[n] = not self.mutes[n]
                    holoOut.send_message([CONTROL_CHANGE, 41 + message[1], 0 if self.mutes[n] else 127])
                    launchOut.send_message([NOTE_ON, message[1], EMPTY if self.mutes[n] else RECORDING])
            else:
                # no matching rule found for message
                # launchOut.send_message(message)
                pass
        elif message[0] == CONTROL_CHANGE and data == 0:
            # print('control change', message)
            if message[1] in launchpad_scenes:
                s = launchpad_scenes.index(message[1])
                if message[2] == 127:
                    # scene button pressed
                    if self.shift:
                        # erase scene
                        print('erasing scene', s)
                        self.holo_scenes[s] = None
                        launchOut.send_message([NOTE_ON, message[1], ERASE])
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
                else:
                    # scene button released
                    if self.holo_scenes[s] is None:
                        launchOut.send_message([NOTE_ON, message[1], 0])
            elif message[1] in launchpad_functions:
                if message[1] == 98:
                    # caputre midi button
                    # enable shift functionality
                    self.shift = False if message[2] == 0 else True
                    holoOut.send_message(message)
                    launchOut.send_message([*message[:2], ERASE if message[2] else 0])
                if self.shift:
                    if message[1] == 95:
                        # erase + session = delete-pulse
                        if message[2] == 127:
                            print('deleting pulse')
                            holoOut.send_message([CONTROL_CHANGE, 108, 0])
                            self.clear()
                        launchOut.send_message([CONTROL_CHANGE, 95, ERASE if message[2] else PULSE])

                else:
                    # normal mode
                    if message[1] == 91 and message[2] == 127:
                        # drum bank increment
                        self.changeDrumBank(min(self.drum_bank + 1, 3))
                    elif message[1] == 92 and message[2] == 127:
                        # drum bank decrement
                        self.changeDrumBank(max(self.drum_bank - 1, -1))
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
                            self.tap = not self.tap
                        # this also clears the ERASE color from the Session button if shift mode is released first
                        launchOut.send_message([CONTROL_CHANGE, 95, TAP if self.tap else PULSE])
        elif (message[0] & 0xF0 == CONTROL_CHANGE) and data == 1:
            print('pano midi', message, data)
            if message[1] == 113 and self.overdub != bool(message[2]) :
                # record button: overdub mode
                self.toggleOverdub()
            elif message[1] == 118:
                # mode button: cut mode
                self.toggleCut()
            elif message[1] == 3:
                # master volume
                holoOut.send_message(message)


if __name__ == '__main__':
    try:
        holoOut, p = open_midioutput('FreeWheeling:FreeWheeling IN 1', client_name='holoOut')
        holoIn, p = open_midiinput('FreeWheeling:FreeWheeling OUT 1', client_name='holoIn')
        launchOut, p = open_midioutput('Launchpad X:Launchpad X MIDI 2', client_name='launchOut')
        launchIn, p = open_midiinput('Launchpad X:Launchpad X MIDI 2', client_name='launchIn')
        fluidOut, p = open_midioutput('FLUID Synth (ElectricMayhem)', client_name='ElectricMayhem', interactive=False)
        panoIn, p = open_midiinput('Virtual Raw MIDI 0-0', client_name='panoIn', interactive=False)
        bitwigOut, p = open_midioutput('Virtual Raw MIDI 0-0', client_name='bitwigOut', interactive=False)
    except Exception as e:
        print('error opening ports')
        print(e)
        
    try:
        hc = HoloController()
        launchIn.set_callback(hc, 0)
        panoIn.set_callback(hc, 1)
    except Exception as e:
        print('error setting callbacks')
        print(e)
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print('')
    finally:
        hc.exit()
        print("hub out!")
        
