import m from 'mithril'
import Fuse from 'fuse.js'

export function Lyrics() {
  
  let setlist = []
  let fuse = new Fuse(setlist, {
    // keys: ['title'],
    threshold: .35,
  })
  let filter = ''
  let lyrics = ''
  let pdfLink = ''
  function Song(song) {
    return m('li', {onclick: e => {
      m.request(`/lyrics/${song}`).then(res => {
        lyrics = res
      })
      pdfLink = `/static/pdf/${song}.pdf`
    }}, song)
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
              console.log('match', s)
            return Song(s.item)
          }) : setlist.map(s => {
            return Song(s)
            })
          ]),
          lyrics ? m('pre.lyrics', {}, lyrics) : null,
          pdfLink ? m('iframe.sheet', {
            src: pdfLink,
          }, ) : null,
        ])]
    }
  }
}



