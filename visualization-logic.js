var svg, chord, inner, outer, fill;
hideLoad();

function sortSubgroups(a, b){
	return d3.ascending(a,b);
}

function reset() {
	d3.select('svg').remove();
	showLoad();
}

function hideLoad() {
	d3.select('#update').attr('disabled', null);
}

function showLoad() {
	d3.select('#update').attr('disabled', 'disabled');
}

function start(json){
	hideLoad();
	// Generate colors
	colorRange = [];
	for(i = 0; i < json.matrix.length; i++){
		colorRange.push(HSVtoRGB( i * 1/json.matrix.length, 0.6, 1));
	}
	shuffleArray(colorRange);
	fill = d3.scale.ordinal()
		.domain(d3.range(json.matrix.length))
		.range(colorRange);

	var w = window.innerWidth,
		h = window.innerHeight;

	inner = Math.min(w, h) * .32;
	outer = inner * 1.08;
	
	
	svg = d3.select("body")
		.append("svg:svg")
		.attr("width", w)
		.attr("height", h)
		.append("svg:g")
		.attr("transform", "translate(" + w / 2 + "," + h / 2 + ")");
	
	chord = d3.layout.chord()
		.padding(.03)
		.sortGroups(d3.descending)
		.sortSubgroups(sortSubgroups)
		.matrix(json.matrix);

	//Draw everything
	addGroups();
	addTicks(json.groups);
	stylePaths();
}

function addGroups() {
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

function addTicks(groups) {
	var boundTicks = groupTicks.bind(null, groups);

	var ticks = svg.append("svg:g")
		.selectAll("g")
		.data(chord.groups)
		.enter().append("svg:g")
		.selectAll("g")
		.data(boundTicks)
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
		.style("stroke", "#666");

	ticks.append("svg:text")
		.attr("x", 8)
		.attr("dy", ".35em")
		.attr("fill", "#666")
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
function groupTicks(groups, d) {
	result = [{
		angle: d.startAngle + ((d.endAngle - d.startAngle) / 2),
		label: groups[d.index]
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

/*
 * Transform a hsv color to rgb
 * accepts parameters
 * h  Object = {h:x, s:y, v:z}
 * OR 
 * h, s, v
*/
function HSVtoRGB(h, s, v) {
	var r, g, b, i, f, p, q, t;

	// Convert from object if necessary
	if (h && s === undefined && v === undefined) {
	    s = h.s, v = h.v, h = h.h;
	}

	i = Math.floor(h * 6);
	f = h * 6 - i;
	p = v * (1 - s);
	q = v * (1 - f * s);
	t = v * (1 - (1 - f) * s);

	switch (i % 6) {
		case 0: r = v, g = t, b = p; break;
		case 1: r = q, g = v, b = p; break;
		case 2: r = p, g = v, b = t; break;
		case 3: r = p, g = q, b = v; break;
		case 4: r = t, g = p, b = v; break;
		case 5: r = v, g = p, b = q; break;
	}

	return "#" + componentToHex(Math.floor(r * 255)) + componentToHex(Math.floor(g * 255)) + componentToHex(Math.floor(b * 255));
}

function componentToHex(color){
	var hex = color.toString(16);
	return hex.length == 1 ? "0" + hex : hex;
}

/**
 * Randomize array element order in-place.
 * Using Fisher-Yates shuffle algorithm.
 */
function shuffleArray(array) {
    for (var i = array.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
    return array;
}

function trigger() {
	reset();
	var edgeFilter = d3.select("#edge-filter").property("value");
	var subNumFilter = d3.select("#subnumber-filter").property("value");
	var subNameFilter = d3.select("#subname-filter").property("value");
	
	filter(edgeFilter, subNameFilter, subNumFilter);

}

function filter(edgeFilter, subNameFilter, subNumFilter) {

	var params = [];
	if(edgeFilter) {
		params.push('edge_value=' + encodeURIComponent(edgeFilter));
	}
	if(subNameFilter) {
		params.push('sub_name=' + encodeURIComponent(subNameFilter));
	}
	if(subNumFilter) {
		params.push('sub_max=' + encodeURIComponent(subNumFilter));
	}

	var form = params.join('&');

	var http = new XMLHttpRequest();
	var url = '/filter';
	http.open('POST', url, true);

	http.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

	http.onreadystatechange = function() {
		if(http.readyState === 4 && http.status === 200) {
			start(JSON.parse(http.responseText));
		}
	};

	http.send(form);
}
