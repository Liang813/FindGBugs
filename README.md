# FindGBugs
This project consists of two main parts, the first department is bugs_crawler and the second part is bugs_mining.

## bugs_crawler
The files in this folder are used for crawling, and they all end up fetching bugs in the form of <issue, commit>.

* oneRepoIWC.py

  This .py file is based on the full name of the repo to do the crawl only for this repo.


* getIWC.py

  This .py file does a query based on the keywords entered and does a crawl of all the repo's that are queried.

## bugs_mining
This part is to propose a set of automated ways to dig the General Bug from the bugs obtained by the crawler above.It mainly uses python's abstract syntax tree. Based on the abstract syntax tree, a rule-based approach is used to mine the General Bug.
You need to run `clone_repo.py` to clone the Github repo to your own local before digging into the General Bug.
`update_nodes.py` is the starting position for digging the General Bug.