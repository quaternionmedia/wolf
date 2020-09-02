from mido import Backend, Message
import asyncio

jack = Backend('mido.backends.rtmidi/UNIX_JACK')

holophonor = jack.open_output('holophonor', client_name='holoOutput')
automation = jack.open_output('automation', client_name='otto')
drums = jack.open_output('drums', client_name='animal')

launchpad_holophonor = [0,1,2,3,16,17,18,19,32,33,34,35,48,49,50,51,64,65,66,67,80,81,82,83,96,97,98,99,108,112,113,114,115]
launchpad_automation = [4,5,6,7,20,21,22,23,36,37,38,39,52,53,54,55]
launchpad_drums = [68,69,70,71,84,85,86,87,100,101,102,103,116,117,118,119]

drum_map = [32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47]

active = set()

def make_stream():
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()
    def callback(message):
        loop.call_soon_threadsafe(queue.put_nowait, message)
    async def stream():
        while True:
            yield await queue.get()
    return callback, stream()

async def print_messages():
    cb, stream = make_stream()
    jack.open_input('holo', client_name='holoInput', callback=cb)
    async for message in stream:
        print(message)
        if message.type in ['note_on', 'note_off']:
            if message.note in launchpad_holophonor:
                holophonor.send(message)
            elif message.note in launchpad_automation:
                if message.note in active:
                  velocity = 0
                  active.remove(message.note)
                else:
                  velocity = 127
                  active.add(message.note)
                m = Message('control_change', channel=15, control=message.note, value=velocity)
                automation.send(m)
            elif message.note in launchpad_drums:
                message.note = drum_map[launchpad_drums.index(message.note)]
                drums.send(message)

if __name__ == '__main__':
    # loop.run_until_complete(print_messages())
    # loop.close()
    asyncio.ensure_future(print_messages())
    loop = asyncio.get_event_loop()
    loop.run_forever()
