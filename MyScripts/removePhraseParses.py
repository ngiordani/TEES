import argparse
import xml.etree.cElementTree as ET
from addGoldAnnotations import removeConstituencyParse

parser = argparse.ArgumentParser(description='"Unsplit" tokenization.')
parser.add_argument('input',
                   help='Input file')
parser.add_argument('--output',  default='test_output.xml',
                   help='Output file')

args = parser.parse_args()


system = args.input
#gold = "/afs/cs.stanford.edu/u/natalias/.tees/corpora/GE09-devel.xml"
#unsplitTokenization(system)
removeConstituencyParse(system)
