#!/usr/bin/env python
import json
import os.path
import argparse
import collections

def read_results(file_name):
	if not os.path.isfile(file_name):
		print 'No graph data file found! Make sure you run crawler.py and transformer.py first!'
		return {}
	try:
		with open(file_name, 'r') as filestream:
			return json.load(filestream)
	except ValueError:
		print 'Couldn\'t parse crawler file'
		return {}

def write_stats(stats):
	with open('stats.json', 'w') as filestream:
		filestream.write(json.dumps(stats, indent = 4, separators = (',', ': ')))

def increment_value_frequency(edge_hist, value):
	if value not in edge_hist:
		edge_hist[value] = 1
	else:
		edge_hist[value] += 1

def get_threshold(odict, max_edge):
	cumulative = 0
	for k, v in odict.items():
		cumulative += v
		if cumulative >= max_edge:
			return k

	return -1

def extract_stats(file_name, max_edge):
	print 'reading results'
	graph = read_results(file_name)

	if not graph:
		return

	print 'processing results'
	edge_hist = {}	

	edge_list = graph['edges']

	for edge in edge_list:
		increment_value_frequency(edge_hist, edge['value'])

	od = collections.OrderedDict(sorted(edge_hist.items(), reverse=True))

	threshold = get_threshold(od, max_edge)

	if threshold == -1:
		print 'No threshold found for ' + str(max_edge) + '. You can use all data.'
	else:
		print 'Threshold for about ' + str(max_edge) + ' edges is edge value ' + str(threshold)

	print 'writing results'
	write_stats(od)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Transform graph data into statistical data')
	parser.add_argument('--file', action='store', default='graph.json', help='file to read graph data from')
	parser.add_argument('--max_edge', action='store', default='5000', help='Desired maximal amount of edges')
	args = parser.parse_args()
	
	extract_stats(args.file, int(args.max_edge))
