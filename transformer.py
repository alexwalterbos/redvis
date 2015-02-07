#!/usr/bin/env python
import json
import os.path
import argparse
from functools import partial

def read_results(file_name):
	if not os.path.isfile(file_name):
		print 'No crawling file found! Make sure you run crawler.py first!'
		return {}
	try:
		with open(file_name, 'r') as filestream:
			return json.load(filestream)
	except ValueError:
		print 'Couldn\'t parse crawler file'
		return {}

def write_graph(graph):
	with open('graph.json', 'w') as filestream:
		filestream.write(json.dumps(graph, indent = 4, separators = (',', ': ')))

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

def build_nodes(edge_list):
	node_dict = {}
	for edge in edge_list:
		sub1 = edge['from']
		sub2 = edge['to']

		if sub1 not in node_dict:
			node_dict[sub1] = {'index' : len(node_dict), 'label' : sub1}
		if sub2 not in node_dict:
			node_dict[sub2] = {'index' : len(node_dict), 'label' : sub2}

		edge['from'] = node_dict[sub1]['index']
		edge['to'] = node_dict[sub2]['index']
		
	return node_dict.values()

# selects edges from edge_list such that the maximum number of subreddits doesn't exceed max_subs
def trim_to_size(edge_list, max_subs):
	subs = set()
	trimmed_edge_list = []
	
	for edge in edge_list:
		if len(subs) >= max_subs and (edge['from'] not in subs or edge['to'] not in subs):
			continue

		subs.add(edge['from'])
		subs.add(edge['to'])
		trimmed_edge_list.append(edge)
	
	return trimmed_edge_list


def build_matrix(node_list, edge_list):
	size = len(node_list)
	#create size x size empty matrix
	edge_matrix = [[0] * size for i in range(size)]

	for edge in edge_list:
		edge_matrix[edge['from']][edge['to']] = edge['value']
		edge_matrix[edge['to']][edge['from']] = edge['value']

	return edge_matrix

def construct_graph(file_name, filter_min, max_subs):
	crawl_results = read_results(file_name)
	
	if not crawl_results:
		return
	
	edge_dict = {}

	for user_key in crawl_results:
		user_subs = crawl_results[user_key]
		if '___last_seen' in user_subs:
			del user_subs['___last_seen']

		for subreddit1 in user_subs:
			for subreddit2 in user_subs:
				if subreddit1 is subreddit2:
					continue

				add_or_increment_edge(edge_dict, subreddit1, subreddit2)

	edge_list = edge_dict.values()
	edge_list.sort(key = lambda l: l['value'])

	if filter_min > 1:
		print 'filtering results below ' + str(filter_min)
		edge_list = [edge for edge in edge_list if edge['value'] >= filter_min]

	if max_subs > 0:
		print 'limiting amount of subs to ' + str(max_subs)
		edge_list = trim_to_size(edge_list, max_subs)

	node_list = build_nodes(edge_list)

	edge_matrix = build_matrix(node_list, edge_list)

	# construct empty graph object with nodes and edges
	graph_result = { 'groups' : node_list, 'matrix' : edge_matrix }

	print 'created graph file for ' + str(len(graph_result['groups'])) + ' subreddits'
	print 'no. of edges is ' + str(len(edge_list))

	print 'writing'
	write_graph(graph_result)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Transform reddit crawling results into a graphing result for vis.js')
	parser.add_argument('--file', action='store',  default='results.json', help='file to read crawling results from')
	parser.add_argument('--min', action='store', default=1, help='Minumum number of users each relation needs for it to be added to the graph')
	parser.add_argument('--subs', action='store', default=0, help='Maximum number of subs to include')
	args = parser.parse_args()

	construct_graph(args.file, int(args.min), int(args.subs))

