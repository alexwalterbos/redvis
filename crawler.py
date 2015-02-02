#!/usr/bin/env python
import json
import praw 
import os.path
import sys
from functools import partial
from requests.exceptions import HTTPError

# puts the final results in a json file
def write_results(post_results):
	with open('results.json', 'w') as filestream:
		filestream.write(json.dumps(post_results, indent = 4, separators = (',', ': ')))

# Read results from file
def read_results():
	if not os.path.isfile('results.json'):
		return {}

	try:
		with open('results.json', 'r') as filestream:
			return json.load(filestream)
	except ValueError:
		print 'Could not read old results, returning empty'
		return {}

# Handle a reddit comment
def comment_handler(comment, post_results):
	user_name = comment.author.name

	sys.stdout.write("\r\x1b[KParsing user %s" % (user_name) )
	sys.stdout.flush()

	# If the user does not exist, get comment history
	post_results[user_name] = post_results.get(user_name, {})
	last_seen = post_results[user_name].get("___last_seen", None)
	
	for user_comment in comment.author.get_comments(limit=100):
		if user_comment.id is last_seen:
			break
		# Get comment array per user per sub
		comments_per_sub = post_results[user_name].get(user_comment.subreddit.display_name, [])
		# Append comment id to comment per sub array
		comments_per_sub.append(user_comment.id)
		post_results[user_name][user_comment.subreddit.display_name] = comments_per_sub
		
	post_results[user_name]["___last_seen"] = comment.id

# create_agent constructs a thread-safe praw agent to be used by each process
def create_agent():
	user_agent = "Reddit graph crawler data visualization"
	return praw.Reddit(user_agent=user_agent)

if __name__ == '__main__':
	# Read previous results (if any) from file
	post_results = read_results()

	try:
		reddit = create_agent()

		partial_comment_handler = partial(comment_handler, post_results=post_results)

		# Crawl the reddit stream for new posts
		all_stream = praw.helpers.comment_stream(reddit, 'all', limit=None, verbosity=0)
		
		while True:
			try:
				# Pass each comment from the /r/all stream to the comment handler
				map(partial_comment_handler, all_stream)
			except HTTPError:
				pass


	except KeyboardInterrupt:
		print '\nCancelled by user'
	finally:
		print '\nLogging results...'
		write_results(post_results)
		print 'Finished'
