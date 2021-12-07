# README


# High-level approach:

We started this assignment by reviewing the raft implementation document. From here we followed the suggested step for our raft implementation.


# Challenges Faced:

The greatest challenge we faced for this milestone was with the leader election. Since it is possible to receive put or get requests while an election is in progress,
we had difficulty determing how to store these messages before dealing with them. Testing our functionality was also a challenge. 
Usually a test would run without issue, but occasionally we would get unanswered requests or errors. As a result we would run each test multiple times.

# Overview of testing:

We tested our code by running provided sim with files from the test directory. 