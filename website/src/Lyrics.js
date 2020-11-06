import m from 'mithril'

export function Lyrics() {
  let setlist = []
  return {
    oninit: (vnode) => {
      m.request('/setlist').then(res => {
        setlist = res
      })
    },
    view: (vnode) => {
      return m('ul.setlist', {}, setlist.map(song => {
        return m('li', {}, song)
      }))
    }
  }
}

export function Search() {
  return {
    view: (vnode) => {
      return m('input.search', {}, [])
    }
  }
}