#!/u/nlp/packages/anaconda/bin/python

from __future__ import division
import argparse
import sys
import random
import math

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
    
    count = 0
    
    for i in xrange(0, iterations):
        sample = getSample(sampleSize, len(baseline))
        baselineScore = getScore(sample, baseline)
        systemScore = getScore(sample, system)
#        print "baseline:{}, system:{}".format(baselineScore, systemScore)
        if systemScore - baselineScore > 2*difference:
            count += 1
#            print "adding"

    print "Found difference larger than 2 * mean difference in", count, "out of", iterations, "bootstrapped samples."
    return count / iterations


def getDocEvals(filename):
    docEvals = {}
    with open(filename) as f:
        f.readline()
        for line in f:
            doc, answer, answer_match, gold, fscore = map(float, line.strip().split(','))
            scores = {"answer":answer, "answer_match":answer_match, "gold":gold}
            docEvals[int(doc)] = scores

    return docEvals


def getSample(sampleSize, numDocs):
    sample = []
    for i in xrange(0, sampleSize):
        sample.append(random.randint(0, numDocs-1))

    return sample


def getScore(sample, docEvals):
    total_answer = sumOverCriterion(sample, docEvals, "answer")
    total_answer_match = sumOverCriterion(sample, docEvals, "answer_match")
    total_gold = sumOverCriterion(sample, docEvals, "gold")

    precision = total_answer_match / total_answer
    recall = total_answer_match / total_gold
    fscore = 2 * (precision * recall) / (precision + recall)

    return fscore


def sumOverCriterion(sample, docEvals, criterion):
    return sum([docEvals[x][criterion] for x in docEvals if not sample or x in sample])


if __name__ == "__main__":


    baseline = getDocEvals(sys.argv[1])
    system = getDocEvals(sys.argv[2])

    assert baseline.keys() == system.keys()

    baseline_better = set()
    system_better = set()
    for doc in baseline:
        baseline_matches = baseline[doc]["answer_match"]
        system_matches = system[doc]["answer_match"]
        if baseline_matches != system_matches:
        #print "Document {} has {} answer_match in first classifier and {} in second".format(doc, baseline_matches, system_matches)
            if baseline_matches > system_matches:
                baseline_better.add(doc)
            else:
                system_better.add(doc)

    print "First argument (baseline) is better on", len(baseline_better), "documents:"
    baseline_better = sorted(baseline_better)
    for doc in baseline_better:
        print doc
        
    print "First argument (system) is better on", len(system_better), "documents:"
    system_better = sorted(system_better)
    for doc in system_better:
        print doc

    iterations = int(sys.argv[3])
    sampleSize = len(system)
    
    p = getPValue(baseline, system, iterations, sampleSize)
    print "Estimated p-value:", p

