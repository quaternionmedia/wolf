import m from 'mithril'
import { Selector } from './Mixer'
import cytoscape from 'cytoscape'
import edgehandles from 'cytoscape-edgehandles'
cytoscape.use( edgehandles )

export function Patchbay() {
  let cy, eh, elements
  return {
    oninit: vnode => {
    },
    oncreate: vnode => {
      cy = cytoscape({
        container: vnode.dom,
        elements: m.request('/connections').then(res => {
          let elems = res.elements
            return res.elements
          }),
        layout: {
               name: 'grid',
               padding: 0,
             },
        style: [

          {
            selector: 'node',
            style: {
              'background-color': '#aaa'
            }
          },
          {
            selector: ':selected',
            style: {
              'background-color': '#00f'
            }
          },
           {
             selector: 'node[name]',
             style: {
               'content': 'data(name)',
               'color': '#fff',
             }
           },

           {
             selector: 'edge',
             style: {
               'curve-style': 'bezier',
               'target-arrow-shape': 'triangle'
             }
           },

           // some style for the extension
           {
             selector: '.eh-handle',
             style: {
               'background-color': 'red',
               'width': 12,
               'height': 12,
               'shape': 'ellipse',
               'overlay-opacity': 0,
               'border-width': 12, // makes the handle easier to hit
               'border-opacity': 0
             }
           },

           {
             selector: '.eh-hover',
             style: {
               'background-color': 'red'
             }
           },

           {
             selector: '.eh-source',
             style: {
               'border-width': 2,
               'border-color': 'red'
             }
           },

           {
             selector: '.eh-target',
             style: {
               'border-width': 2,
               'border-color': 'red'
             }
           },

           {
             selector: '.eh-preview, .eh-ghost-edge',
             style: {
               'background-color': 'red',
               'line-color': 'red',
               'target-arrow-color': 'red',
               'source-arrow-color': 'red'
             }
           },
           {
             selector: '.eh-ghost-edge.eh-preview-active',
             style: {
               'opacity': 0
             }
           },
           {
             selector: ':parent',
             style: {
               'background-color': '#444',
               opacity: .8,
             }
           },
           {
             selector: '.midi',
             style: {
               'color': 'yellow'
             }
           },
           {
             selector: '.audio',
             style: {
               'color': 'green'
             }
           },
         ],
      })
      eh = cy.edgehandles({
        noEdgeEventsInDraw: true,
        snap: true
      })
      // let grid = cy.layout({name: 'grid'})
      // grid.run()
    },
    view: vnode => {
      return m('.graph', {}, )
    }
  }
}
