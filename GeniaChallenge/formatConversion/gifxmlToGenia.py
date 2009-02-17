import InteractionXML.CorpusElements as CorpusElements
import sys, os, shutil
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/../../JariSandbox/ComplexPPI/Source")
from Utils.ProgressCounter import ProgressCounter
import Range
from optparse import OptionParser

def getEntityIndex(entities, index=0):
    origIds = []
    for entity in entities:
        origId = entity.get("origId")
        if origId != None:
            origIds.append(origId)
    for origId in origIds:
        idPart = origId.split(".")[-1]
        assert(idPart[0] == "T")
        newIndex = int(idPart[1:])
        if newIndex > index:
            index = newIndex
    return index

def processCorpus(inputCorpus, outputFolder):
    counter = ProgressCounter(len(inputCorpus.documents), "Document")
    # Each document is written to an output file
    for document in inputCorpus.documents:
        documentId = document.find("sentence").get("origId").split(".")[0]
        outputFile = open(os.path.join(outputFolder,documentId + ".a2"), "wt")
        counter.update()
        
        writeEventTriggers(document, inputCorpus, outputFile)
        findThemeCausePairs(document, inputCorpus)
        makeEvents(document, inputCorpus, outputFile)
        
        outputFile.close()

def writeEventTriggers(document, inputCorpus, outputFile):
    entityIndex = 0
    # Find new entity index
    for sentenceElement in document.findall("sentence"):
        sentence = inputCorpus.sentencesById[sentenceElement.get("id")]
        entityIndex = getEntityIndex(sentence.entities, entityIndex)
    # Write entities
    offsetMap = {}
    entityIndex += 1
    for sentenceElement in document.findall("sentence"):
        sentence = inputCorpus.sentencesById[sentenceElement.get("id")]
        sentenceOffset = Range.charOffsetToSingleTuple(sentenceElement.get("charOffset"))
        for entity in sentence.entities:
            if entity.get("isName") == "False":
                entityOffset = Range.charOffsetToSingleTuple(entity.get("charOffset"))
                newOffset = [entityOffset[0] + sentenceOffset[0], entityOffset[1] + sentenceOffset[1]]
                match = Range.tuplesToCharOffset(newOffset) + "_" + entity.get("type")
                if match in offsetMap.keys():
                    entity.set("temp_newId", offsetMap[match].get("temp_newId"))
                else:
                    newId = "T" + str(entityIndex)
                    entity.set("temp_newId", newId)
                    outputFile.write( newId + "\t" + entity.get("type") + " " + str(newOffset[0]) + " " + str(newOffset[1]) + "\t" + entity.get("text") + "\n" )
                    offsetMap[match] = entity
                    entityIndex += 1
            else:
                entity.set("temp_newId", entity.get("origId").split(".")[-1])

def writeEvents(document, inputCorpus, outputFile):
    """
    Writes events defined as trigger words that have one or more interactions
    leaving from them. When the Theme or Cause of such an event refers to a
    trigger that is also an event, the Theme or Cause will point to that event (E).
    Note that even if the Theme or Cause is an event-trigger, if that trigger
    has no defined interactions, it will be annotated as trigger (T), not as 
    a nested event (E).
    """
    events = {} # event trigger entity : list of interactions pairs
    eventIndex = 1
    eventIds = {}
    for sentenceElement in document.findall("sentence"):
        sentence = inputCorpus.sentencesById[sentenceElement.get("id")]
        sentenceOffset = Range.charOffsetToSingleTuple(sentenceElement.get("charOffset"))
        
        # Group interactions by their interaction word, i.e. the event trigger
        for interaction in sentence.interactions + sentence.pairs:
            if interaction.get("type") == "neg": # negative prediction
                continue
            # All interaction are directed (e1->e2), so e1 is always the trigger
            e1 = sentence.entitiesById[interaction.get("e1")]
            assert(e1.get("isName") == "False")
            if not events.has_key(e1):
                events[e1] = [] # mark entity as an event trigger
            events[e1].append(interaction)
        
        # Predefine event ids because all ids must be defined so that
        # we can refer to nested events
        for entity in sentence.entities:
            if events.has_key(entity): # entity is an event trigger
                eventIds[entity] = "E" + str(eventIndex)
                eventIndex += 1
        
        # Write the events
        for entity in sentence.entities:
            if events.has_key(entity):
                eventType = entity.get("type")
                outputLine = eventIds[entity] + "\t" + eventType + ":" + entity.get("temp_newId")
                for interaction in events[entity]:
                    e1 = sentence.entitiesById[interaction.get("e1")]
                    e2 = sentence.entitiesById[interaction.get("e2")]
                    assert(e1 == entity)
                    if eventIds.has_key(e2): # e2 is a nested event
                        e2Id = eventIds[e2]
                    else: # e2 is a named entity, i.e. protein
                        e2Id = e2.get("temp_newId")
                        #assert(e2.get("isName") == "True")
                    outputLine += " " + interaction.get("type") + ":" + e2Id
                outputFile.write( outputLine + "\n" )           

if __name__=="__main__":
    # Import Psyco if available
    try:
        import psyco
        psyco.full()
        print >> sys.stderr, "Found Psyco, using"
    except ImportError:
        print >> sys.stderr, "Psyco not installed"

    optparser = OptionParser(usage="%prog [options]\nConvert interaction XML to GENIA shared task format.")
    optparser.add_option("-i", "--input", default=None, dest="input", help="interaction xml input file", metavar="FILE")
    optparser.add_option("-o", "--output", default=None, dest="output", help="output directory")
    (options, args) = optparser.parse_args()
    
    assert(options.input != None)
    assert(options.output != None)
    if os.path.exists(options.output):
        print >> sys.stderr, "Output directory exists, removing", options.output
        shutil.rmtree(options.output)
    os.mkdir(options.output)
        
    inputCorpus = CorpusElements.loadCorpus(options.input)
    processCorpus(inputCorpus, options.output)
    
    
