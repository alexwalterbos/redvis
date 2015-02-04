#!/usr/bin/env python
import json
import os.path

def read_results():
	if not os.path.isfile('results.json'):
		print 'No crawling file found! Make sure you run crawler.py first!'
		return {}
	try:
		with open('results.json', 'r') as filestream:
			return json.load(filestream)
	except ValueError:
		print 'Couldn\'t parse crawler file'
		return {}

def write_graph(graph):
	with open('graph.json', 'w') as filestream:
		filestream.write(json.dumps(graph, indent = 4, separators = (',', ': ')))

def get_or_add_node(nodes, subreddit_name):
	if not subreddit_name in nodes:
		nodes[subreddit_name] = { 'id' : subreddit_name, 'label' : subreddit_name }
	
	return nodes[subreddit_name]

def add_or_increment_edge(edge_dict, node1, node2):
	edge = None
	if (node1, node2) in edge_dict:
		edge = edge_dict[(node1, node2)]
	elif (node2, node1) in edge_dict:
		edge = edge_dict[(node2, node1)]
	
	if not edge:
		edge = { 'from' : node1, 'to' : node2, 'value' : 1 }
		edge_dict[(node1, node2)] = edge
	else:
		edge['value'] += 1

	return edge

def construct_graph():
	crawl_results = read_results()
	
	if not crawl_results:
		return
	
	node_dict = {}
	edge_dict = {}

	for user_key in crawl_results:
		user_subs = crawl_results[user_key]
		if '___last_seen' in user_subs:
			del user_subs['___last_seen']

		for subreddit1 in user_subs:
			get_or_add_node(node_dict, subreddit1)
						
			for subreddit2 in user_subs:
				if subreddit1 is subreddit2:
					continue

				get_or_add_node(node_dict, subreddit2)
				add_or_increment_edge(edge_dict, subreddit1, subreddit2)

	# construct empty graph object with nodes and edges
	graph_result = { 'nodes' : node_dict.values(), 'edges' : edge_dict.values() }

	write_graph(graph_result)

	print 'created graph file for ' + str(len(graph_result['nodes'])) + ' subreddits'

if __name__ == '__main__':
	construct_graph()

