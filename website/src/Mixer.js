import m from 'mithril'
import interact from 'interactjs'

var Stream = require("mithril/stream")

export function Channel() {
  const position = { x: 0, y: 0 }
  let value = 0
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
    // m.redraw()
      })
      vnode.dom.style.paddingLeft = (vnode.attrs.value / 1.27) + '%'
    },
    view: vnode => {
      return m('.channel.slider', {value: vnode.attrs.value})
    }
  }
}


export function Mixer() {
  let channels = []
  let ws
  return {
    oninit: vnode => {
      ws =
      channels = vnode.attrs.channels
    },
    view: vnode => {
      return m('.mixer#mixer', {}, [
        channels.map((c, i) => {
          return m(Channel, {
            name: c.name,
            control: c.control,
            value: c.value
          })
        })
      ])
    }
  }
}
