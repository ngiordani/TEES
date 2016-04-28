import sys
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))
from Tools.StanfordParser import *


insertParses(sys.argv[1], sys.argv[2], output=sys.argv[3])
