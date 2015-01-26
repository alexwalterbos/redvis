#!/usr/bin/env python
import signal
import json
import praw 
import threading 
import os.path
import Queue
from functools import partial
from multiprocessing import Process
from praw.handlers import MultiprocessHandler

#helper class for unique 
class SetQueue(Queue.Queue):

    def _init(self, maxsize):
        self.maxsize = maxsize
        self.queue = set()

    def _put(self, item):
        self.queue.add(item)

    def _get(self):
        return self.queue.pop()

def comment_handler(results_out, queue, active, lock, comment):
	user_name = comment.author.user_name
	
	with lock:
		if author in results_out:
			update_sub_post(user_name, post)
		elif author not in active:
			queue.put(user_name)

def update_sub_post(author, post):
	user_posts = self.post_results[author]
	sub_post_count = user_posts.get(post.subreddit, 0)
	user_posts[post.subreddit] = sub_post_count

def user_handler(results, queue, active, lock):
	reddit = create_agent()

	while True:
		username = queue.get()
		active.put(username)

		user = reddit.get_redditor(username)
		user_comments = {}
		for comment in user.get_comments(limit=None):
			subreddit = comment.subreddit.display_name
			user_comments[subreddit] = user_comments.get(subreddit, 0) + 1

		with lock:
			results[username] = user_comments
			active.remove(username)

# puts the final results in a json file
def write_results(post_results):
	with open('results.json', 'w') as f:
		f.write(json.dumps(post_results))

def read_results():
	if not os.path.isfile('results.json'):
		return {}

	with open('results.json', 'r') as f:
		return json.load(f)

# create_agent constructs a thread-safe praw agent to be used by each process
def create_agent():
	user_agent = "Reddit graph crawler data visualization by /u/alpacalex"
	handler = MultiProcessHandler()
	return praw.reddit(user_agent=user_agent, handler=handler)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, signal.SIG_IGN)
	
	post_results = read_results()
	processes = []

	try:
		queue = SetQueue(maxsize=1000)
		active = []
		lock = threading.RLock()

		partial_handler = partial(comment_handler, results=post_results, queue=queue, active=active, lock = lock)

		#start processes for user crawling
		for x in range(4):
			p = Process(target=user_handler, args=(post_results, queue, active, lock))
			p.start()
			processes.append(p)

		reddit = create_agent()

		#crawl the reddit stream for new posts
		all_stream = praw.helpers.comment_stream(reddit, 'all', limit=None)
		map(comment_crawler, all_stream)

	except KeyboardInterrupt:
		print 'comment crawling cancel requested'
		print 'killing running jobs'
		for p in processes:
			p.terminate()
	finally:
		print 'finalizing jobs'
		for p in processes:
			p.join()

		print 'logging results...'
		write_results(post_results)
