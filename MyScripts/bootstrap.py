#!/u/nlp/packages/anaconda/bin/python

from __future__ import division
import argparse
import sys
import random
import math
import numpy as np

def getPValue(baseline, system, iterations, sampleSize):
    baselineMean = getScore([], baseline)
    systemMean = getScore([], system)

    if systemMean < baselineMean:
        temp = baseline
        tempMean = baselineMean
        baseline = system
        baselineMean = systemMean
        system = temp
        systemMean = tempMean

    difference = systemMean - baselineMean
    if args.verbose:
        print "baseline mean:", baselineMean
        print "system mean:", systemMean
        print "difference:", difference
    
    if not iterations > 0:
        return "Not estimated"
    
    count = 0
    #docs = list(baseline.keys())
    docsLength = baseline.shape[0]

    for i in xrange(0, iterations):
        if args.verbose:
            sys.stdout.write('\r'+str(i))
            sys.stdout.flush()
        sample = np.random.choice(docsLength, docsLength, replace=True)
        baselineScore = getScore(sample, baseline)
        systemScore = getScore(sample, system)

        if systemScore - baselineScore > 2*difference:
            count += 1

    if args.verbose:
        print ""
        print "Found difference larger than 2 * mean difference in", count, "out of", iterations, "bootstrapped samples."
    return count / iterations


def getDocEvals(filenames):
    arrays = []
    docEvals = {}
    for filename in filenames:
        results = np.genfromtxt(filename, delimiter=',', skip_header=1, dtype=int)
        arrays.append(results)
#        with open(filename) as f:
#            f.readline()
#            for line in f:
#                doc, answer, answer_match, gold, fscore = line.strip().split(',')
#                scores = {"answer":float(answer), "answer_match":float(answer_match), "gold":float(gold)}
#                assert doc not in docEvals
#                docEvals[doc] = scores

    matrix = np.vstack(tuple(arrays))
    matrix = matrix[matrix[:,0].argsort()]

    return matrix
#    return docEvals


#def getSample(sampleSize, numDocs):
#    return 

#    sample = np.zeros(sampleSize)
#    for i in xrange(0, sampleSize):
#        sample.append(docs[random.randint(0, numDocs-1)])
#        sample.append(random.randint(0, numDocs-1))
#        sample[random.randint(0, numDocs-1)] += 1

#    return sample


def getScore(sample, docEvals, metric="fscore"):
    criteria = {"doc":0, "answer":1, "answer_match":2, "gold":3, "fscore":4}
    total_answer = sumOverCriterion(sample, docEvals, criteria["answer"])
    total_answer_match = sumOverCriterion(sample, docEvals, criteria["answer_match"])
    total_gold = sumOverCriterion(sample, docEvals, criteria["gold"])

    metrics = {}

    metrics["precision"] = total_answer_match / total_answer
    metrics["recall"] = total_answer_match / total_gold
    metrics["fscore"] = 2 * (metrics["precision"] * metrics["recall"]) / (metrics["precision"] + metrics["recall"])

    return metrics[metric]


def sumOverCriterion(sample, docEvals, criterion):
#    if not sample:
#        sample = range(0, docEvals.shape[0])
    sampled = docEvals[:,criterion]
    if sample != []:
        sampled = np.multiply(sample, sampled)

    return np.sum(sampled)
#    return sum([docEvals[x,criterion] for x in sample])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Perform a paired bootstrap test.')
    parser.add_argument("--aggregate", nargs='+')
    parser.add_argument("--compareTo", nargs='+')
    parser.add_argument("--baseline", nargs="+")
    parser.add_argument("--system", nargs="+")
    parser.add_argument("-i", "--iterations", default=10000, type=int)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if args.aggregate:
        evals = getDocEvals(args.aggregate[:-1])
        agg = getScore([], evals, args.aggregate[-1])

        if args.compareTo:
            baseline = getDocEvals(args.compareTo)
            comparison = baseline[:,0] == evals[:,0]
            assert all(comparison), comparison

            baseline = getScore([], baseline, args.aggregate[-1])
            agg -= baseline
        print "{:6.4f}".format(agg*100)
        sys.exit()


    baseline = getDocEvals(args.baseline)
    system = getDocEvals(args.system)

    comparison = baseline[:,0] == system[:,0]
    assert all(comparison), comparison
    #assert set(baseline.keys()) == set(system.keys())

    sampleSize = len(system)
    
    p = getPValue(baseline, system, args.iterations, sampleSize)

    if args.verbose: print "Estimated p-value:"
    print p

'''
    baseline_better = {}
    system_better = {}
    for doc in baseline:
        baseline_matches = baseline[doc]["answer_match"] / max(1.0, baseline[doc]["answer"])
        system_matches = system[doc]["answer_match"] / max(1.0, system[doc]["answer"])
        if baseline_matches != system_matches:
        #print "Document {} has {} answer_match in first classifier and {} in second".format(doc, baseline_matches, system_matches)
            if baseline_matches > system_matches:
                baseline_better[doc] = baseline_matches - system_matches
            else:
                system_better[doc] = system_matches - baseline_matches

    print "First argument (baseline) is better on", len(baseline_better), "documents:"
#    baseline_better = sorted(baseline_better)
    for doc in baseline_better:
        print doc, "diff:", baseline_better[doc]
        
    print "First argument (system) is better on", len(system_better), "documents:"
#    system_better = sorted(system_better)
    for doc in system_better:
       print doc, "diff:", system_better[doc]
'''
