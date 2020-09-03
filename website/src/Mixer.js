import m from 'mithril'
import interact from 'interactjs'

var Stream = require("mithril/stream")
export let ws = new WebSocket(`ws://${window.location.host}/ws`)

const debounce = 30

ws.onopen = e => {
  console.log('opened ws')
}
ws.onmessage = e => {
  console.log(e.data)
}

export function Fader() {
  const position = { x: 0, y: 0 }
  let value = 0
  let lastsend = new Date()
  return {
    oncreate: vnode => {
      interact(vnode.dom).draggable({
        origin: 'self',
        inertia: true,
        modifiers: [
          interact.modifiers.restrict({
            restriction: 'self'
          })
        ],
      }).on('dragmove', function (event) {
    const sliderWidth = interact.getElementRect(event.target.parentNode).width
    const p = event.pageX / sliderWidth

    event.target.style.paddingLeft = (p * 100) + '%'
    event.target.setAttribute('data-value', (p*100).toFixed(2))
    value = parseInt(p*127)
    event.target.setAttribute('value', value)
    if (new Date() - lastsend > debounce) {
      ws.send(JSON.stringify({
        channel: vnode.attrs.channel,
        control: vnode.attrs.control,
        value: value
      }))
      lastsend = new Date()
    } else {
      console.log('debouncing')
    }
    // m.redraw()
      })
      vnode.dom.style.paddingLeft = (vnode.attrs.value / 1.27) + '%'
    },
    view: vnode => {
      return m('.slider', {value: vnode.attrs.value})
    }
  }
}


export function Mixer() {
  let channels = []
  return {
    oninit: vnode => {
      m.request('/channels').then(e => {
        console.log(e)
        channels = Object.entries(e['calf_vocal']['Vocal Reverb'])
      })
    },
    view: vnode => {
      return m('.mixer#mixer', {}, [
        channels.map((c, i) => {
          console.log('making channel', c)
          return m('.channel', {}, [
            m('', {}, channels[i][0]),
            m(Fader, {
            channel: Math.floor(c[1].control/256),
            control: c[1].control,
            value: c[1].value,
          })])
        })
      ])
    }
  }
}