var svg, chord, inner, outer, fill, data;
load();

function load() {
	fill = d3.scale.ordinal()
		.domain(d3.range(4))
		.range(["#DDDDFF", "#CCCCEE", "#BBBBDD", "#AAAACC"]);
	d3.json('graph.json', function(error, json) {
		start(json);
	});
}

function start(json){
	data = json;
	var w = window.innerWidth,
		h = window.innerHeight;

	inner = Math.min(w, h) * .3;
	outer = inner * 1.1;
	
	
	svg = d3.select("body")
		.append("svg:svg")
		.attr("width", w)
		.attr("height", h)
		.append("svg:g")
		.attr("transform", "translate(" + w / 2 + "," + h / 2 + ")");
	
	chord = d3.layout.chord()
		.padding(.05)
		.sortSubgroups(d3.descending)
		.matrix(json.matrix);

	//Draw everything
	draw();
}


function draw() {
	addPaths();
	addTicks();
	stylePaths();
}

function addPaths() {
	svg.append("svg:g")
		.selectAll("path")
		.data(chord.groups)
		.enter().append("svg:path")
		.style("fill", getfill)
		.style("stroke", getfill)
		.attr("d", d3.svg.arc().innerRadius(inner).outerRadius(outer))
		.on("mouseover", fade(.1))
		.on("mouseout", fade(1));
}

function addTicks() {
	var ticks = svg.append("svg:g")
		.selectAll("g")
		.data(chord.groups)
		.enter().append("svg:g")
		.selectAll("g")
		.data(groupTicks)
		.enter().append("svg:g")
		.attr("transform", function(d) {
			return "rotate(" + (d.angle * 180 / Math.PI - 90) + ")"
		+ "translate(" + outer + ",0)";
		});

	ticks.append("svg:line")
		.attr("x1", 1)
		.attr("y1", 0)
		.attr("x2", 5)
		.attr("y2", 0)
		.style("stroke", "#000");

	ticks.append("svg:text")
		.attr("x", 8)
		.attr("dy", ".35em")
		.attr("text-anchor", function(d) {
			return d.angle > Math.PI ? "end" : null;
		})
		.attr("transform", function(d) {
			return d.angle > Math.PI ? "rotate(180)translate(-16)" : null;
		})
		.text(function(d) { 
			return d.label; 
		});
}

function stylePaths() {
	svg.append("svg:g")
		.attr("class", "chord")
		.selectAll("path")
		.data(chord.chords)
		.enter().append("svg:path")
		.style("fill", function(d) { 
			return fill(d.target.index); 
		})
		.attr("d", d3.svg.chord().radius(inner))
		.style("opacity", 1);
}

function getfill(sub) {
	return fill(sub.index);
}

/** Returns an array of tick angles and labels, given a group. */
function groupTicks(d) {
	result = [{
		angle: d.startAngle + ((d.endAngle - d.startAngle) / 2),
		label: data.groups[d.index].label
	}];
	return result;
}

/** Returns an event handler for fading a given chord group. */
function fade(opacity) {
	return function(g, i) {
		svg.selectAll("g.chord path")
	.filter(function(d) {
		return d.source.index != i && d.target.index != i;
	})
	.transition()
	.style("opacity", opacity);
	};
}

function reset() {
	d3.select("svg").remove();
	setTimeout(load, 250);
}
