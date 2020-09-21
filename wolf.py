from mido import Backend, Message
from fastapi import FastAPI, WebSocket
from starlette.staticfiles import StaticFiles
from networkx import Graph
from networkx.readwrite.json_graph import cytoscape_data
from json import loads
from jack import Client

client = Client('wolf_connections')
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

@app.get('/connections')
async def getConnections():
    graph = Graph()
    ports = [ p.name for p in client.get_ports() ]
    print(ports)
    graph.add_nodes_from(ports)
    for p in ports:
        c = [ (p, c.name) for c in client.get_all_connections(p) ]
        if c:
            print(f'connection from {p} to {c}')
            graph.add_edges_from(c)
    print('graph', graph.nodes, graph.edges)
    return cytoscape_data(graph)

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
