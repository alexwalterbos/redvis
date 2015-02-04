function draw() {
	var request = new XMLHttpRequest();
	request.open("GET", "graph.json", false);
	request.send(null)

	var data = JSON.parse(request.responseText);
	console.log(data);
	
	// Instantiate our network object.
	var container = document.getElementById('subreddits');

	var options = {
		nodes: {
		  shape: 'dot'
		},
		edges: {
		  color: '#97C2FC'
		}
	};
	
	network = new vis.Network(container, data, options);
}
