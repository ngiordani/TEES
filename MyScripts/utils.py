import argparse, copy
import xml.etree.cElementTree as ET
from collections import defaultdict

'''
def mergeDependencies(system, gold):
    system_tree = ET.parse(system)
    system_root = system_tree.getroot()

    gold_tree = ET.parse(gold)
    gold_root = gold_tree.getroot()

    deps = {}

   for sd, gd in zip(system_tree.findall("document"), gold_tree.findall("document")):
        for ss, gs in zip(sd.findall("sentence"), gd.findall("sentence")):
            if ss.get("text") != gs.get("text"):
                print "Mismatched sentences:", ss.get("id"), gs.get("id")
                print ss.get("text")
                print gs.get("text")
                continue
        
            [sa, ga] = map(lambda x: x.find("analyses"), [ss, gs])
            [sp, gp] = map(lambda x: x.find("parse"), [sa, ga])
                        
            for dependency in sp.findall("dependency"):
                pass
 
            for dependency in sp.findall("dependency"):
                pass               

            
            for annotation in ss.findall("entity"):
                ss.remove(annotation)
            for annotation in ss.findall("interaction"):
                ss.remove(annotation)
            for annotation in reversed(gs.findall("interaction")):
                ss.insert(0, annotation)
            for annotation in reversed(gs.findall("entity")):
                ss.insert(0, annotation)

    xml.write(args.output)
'''
def getTriggerPOS(args):
    xml = ET.parse(args.input)
    POS = defaultdict(int)
    P = defaultdict(int)
    for d in xml.findall("document"):
        for s in d.findall("sentence"):
            triggerOffsets = set()
            for e in s.findall("entity"):
                if e.get("event") == "True":
                    triggerOffsets.add(e.get("headOffset"))
            a = s.find("analyses")
            tokenization = a.find("tokenization")
            for t in tokenization.findall("token"):
                offset = t.get("charOffset")
                if offset in triggerOffsets:
                    POS[t.get("POS")] += 1
                    P[t.get("POS")[0]] += 1
    print P
    print POS


def __getPath(dependencies, leaf):
    parent = dependencies[leaf]
    antecedents = []
    while parent[1] != 'root':
        antecedents.append(parent)
        parent = dependencies[parent[0]]

    return antecedents
    

def __printFrequencies(d, scale=5):
    keys = sorted(d, key=lambda x:d[x])
    for k in keys:
        print str(k).upper().ljust(30), '|'*(d[k]/scale)


def getPathDistribution(args):
    xml = ET.parse(args.input)
    paths = defaultdict(int)
    pathTypes = defaultdict(int)
    pathLengths = defaultdict(int)
    for d in xml.findall("document"):
        for s in d.findall("sentence"):
            themes = {}
            causes = {}
            entities = {}
            a = s.find("analyses")

            for e in s.findall("entity"):
                entities[e.get("id")] = e.get("headOffset")

            for i in s.findall("interaction"):
                e1 = i.get("e1")
                e2 = i.get("e2")
                if e1 not in entities or e2 not in entities:
                    sid = s.get("id")
                    assert sid not in e1 or sid not in e2
                    continue

                if i.get("type") == "Theme":
                    themes[entities[e1]] = entities[e2]
                elif i.get("type") == "Cause":
                    causes[entities[e1]] = entities[e2]

            p = a.find("parse")
            dependencies = defaultdict(lambda:('ROOT', 'root'))
            offsets = {}
            deps = p.findall("dependency")
            tokenization = a.find("tokenization")
            tokens = tokenization.findall("token")
            for t in tokens:
                offsets[t.get("id")] = t.get("charOffset")

            for d in deps:
                t = d.get("type")
                parent = offsets[d.get("t1")]
                dependent = offsets[d.get("t2")]
                dependencies[dependent] = (parent, t)

            for c in themes:
                ent_antecedents = __getPath(dependencies, themes[c])
                tr_antecedents = __getPath(dependencies, c)

                while ent_antecedents and tr_antecedents and ent_antecedents[-1][0] == tr_antecedents[-1][0]:
                    ent_antecedents.pop()
                    tr_antecedents.pop()

                tr_antecedents.reverse()
                path = ent_antecedents + tr_antecedents
                pathLengths[len(path)] += 1
                for t in path:
                    pathTypes[t[1]] += 1

                path = ','.join([x[1] for x in path])
                paths[path] += 1


    __printFrequencies(pathLengths, scale=10)
    __printFrequencies(pathTypes, scale=10)


def getTypeDistribution(args):
    xml = ET.parse(args.input)
    types = defaultdict(int)
    for d in xml.findall("document"):
        for s in d.findall("sentence"):
            a = s.find("analyses")
            p = a.find("parse")
            deps = p.findall("dependency")
            for d in deps:
                t = d.get("type")
                types[t] += 1

    print types


def unsplitTokenization(args):
    xml = ET.parse(args.input)
    for d in xml.findall("document"):
        for s in d.findall("sentence"):
            a = s.find("analyses")
            tokenization = a.find("tokenization")
            if tokenization == None:
                print "Missing tokenization from sentence", s.get("id")
                continue
            tokens = tokenization.findall("token")

            splitFrom = ""
            newTokens = []
            for t in tokens:
                if "splitFrom" not in t.attrib:
                    t.set("id", "bt_"+str(len(newTokens)))
                    newTokens.append(t)
                    continue

                #deal with splitFrom tokens
                if t.get("splitFrom") != splitFrom:
                    splitFrom = t.get("splitFrom")
                    t.set("charOffset", splitFrom)
                    t.set("id", "bt_"+str(len(newTokens)))
                    newTokens.append(t)
                    del t.attrib["splitFrom"]
                    continue
                else:
                    last = newTokens[-1]
                    last.set("text", last.get("text")+t.get("text"))
                    
            for t in tokens:
                tokenization.remove(t)
            for t in newTokens:
                tokenization.append(t)
                
    xml.write(args.output)


def removeConstituencyParse(args):
    xml = ET.parse(args.input)
    for d in xml.findall("document"):
        for s in d.findall("sentence"):
            a = s.find("analyses")
            parse = a.find("parse")
            if parse == None:
                print "Missing parse from sentence", s.get("id")
                continue
            
            parse.set("pennstring", "(S1 (NN PARSE-FAILED))")
            phrases = parse.findall("phrase")
                        
            for p in phrases:
                parse.remove(p)
            newPhrase = ET.SubElement(parse, "phrase")
            newPhrase.set("begin", "0")
            newPhrase.set("end", "0")
            newPhrase.set("id", "bp_0")
            newPhrase.set("type", "NP")
            #<phrase begin="0" end="0" id="bp_0" type="NP" />

    xml.write(args.output)

def __readMapping(mappingFiles, target):
    mapping = {}
    for m in mappingFiles:
        with open(m) as f:
            for line in f:
                if not target:
                    key, value = line.strip().split()
                else:
                    key = line.strip()
                    value = target
                mapping[key] = value

    return mapping

def substituteDependencyTypes(args):
    xml = ET.parse(args.input)
    mapping = __readMapping(args.mapping, args.target)
    for d in xml.findall("document"):
        for s in d.findall("sentence"):
            a = s.find("analyses")
            parse = a.find("parse")
            if parse == None:
                print "Missing parse from sentence", s.get("id")
                continue
            
            deps = parse.findall("dependency")
            next = len(deps)
                        
            for d in deps:
                label = d.get("type")
                if label in mapping:
                    if args.keepOriginal:
                        original = copy.deepcopy(d)
                        original.set("id", "sd_"+str(next))
                        next += 1
                        parse.append(original)
                    d.set("type", mapping[label])

    xml.write(args.output)



parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers()

parser_trigger = subparsers.add_parser('getPathDistribution')
parser_trigger.add_argument('input')
parser_trigger.set_defaults(func=getPathDistribution)

parser_trigger = subparsers.add_parser('getTriggerPOS')
parser_trigger.add_argument('input')
parser_trigger.set_defaults(func=getTriggerPOS)

parser_trigger = subparsers.add_parser('getTypeDistribution')
parser_trigger.add_argument('input')
parser_trigger.set_defaults(func=getTypeDistribution)

parser_remove = subparsers.add_parser('removeConstituencyParse')
parser_remove.add_argument('input')
parser_remove.set_defaults(func=removeConstituencyParse)
parser_remove.add_argument('--output',  default='test_output.xml',
                   help='Output file')

parser_merge = subparsers.add_parser('unsplitTokenization')
parser_merge.add_argument('input')
parser_merge.set_defaults(func=unsplitTokenization)
parser_merge.add_argument('--output',  default='test_output.xml',
                   help='Output file')

parser_sub = subparsers.add_parser('substituteDependencyTypes')
parser_sub.add_argument('mapping', nargs='+')
parser_sub.add_argument('input')
parser_sub.set_defaults(func=substituteDependencyTypes)
parser_sub.add_argument('--target', help='Target relation')
parser_sub.add_argument('--keepOriginal', action='store_true',
                        help='Whether to keep the original dependencies')
parser_sub.add_argument('--output',  default='test_output.xml',
                   help='Output file')


args = parser.parse_args()
args.func(args)
