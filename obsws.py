from obswebsocket import obsws, requests
from sys import argv
from argparse import ArgumentParser
from config import HOST, PORT, PASSWORD


class ObsWs:
    def __init__(self):
        parser = ArgumentParser(description='obs websocket cli')
        parser.add_argument('command',
            type=str,
            help='the function to call in obs-websocket'
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

if __name__ == '__main__':
    ObsWs()
