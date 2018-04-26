I put little comments and some print statements in some syscalls to see what they do, so find those. they are the simple ones like open create read, readdir, etc. 

I was also thinking about how to have node and fusepy talk... I was thinking we can fork node and exec the fusepy file, and then communicate via a pipe so whenever fuse wants to do something, it pauses, sends something back to node saying "hey get me this from bootstrap", and then node will contact bootstrap etc, but that way fusepy only does lower-level and node deals with upper-level.
Any other ideas?