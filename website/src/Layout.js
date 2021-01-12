import m from 'mithril'
import { Menu } from './Menu'

export function Layout() {
  return {
    view: vnode => {
      return m('main.layout', {}, [
        m('nav.menu', {}, m(Menu)),
        m('section', vnode.children)
      ])
    }
  }
}