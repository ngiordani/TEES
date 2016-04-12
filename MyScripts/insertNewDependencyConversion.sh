INPUT="$1"
OUTPUT="$2"

python MyScripts/utils.py unsplitTokenization --output $INPUT.merged.xml $INPUT
python Tools/StanfordParser.py -i $INPUT.merged.xml -o $INPUT.merged.converted.xml --parse McCC --reparse
python Utils/ProteinNameSplitter.py -f $INPUT.merged.converted.xml -o $OUTPUT -p McCC -t McCC -n McCC -s McCC

rm $INPUT.merged.xml
rm $INPUT.merged.converted.xml