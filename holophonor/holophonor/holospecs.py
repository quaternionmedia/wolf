from pluggy import HookspecMarker
from rtmidi.midiutil import open_midioutput

holospec = HookspecMarker('holophonor')

class Holophonor:
    def __init__(self, hook, port, plugins=[]):
        self.hook = hook
        self.port = port
        self.midi, self.name = open_midioutput(self.port, client_name='holo->fweelin')
        self.plugins = plugins
        self.loops = [None]*32
        self.scenes = [None]*8
        self.current_scene = None
        self.shift = False
        self.mutes = [False]*4
        self.overdub = False
        self.cut = False
        self.tap = False
    
    @holospec
    def playLoop(self, loop: int, volume: int):
        '''play loop at volume'''
    
    @holospec
    def stopLoop(self, loop: int):
        '''pause loop'''
    
    @holospec
    def recordLoop(self, loop: int):
        '''record loop'''
    
    @holospec
    def eraseLoop(self, loop: int):
        '''erase the selected loop'''
    
    @holospec
    def clearLoop(self, loop: int):
        '''clear the button on release for the selected loop'''
    
    @holospec
    def startLoopInCutMode(self, loop: int, volume: int):
        '''fix for FreeWheeling not starting loops while in cut mode'''
    
    @holospec
    def overdubLoop(self, loop: int):
        '''overdub the selected loop'''
        
    @holospec
    def recallScene(self, scene: int):
        '''recall a scene'''
    
    @holospec
    def storeScene(self, scene: int):
        '''store a scene'''
    
    @holospec
    def eraseScene(self, scene: int):
        '''erase a scene'''
    
    @holospec
    def clearScene(self, scene: int):
        '''release the scene button'''
    
    @holospec
    def toggleShift(self):
        '''toggle shift mode'''
    
    @holospec
    def toggleCut(self):
        '''toggle cut mode'''
    
    @holospec
    def toggleOverdub(self):
        '''toggle overdub mode'''
    
    @holospec
    def deletePulse(self):
        '''delete pulse'''
    
    @holospec
    def clearPulse(self):
        '''release pulse button'''
    
    # @holospec
    # def clear(self):
    #     '''clear all loops'''
    
    @holospec
    def tapPulse(self):
        '''tap pulse'''
    
    @holospec
    def toggleMute(self, channel: int):
        '''toggle mute on channel'''
    
    @holospec
    def toggleFX(self, fx: int):
        '''toggle fx'''
    
    @holospec
    def setDrumPatch(self, patch: int):
        '''set drum pad patch'''
    
    @holospec
    def setDrumBank(self, patch: int):
        '''set drum pad bank'''
    

    @holospec
    def close(self):
        '''close the connection'''
    
    