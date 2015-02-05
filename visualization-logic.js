function draw() {
	// Load data
	var request = new XMLHttpRequest();
	request.open("GET", "graph.json", false);
	request.send(null)
	var data = JSON.parse(request.responseText);
	
	// Instantiate our network object.
	var container = document.getElementById('subreddits');

	var options = {
		smoothCurves: {
			type: 'straightCross',
			roundness: 0
		},
		nodes: {
		  shape: 'dot'
		},
		edges: {
		  color: '#97C2FC'
		}
	};
	
	network = new vis.Network(container, data, options);
}
