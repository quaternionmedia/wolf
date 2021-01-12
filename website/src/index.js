import m from 'mithril'
import { Menu } from './Menu'
import { Layout } from './Layout'
import { Mixer } from './Mixer'
import { PatchbayPage } from './Patchbay'
import { Lyrics } from './Lyrics'
import './style.css'

console.log('wolf!')

export function Home() {
  return {
    view: vnode => {
      return m('#home', {}, [
        m('meta', {
          name: 'viewport',
          content: 'width=device-width,initial-scale=1.01,minimal-ui'
        })
      ])
    }
  }
}

m.route(document.body, "/", {
  '/': { render: () => m(Layout, m(Home))},
  '/mixer': { render: () => m(Layout, m(Mixer))},
  '/patchbay': { render: () => m(Layout, m(PatchbayPage))},
  '/lyrics': { render: () => m(Layout, m(Lyrics))},
})
