import m from 'mithril'
import { Links } from './Menu'
import { Mixer } from './Mixer'
import { PatchbayPage } from './Patchbay'
import './style.css'

console.log('wolf!')

export function Home() {
  return {
    view: vnode => {
      return m('#home', {}, [
        m('', {}, 'wolf!'),
        m(Links),
      ])
    }
  }
}

m.route(document.body, "/", {
  '/': Home,
  '/mixer': Mixer,
  '/patchbay': PatchbayPage,
})
