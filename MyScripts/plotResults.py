from matplotlib import pyplot as plt
from collections import defaultdict
import argparse

parser = argparse.ArgumentParser(description='Plot results')
parser.add_argument('values', help='''File with values in expected format: 
1-line title for representation, followed by one line per fold of results: 
Recall Precision F-Score, space-separated.''')
parser.add_argument('--filter', nargs='+', help="Matches to be plotted")
parser.add_argument('--metrics', nargs='+',  default=["fscore"], help="Metrics to plot")

args = parser.parse_args()

lines = []
with open(args.values) as f:
    lines= f.readlines()

results = defaultdict(lambda: defaultdict(list))
label = ""
dir = ""

sieve = args.filter

for line in lines:
    if not line.strip():
        continue

    if '/' in line:
        dir = line.strip()
        folder, group, rep  = dir.split('/')
        data = folder.split('-')[0]
        label = (group, rep)
        continue

    if sieve and all([x not in dir for x in sieve]):
        print "Skipping", dir
        continue

    recall, precision, fscore = map(float, line.strip().split())
    results[label]["precision"].append(precision)
    results[label]["recall"].append(recall)
    results[label]["fscore"].append(fscore)

#markers = {'GE11':'o', 'GE09':'*'}

width = defaultdict(lambda:1.0)
width['basicUD'] = 3.0

style = defaultdict(lambda: "solid")
style['trivial'] = 'dotted'
style['untyped_basicUD'] = 'dotted'

markers = {'fscore':'o', 'precision':'x', 'recall':'*'}

for lbl in results:
    group, rep = lbl
    print rep
    for metric in args.metrics:        
        plt.plot(results[lbl][metric], label="F "+rep, lw=width[rep], ls=style[rep], marker=markers[metric])

plt.legend(fontsize=10, loc=2)
x = max([len(results[x]["fscore"]) for x in results])
plt.axis([-1,x,10,90])
plt.gca().yaxis.grid(True)
plt.show()
