import m from 'mithril'
import { Channel, Mixer } from './Mixer'
import './style.css'

console.log('wolf!')

export function Home() {
  return {
    view: vnode => {
      return m('#home', {}, [
        m('', {}, 'wolf!'),
        m(Mixer, {channels: [
          {name: 'test', value: 127, control: 0},
          {name: 'reverb', value: 12, control:7}
        ]}),
      ])
    }
  }
}

m.route(document.body, "/", {
  "/": Home,
})
