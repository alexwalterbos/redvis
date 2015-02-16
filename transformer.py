#!/usr/bin/env python
import json
import os.path
import argparse
import copy
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
		edge = { 'from' : node1, 'to' : node2, 'fromCount' : 1, 'toCount' : 1}
		edge_dict[(node1, node2)] = edge
	else:
		edge['fromCount'] += 1
		edge['toCount'] += 1

def build_nodes(edge_list):
	node_dict = {}
	
	for edge in edge_list:
	
		if edge['from'] not in node_dict:
			node_dict[edge['from']] = {'index' : len(node_dict), 'label' : edge['from']}
		if edge['to'] not in node_dict:
			node_dict[edge['to']] = {'index' : len(node_dict), 'label' : edge['to']}

		edge['from'] = node_dict[edge['from']]['index']
		edge['to'] = node_dict[edge['to']]['index']

	return [ item['label'] for item in sorted(node_dict.values(), key= lambda node : node['index']) ]

# selects edges from edge_list such that the maximum number of subreddits doesn't exceed max_subs
def trim_to_size(edge_list, subreddit, max_subs):
	subs = set()
	trimmed_edge_list = []

	sorted_edges = sorted(edge_list, key= lambda edge : edge['fromCount'], reverse=True)

	# first step filters for all direct relations in 'edge_list' to 'subreddit', with a maximum of 'max_subs'
	for edge in sorted_edges:
		if edge['from'].lower() != subreddit and edge['to'].lower() != subreddit:
			continue

		if len(subs) >= max_subs and not max_subs <= 0:
			break

		subs.add(edge['from'])
		subs.add(edge['to'])
		trimmed_edge_list.append(edge)


	# second step filters subreddits for relations between subreddits that are not 'subreddit'
	for edge in sorted_edges:
		if (edge['from'] in subs and edge['to'] in subs) and not (edge['from'].lower() == subreddit or edge['to'].lower() == subreddit):
			trimmed_edge_list.append(edge)

	return trimmed_edge_list

def normalize_edges(edge_list):
	node_dict = {}
	for edge in edge_list:
		node_from = node_dict.get(edge['from'], 0)
		node_to = node_dict.get(edge['to'], 0)
		
		node_from += edge['fromCount']
		node_to += edge['toCount']

		node_dict[edge['from']] = node_from
		node_dict[edge['to']] = node_to

	for edge in edge_list:
		edge['fromCount'] = edge['fromCount'] / float(node_dict[edge['from']])
		edge['toCount'] = edge['toCount'] / float(node_dict[edge['to']])

def build_matrix(node_list, edge_list):
	size = len(node_list)
	#create size x size empty matrix
	edge_matrix = [[0] * size for i in range(size)]

	for edge in edge_list:
		edge_matrix[edge['from']][edge['to']] = edge['fromCount']
		edge_matrix[edge['to']][edge['from']] = edge['toCount']

	return edge_matrix
def build_edges(crawl_results):
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
	edge_list.sort(key = lambda l: l['fromCount'])
	return edge_list

def construct_graph(edges, filter_min, max_subs, normalize, sub):
	edge_list = copy.deepcopy(edges)
	if filter_min > 1:
		print 'filtering results below ' + str(filter_min)
		edge_list = [edge for edge in edge_list if edge['fromCount'] >= filter_min]

	if not sub:
		#filter for highest connectivity
		sub = edge_list[len(edge_list) - 1]['from']
	else:
		print 'filtering for subreddit ' + str(sub)
	edge_list = trim_to_size(edge_list, sub, max_subs)

	if normalize:
		print 'normalizing results'
		normalize_edges(edge_list)

	node_list = build_nodes(edge_list)

	edge_matrix = build_matrix(node_list, edge_list)

	# construct empty graph object with nodes and edges
	graph_result = { 'groups' : node_list, 'matrix' : edge_matrix }

	print 'created graph file for ' + str(len(graph_result['groups'])) + ' subreddits'
	print 'no. of edges is ' + str(len(edge_list))
	return graph_result

def get_subreddits(crawl_results):
	subs = set()
	for user_key in crawl_results:
		user_subs = crawl_results[user_key]
		if '___last_seen' in user_subs:
			del user_subs['___last_seen']
		for subreddit_key in user_subs:
			subs.add(subreddit_key)
	
	return list(subs)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Transform reddit crawling results into a graphing result for vis.js')
	parser.add_argument('--file', action='store',  default='results.json', help='file to read crawling results from')
	parser.add_argument('--min', action='store', default=1, help='Minumum number of users each relation needs for it to be added to the graph')
	parser.add_argument('--subCount', action='store', default=0, help='Maximum number of subs to include')
	parser.add_argument('--normalize', action='store_true', help='Normalizes the results, making the input of each node the same size')
	parser.add_argument('--sub', action='store', default=None, help='Set a subreddit as a starting point for the selection')
	args = parser.parse_args()
	
	lower_sub = args.sub
	if lower_sub:
		lower_sub.lower()

	print 'reading results'
	results = read_results(args.file)

	graph = construct_graph(results, int(args.min), int(args.subCount), args.normalize, lower_sub)

	print 'writing'
	write_graph(graph)

