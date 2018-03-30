
var blocks = [
  { blockid : 'hash0x00', hostname : 'genesisblock', time : 12345001, validates : []},
  { blockid : 'hash0x01', hostname : 'genesisblock', time : 12345002, validates : []},
  { blockid : 'mta01', hostname : 'MTA', time : 12345010, validates : ['hash0x00', 'hash0x01']},
  { blockid : 'cdn01', hostname : 'CDN', time : 12345020, validates : ['mta01', 'hash0x01']},
  { blockid : 'mta02', hostname : 'MTA', time : 12345030, validates : ['mta01', 'cdn01']}
]

function generateImg(blocks) {
  // Create the input graph
  var g = new dagreD3.graphlib.Graph()
    .setGraph({})
    .setDefaultEdgeLabel(function() { return {} })
  
  var knownhosts = [] // we keep track of all the hostnames, they will be in a lane
  var knownblocks = []
  //first we will set the nodes
  blocks.forEach(function(blck){
    if (knownhosts.indexOf(blck['hostname']) === -1)
      knownhosts.push(blck['hostname'])
    var swimlane = knownhosts.indexOf(blck['hostname']) // y axis
    var id = blck['blockid']
    knownblocks.push(id)
    g.setNode(id, { label : id, x : blck['time'], y : swimlane * 10})
  })
  
  //we continue by drawing the relations
  
  blocks.forEach(function(blck){
    var id = blck['blockid']
    blck['validates'].forEach(function(hash){
      if(knownblocks.indexOf(hash) !== -1) // only if it actually exists
        g.setEdge(id,hash)
      else console.log('failed to link to',hash)
    })
  })
  
  
  /*
  The following code is copied, see the following links
  https://github.com/dagrejs/dagre/wiki <- we should use the layout from this one, TODO
  https://github.com/dagrejs/dagre-d3/wiki <-copied from
  https://github.com/nickholub/d3-dag-visualization could be useful
  */
  
  // Create the renderer
  var render = new dagreD3.render();
  
  // Set up an SVG group so that we can translate the final graph.
  var svg = d3.select("svg"),
      svgGroup = svg.append("g");
  
  // Run the renderer. This is what draws the final graph.
  render(d3.select("svg g"), g);
  
  // Center the graph
  var xCenterOffset = (svg.attr("width") - g.graph().width) / 2;
  svgGroup.attr("transform", "translate(" + xCenterOffset + ", 20)");
  svg.attr("height", g.graph().height + 40);
}


generateImg(blocks) // example image

function loadfile(){
    $.getJSON( "datadir/logdag.json", function( json ) {
          window.data_from_server = json
          console.log(json)
          generateImg(json['LogDAG'])
        });
}

window.setInterval(loadfile,30000) // every half minute
