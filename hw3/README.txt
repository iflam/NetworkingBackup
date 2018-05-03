~README~

How to run Bootstrap:
python bootstrap.py
Optional arg: -p to specify port to listen on (default port is 1234)

How to run nodes:
python node.py -ip [ip of bootstrap] 
Optional: -p port bootstrap is listening on (default is 1234)
Optional: -m mount directory (default is mnt, creates if doesn't exist)

There's a lot of debugging info printed in both node and bootstrap that shows connections and what's being called

Both node and bootstrap have a little shell where you can type in the name of any global variable to see its current value
E.g:
bootstrap> nodes
[list of nodes connected]
bootstrap> files
{dict of files to locations}
bootstrap> sock
<socket bootstrap is listening on>
client> listen_sock
<socket node is listening on>

You can ctrl+c from bootstrap to kill all nodes, or from each node separately as well.