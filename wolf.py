from mido import Backend, Message
from fastapi import FastAPI, WebSocket
from starlette.staticfiles import StaticFiles
from json import loads

jack = Backend('mido.backends.rtmidi/UNIX_JACK')
outport = jack.open_output('out', client_name='wolf')

app = FastAPI()

@app.get('/cc')
async def sendCC(channel: int = 0, control: int = 0, value: int = 0):
    message = Message('control_change', channel=channel, control=control, value=value)
    outport.send(message)

@app.get('/channels')
async def getChannels():
    with open('racks.json') as f:
        return loads(f.read())

@app.websocket('/ws')
async def getInput(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        await websocket.send_text(f"Message text was: {data}")
        print(data)
        m = Message('control_change', channel=data['channel'], control=data['control'], value=data['value'])
        outport.send(m)

app.mount("/", StaticFiles(directory='website/dist', html=True), name="static")

if __name__ == '__main__':
    from uvicorn import run
    run(app, host='0.0.0.0', port=8000)
