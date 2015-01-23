#!/usr/bin/env python
import Queue
import threading
import time
import signal
import sys
import json
import praw 
from praw.handlers import MultiProcessHandler

should_stop = [False]
queue = Queue.Queue()
post_results = {}

class PostGrabber(threading.Thread):
	def __init__(self, queue, user_results):
		threading.Thread.__init__(self)

		self.queue = queue
		self.post_results = post_results
		self.reddit = create_agent()		

	def run(self):
		global should_stop
		while True and not should_stop[0]:
			#grabs host from queue
			post = self.queue.get()
			
			author = post.author.user_name

			if author in self.post_results:
				update_sub_post(author, post)
			else
				grab_user_posts(author)

			#signals to queue job is done
			self.queue.task_done()

	def update_sub_post(author, post):
		user_posts = self.post_results[author]
		sub_post_count = user_posts.get(post.subreddit, 0)
		user_posts[post.subreddit] = sub_post_count

	def grab_user_posts(user):
		#grab stuff
		
class NewWatcher(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue
		self.reddit = create_agent()

	def run(self):
		global should_stop
		while True and not should_stop[0]:
			#grab new posts

			

#not thread-safe. no jobs should be running when calling this
def write_results:
	global post_results
	f.open('results.json', 'w')
	f.write(json.dumps(post_results))
	f.close()

def finalize(signal, frame):
	global should_stop
	global queue

	#if we've been called to stop while waiting for current job to finish, just kill everything
	if should_stop[0] is True:
		sys.exit(0)
		return

	should_stop[0] = True
	print "Dropping queued jobs"
	#blame python for not giving an easy way to clear queues
	while not queue.empty():
		queue.get()
		queue.task_done()
	
	print "Waiting for running job to complete"
	queue.join()
	print "Thread returned. Writing results to results.json"
	write_results()
	print "Exiting..."
	sys.exit(0)

def create_agent():
	user_agent = "Reddit graph crawler data visualization"
	handler = MultiProcessHandler()
	self.reddit = praw.reddit(user_agent=user_agent, handler=handler)

if __name__ == '__main__':
	signal.signal(signal.SIGINT, finalize)

	new_queue = NewWatcher(queue)
	post_grabber = PostGrabber(queue, post_results)

	new_queue.start()
	post_grabber.start()

