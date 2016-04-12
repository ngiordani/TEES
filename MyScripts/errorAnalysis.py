import sys
from bootstrap import getDocEvals
from collections import defaultdict

allEvals = defaultdict(dict)

for filename in sys.argv[1:]:
    evals = getDocEvals(filename)
    for doc in evals:
        allEvals[doc][filename] = evals[doc]

print '\t'.join(["document"]+map(lambda x: x.split('/')[2], sys.argv[1:]))

for doc in allEvals:
    matches = [allEvals[doc][filename]["answer_match"] for filename in allEvals[doc]]
    highest = max(matches)
    lowest =  min(matches)
    if highest == lowest:
        continue
    for i, match in enumerate(matches):
        matches[i] = str(match)
        if match == highest:
            matches[i] += "++"
        if match == lowest:
            matches[i] += "--"

    print '\t\t\t'.join([str(doc)]+matches)
    
