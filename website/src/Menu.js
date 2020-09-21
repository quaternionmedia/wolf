import m from 'mithril'


export function Link() {
  return {
    view: (vnode) => {
      return m('.menu-item', [
        m(m.route.Link, vnode.attrs, vnode.children)
      ])
    }
  }
}

export function Links() {
  return {
    view: vnode => {
      return [
        m(Link, {href:'/mixer', id: 'mixer'}, 'mixer'),
        m(Link, {href: '/patchbay', id: 'patchbay'}, 'patchbay'),
      ]
    }
  }
}
