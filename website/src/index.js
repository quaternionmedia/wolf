import m from 'mithril'
import { Mixer } from './Mixer'
import './style.css'

console.log('wolf!')

export function Home() {
  return {
    view: vnode => {
      return m('#home', {}, [
        m('', {}, 'wolf!'),
        m(Mixer, {channels: [
          {name: 'aging', channel: 1, control: 52, value: 0, },
          {name: 'vocal reverb', channel: 0, control:39, value: 111}
        ]}),
      ])
    }
  }
}

m.route(document.body, "/", {
  "/": Home,
})
