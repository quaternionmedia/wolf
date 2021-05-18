from obswebsocket import obsws, requests
from sys import argv
from argparse import ArgumentParser
from config import HOST, PORT, PASSWORD

usage = '''obsws <command> [<args>]

The most commonly used commands are:
   scene [scene]            set the current scene
   preview [scene]          set the current preview
   transition [transition]  set the current transition
   program                  transition to program
'''


class ObsWs:
    def __init__(self):
        parser = ArgumentParser(
            description='obs websocket cli',
            usage=usage,

        )
        parser.add_argument('command',
            type=str,
            help='the function to call in obs-websocket',
        )
        args = parser.parse_args(argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        
        self.ws = obsws(HOST, PORT, PASSWORD)
        self.ws.connect()

        getattr(self, args.command)()
    
    def scene(self):
        parser = ArgumentParser(description='change scene')
        parser.add_argument('scene',
            type=str,
            help='name of scene to select'
        )
        args = parser.parse_args(argv[2:])
        try:
            self.ws.call(requests.SetCurrentScene(args.scene))
        finally:
            self.ws.disconnect()
    
    def transition(self):
        parser = ArgumentParser(description='change transition')
        parser.add_argument('transition',
            type=str,
            help='name of transition to select'
        )
        args = parser.parse_args(argv[2:])
        try:
            self.ws.call(requests.SetCurrentTransition(args.transition))
        finally:
            self.ws.disconnect()
    
    def preview(self):
        parser = ArgumentParser(description='set preview scene')
        parser.add_argument('scene',
            type=str,
            help='name of preview scene to select'
        )
        args = parser.parse_args(argv[2:])
        try:
            self.ws.call(requests.SetPreviewScene(args.scene))
        finally:
            self.ws.disconnect()
    
    def program(self):
        parser = ArgumentParser(description='transition preview to program')
        args = parser.parse_args(argv[2:])
        try:
            self.ws.call(requests.TransitionToProgram())
        finally:
            self.ws.disconnect()


if __name__ == '__main__':
    ObsWs()
