INPUT=$1
OUTPUT=$2

python Utils/InteractionXML/ExportParse.py -i $INPUT -o tempOutput/ --parse McCC

MyScripts/splitBySubcat.sh tempOutput $3
#MyScripts/transformDocuments.sh $3 tempOutput/
#for file in tempOutput/* ; do python makeTrivialParse.py $file ; done

python MyScripts/utils.py unsplitTokenization --output merged.xml $INPUT
python insertParses.py merged.xml tempOutput/ temp.xml
python Utils/ProteinNameSplitter.py -f temp.xml -o $OUTPUT -p McCC -t McCC -n McCC -s McCC

rm merged.xml
rm temp.xml
rm -rf tempOutput/
