RedVis; Reddit Visualized
======
A between-subreddit activity visualization tool.

## Project goal
The goal of this project is to visualize the relationship between subreddits on the online forum www.reddit.com.
We will focus on relationships between subreddits.
Several types of relations can be distinguished:
* User activity: A user that is active in two subreddits defines a relationship between these subreddits.
* X-Posting: Content is posted in multiple subreddits (same question, same url).
* Referral in comments: "Shout out to /r/thisothersub".

This visualization is intended to show characteristics of the userbase and subreddits, by showing related interests (based on the subreddits), and perhaps size of (overlapping) user communities in a later stage.

## Tools
We intend to use the [vis.js Graph visualization tool](http://visjs.org/docs/graph.html).
This library provides an easy way of setting up a node graph to display the relations we want to visualize.

### Languages
Reddit provides an [API](https://github.com/reddit/reddit/wiki/API) and a [Python interface](https://github.com/reddit/reddit/blob/master/r2/r2/controllers/api.py) for it.
This handy tool has driven us to our choice to use Python for data gathering and processing.

For the website, we will, predictably, use HTML, CSS and JavaScript.

## Deliverable
The deliverable for this project will be the graphing tool.
It will be provided via a web interface.
It should be interactive; the user should be able to zoom in on relations, selecting and focussing on subreddits.
The user must also be able to search a subreddit (by name, and if available) and select it as the root node for the graph.
