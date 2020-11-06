import m from 'mithril'
import Fuse from 'fuse.js'

export function Lyrics() {
  let setlist = []
  let fuse = new Fuse(setlist, {
    threshold: .4,
  })
  let filter = ''
  return {
    oninit: (vnode) => {
      m.request('/setlist').then(res => {
        setlist = res
        fuse.setCollection(res)
      })
    },
    view: (vnode) => {
      return [
        m('input.search', {oninput: (v) => {
          console.log('searching', v.target.value)
          filter = v.target.value
          m.redraw()
        }}, []),
        m('ul.setlist', {}, [
          filter ? fuse.search(filter).map(song => {
          return m('li', {}, song.item)
        }) : setlist.map(song => {
          return m('li', {}, song)
        })
        ])
      ]
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