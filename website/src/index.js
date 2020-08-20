console.log('wolf!')

import m from 'mithril'

export function Home() {
  return {
    view: vnode => {
      return m('#home', {}, 'wolf!')
    }
  }
}

m.route(document.body, "/", {
  "/": Home,
})
