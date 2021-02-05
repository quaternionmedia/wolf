from obswebsocket import obsws, requests

host = 'localhost'
port = 4444
password = ''

if __name__ == '__main__':
    from sys import argv
    ws = obsws(host, port, password)
    ws.connect()
    try:
        ws.call(requests.SetCurrentScene(argv[1]))

    except KeyboardInterrupt:
        pass
    finally:
        ws.disconnect()
