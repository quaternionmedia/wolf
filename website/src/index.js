import m from 'mithril'
import { Layout } from './Menu'
import { Mixer } from './Mixer'
import { PatchbayPage } from './Patchbay'
import { Lyrics } from './Lyrics'
import { Control } from './Control'
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
  '/control': { render: () => m(Layout, m(Control))},
})
