d3.json('graph.json', function(error, json) {
	var chord = d3.layout.chord()
	  .padding(.05)
	  .sortSubgroups(d3.descending)
	  .matrix(json.matrix);

	var w = 1200,
	    h = 1200,
	    r0 = Math.min(w, h) * .41,
	    r1 = r0 * 1.1;

	var fill = d3.scale.ordinal()
	    .domain(d3.range(4))
	    .range(["#000000", "#FFDD89", "#957244", "#F26223"]);

	var svg = d3.select("#chart")
	  .append("svg:svg")
	    .attr("width", w)
	    .attr("height", h)
	  .append("svg:g")
	    .attr("transform", "translate(" + w / 2 + "," + h / 2 + ")");

	svg.append("svg:g")
	  .selectAll("path")
	    .data(chord.groups)
	  .enter().append("svg:path")
	    .style("fill", '#000000')
	    .style("stroke", '000000')
	    .attr("d", d3.svg.arc().innerRadius(r0).outerRadius(r1))
	    .on("mouseover", fade(.1))
	    .on("mouseout", fade(1));

//	var ticks = svg.append("svg:g")
//	  .selectAll("g")
//	    .data(chord.groups)
//	  .enter().append("svg:g")
//	  .selectAll("g")
//	    .data(groupTicks)
//	  .enter().append("svg:g")
//	    .attr("transform", function(d) {
//	      return "rotate(" + (d.angle * 180 / Math.PI - 90) + ")"
//		  + "translate(" + r1 + ",0)";
//	    });
//
//	ticks.append("svg:line")
//	    .attr("x1", 1)
//	    .attr("y1", 0)
//	    .attr("x2", 5)
//	    .attr("y2", 0)
//	    .style("stroke", "#000");
//
//	ticks.append("svg:text")
//	    .attr("x", 8)
//	    .attr("dy", ".35em")
//	    .attr("text-anchor", function(d) {
//	      return d.angle > Math.PI ? "end" : null;
//	    })
//	    .attr("transform", function(d) {
//	      return d.angle > Math.PI ? "rotate(180)translate(-16)" : null;
//	    })
//	    .text(function(d) { return d.label; });
//
//	svg.append("svg:g")
//	    .attr("class", "chord")
//	  .selectAll("path")
//	    .data(chord.chords)
//	  .enter().append("svg:path")
//	    .style("fill", function(d) { return fill(d.target.index); })
//	    .attr("d", d3.svg.chord().radius(r0))
//	    .style("opacity", 1);
//
//	/** Returns an array of tick angles and labels, given a group. */
//	function groupTicks(d) {
//	  var k = (d.endAngle - d.startAngle) / d.value;
//	  return d3.range(0, d.value, 1000).map(function(v, i) {
//	    return {
//	      angle: v * k + d.startAngle,
//	      label: i % 5 ? null : v / 1000 + "k"
//	    };
//	  });
//	}

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
});
