from mido import Backend, Message
from fastapi import FastAPI, WebSocket, HTTPException, Query
from starlette.staticfiles import StaticFiles
from networkx import Graph, set_node_attributes
# from networkx.readwrite.json_graph import cytoscape_data
from cyto import cytoscape_data
from json import loads
from jack import Client
from glob import glob
from os.path import basename
from typing import List

backend = Backend('mido.backends.rtmidi/UNIX_JACK')
outport = backend.open_output('out', client_name='wolf')

client = Client('wolf_connections')

@client.set_port_connect_callback
def port_connect(a, b, connect):
    print(['disconnected', 'connected'][connect], a, 'and', b)

app = FastAPI()

@app.get('/cc')
async def sendCC(channel: int = 0, control: int = 0, value: int = 0):
    print(f'sending control - channel {channel} - control {control} - value {value}')
    message = Message('control_change', channel=channel, control=control, value=value)
    outport.send(message)

@app.get('/note')
async def sendNote(channel: int = 0, note: int = 0, velocity: int = 0):
    print(f'sending note - channel {channel} - note {note} - velocity {velocity}')

    message = Message('note_on', channel=channel, note=note, velocity=velocity)
    outport.send(message)

@app.get('/sysex')
async def sendSysex(data: List[int] = Query([])):
    message = Message('sysex', data=data)
    outport.send(message)

@app.get('/channels')
async def getChannels():
    with open('racks.json') as f:
        return loads(f.read())

@app.get('/connections')
async def getConnections():
    graph = Graph()
    ports = [ p.name for p in client.get_ports() ]
    # print(ports)
    clients = set()
    graph.add_nodes_from(ports)
    set_node_attributes(graph, { p:{'parent': p.split(':')[0]} for p in ports})
    for p in ports:

        clientName = p.split(':')[0]
        clients.add(clientName)
        c = [ (p, c.name) for c in client.get_all_connections(p) ]
        if c:
            # print(f'connection from {p} to {c}')
            graph.add_edges_from(c)
    graph.add_nodes_from(clients)
    # print('graph', graph.nodes, graph.edges)
    return cytoscape_data(graph)

@app.get('/connect')
async def connectPorts(source: str, dest: str):
    try:
        client.connect(source, dest)
    except Exception as e:
        print('error connecting ports', source, dest, e)
        raise HTTPException(status_code=500, detail='error connecting ports')

@app.websocket('/ws')
async def getInput(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()
        await websocket.send_text(f"Message text was: {data}")
        # print(data)
        m = Message('control_change', channel=data['channel'], control=data['control'], value=data['value'])
        outport.send(m)

from trello import TrelloClient
with open('trello.json') as f:
    trello_cred = loads(f.read())

trello_client = TrelloClient(api_key=trello_cred['api_key'], api_secret=trello_cred['api_secret'])

@app.get('/setlist')
async def getSetlist():
    # cards = trello_client.get_list('5f5825c1c8324410fbb531e0').list_cards()
    # setlist = [ {'title': card.name, 'id': card.id} for card in cards]
    setlist = [basename(i)[:-4] for i in glob('static/pdf/*.pdf')]
    print(setlist)
    return setlist

@app.get('/lyrics/{song}')
async def getLyrics(song: str):
    try:
        return trello_client.get_card(song).description
    except Exception as e:
        print('error getting lyrics')
        print(e)
        raise HTTPException(status_code=404, detail='no lyrics found')


app.mount("/static", StaticFiles(directory='static', html=True), name="static")
app.mount("/", StaticFiles(directory='website/dist', html=True), name="dist")

if __name__ == '__main__':
    from uvicorn import run
    run(app, host='0.0.0.0', port=5000)
