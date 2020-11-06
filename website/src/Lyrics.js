import m from 'mithril'
import Fuse from 'fuse.js'

export function Lyrics() {
  
  let setlist = []
  let fuse = new Fuse(setlist, {
    keys: ['title'],
    threshold: .4,
  })
  let filter = ''
  let lyrics = ''
  function Song(song) {
    return m('li', {onclick: e => {
      m.request(`/lyrics/${song.id}`).then(res => {
        lyrics = res
      })
    }}, song.title)
  }
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
        }}, []),
        m('.songs', {}, [
          m('ul.setlist', {}, [
            filter ? fuse.search(filter).map(s => {
            return Song(s.item)
          }) : setlist.map(s => {
            return Song(s)
            })
          ]),
          m('textarea.lyrics', {}, lyrics),
        ])]
    }
  }
}



