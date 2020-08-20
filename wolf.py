from mido import Backend, Message
from fastapi import FastAPI

jack = Backend('mido.backends.rtmidi/UNIX_JACK')
outport = jack.open_output()

app = FastAPI()

@app.get('/cc')
async def sendCC(channel: int = 0, control: int = 0, value: int = 0):
    message = Message('control_change', channel=channel, control=control, value=value)
    outport.send(message)

if __name__ == '__main__':
    from uvicorn import run
    run(app, host='0.0.0.0', port=8000)
