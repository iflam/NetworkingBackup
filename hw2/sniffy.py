import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', help='File name to output to')
parser.add_argument('-t', '--timeout', help='Amount of time to capture for before quitting. If no time specified ^C must be sent to close program')
parser.add_argument('-x', '--hexdump', help='Print hexdump to stdout')
parser.add_argument('-f', '--filter', help='Filter for one specific protocol', choices=['UDP','Ethernet','DNS','IP','TCP'])

parser.add_argument('INTERFACE', help='interface to listen for traffic on')

args = parser.parse_args()
