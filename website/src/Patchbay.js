import m from 'mithril'
import cytoscape from 'cytoscape'
import edgehandles from 'cytoscape-edgehandles'

cytoscape.use( edgehandles )

export function Patchbay() {
  let cy
  return {
    oncreate: vnode => {
      cy = cytoscape({
        container: vnode.dom,
        elements: [ // list of graph elements to start with
    { // node a
      data: { id: 'a' }
    },
    { // node b
      data: { id: 'b' }
    },
    { // edge ab
      data: { id: 'ab', source: 'a', target: 'b' }
    }
  ],

  style: [ // the stylesheet for the graph
    {
      selector: 'node',
      style: {
        'background-color': '#666',
        'label': 'data(id)'
      }
    },

    {
      selector: 'edge',
      style: {
        'width': 3,
        'line-color': '#ccc',
        'target-arrow-color': '#ccc',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier'
      }
    }
  ],

  layout: {
    name: 'grid',
    rows: 1
  }
      })
    },
    view: vnode => {
      return m('.patchbay#patchbay', {}, )
    }
  }
}
