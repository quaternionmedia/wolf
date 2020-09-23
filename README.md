# wolf
realtime control server

## install
install npm dependencies
`./wolf install`


## build
build js files, with live rebuilding watcher
`./wolf build`

## run
run server
`uvicorn --reload --host 0.0.0.0 --port 5000 wolf:app`

visit http://localhost:5000
