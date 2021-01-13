import m from 'mithril'
import { Fader } from './Mixer'

export function Control() {
  return {
    view: vnode => {
      return m('.control', {}, m(Fader))
    }
  }
}
