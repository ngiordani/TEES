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

    print "baseline mean:", baselineMean
    print "system mean:", systemMean
    difference = systemMean - baselineMean
    print "difference:", difference
    
    if not iterations > 0:
        return "Not estimated"
    
    count = 0
    docs = list(baseline.keys())
    docsLength = len(baseline)

    for i in xrange(0, iterations):
        sys.stdout.write('\r'+str(i))
        sys.stdout.flush()
        sample = getSample(sampleSize, docsLength, docs)
        baselineScore = getScore(sample, baseline)
        systemScore = getScore(sample, system)

        if systemScore - baselineScore > 2*difference:
            count += 1

    print ""

    print "Found difference larger than 2 * mean difference in", count, "out of", iterations, "bootstrapped samples."
    return count / iterations


def getDocEvals(filenames):
    docEvals = {}
    for filename in filenames:
        with open(filename) as f:
            f.readline()
            for line in f:
                doc, answer, answer_match, gold, fscore = line.strip().split(',')
                scores = {"answer":float(answer), "answer_match":float(answer_match), "gold":float(gold)}
                assert doc not in docEvals
                docEvals[doc] = scores
                
    return docEvals


def getSample(sampleSize, numDocs, docs):
    sample = []
    for i in xrange(0, sampleSize):
        sample.append(docs[random.randint(0, numDocs-1)])

    return sample


def getScore(sample, docEvals, metric="fscore"):
    total_answer = sumOverCriterion(sample, docEvals, "answer")
    total_answer_match = sumOverCriterion(sample, docEvals, "answer_match")
    total_gold = sumOverCriterion(sample, docEvals, "gold")

    metrics = {}

    metrics["precision"] = total_answer_match / total_answer
    metrics["recall"] = total_answer_match / total_gold
    metrics["fscore"] = 2 * (metrics["precision"] * metrics["recall"]) / (metrics["precision"] + metrics["recall"])

    return metrics[metric]


def sumOverCriterion(sample, docEvals, criterion):
    return sum([docEvals[x][criterion] for x in docEvals if not sample or x in sample])


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Perform a paired bootstrap test.')
    parser.add_argument("--aggregate", nargs='+')
    parser.add_argument("--compareTo", nargs='+')
    parser.add_argument("--baseline", nargs="+")
    parser.add_argument("--system", nargs="+")
    parser.add_argument("-i", "--iterations", default=10000, type=int)
    args = parser.parse_args()

    if args.aggregate:
        evals = getDocEvals(args.aggregate[:-1])
        agg = getScore([], evals, args.aggregate[-1])
        if args.compareTo:
            baseline = getDocEvals(args.compareTo)
            assert set(baseline.keys()) == set(evals.keys()), "\nBaseline: {} \nBaseline size:{}\n\nSystem:{}\nSystem size:{}".format(baseline.keys(), len(baseline.keys()), evals.keys(), len(evals.keys()))
            baseline = getScore([], baseline, args.aggregate[-1])
            agg -= baseline
        print "{:6.3f}".format(agg)
        sys.exit()


    baseline = getDocEvals(args.baseline)
    system = getDocEvals(args.system)

    assert set(baseline.keys()) == set(system.keys())

    sampleSize = len(system)
    
    p = getPValue(baseline, system, args.iterations, sampleSize)
    print "Estimated p-value:", p

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
