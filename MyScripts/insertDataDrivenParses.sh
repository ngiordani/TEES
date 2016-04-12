BASIC_UD=$1
CORPUS=$2
SIZE=$3
DESTINATION=Experiments/parsed-$SIZE/

echo "Basic UD annotations in $BASIC_UD"
echo "Corpus $CORPUS"
echo "Sampling size $SIZE"
echo "Destination in $DESTINATION"

for part in train devel test ;
do
    if [ ! -d "parserData/$CORPUS/$part" ]; then
	echo "Did not find parserData/$CORPUS/$part"
	INPUT=$BASIC_UD/$CORPUS-$part.xml
	python Utils/InteractionXML/ExportParse.py -i $INPUT -o parserData/$CORPUS/$part --parse McCC
    fi
done

echo "All exported parses are in place."

mkdir -p $DESTINATION

cd parserData/$CORPUS/
../parse-all.sh $SIZE
cd ../..

for part in train devel test ;
do
    INPUT=$BASIC_UD/$CORPUS-$part.xml
    OUTPUT=$DESTINATION/$CORPUS-$part.xml
    python MyScripts/utils.py unsplitTokenization --output merged.xml $INPUT
    python MyScripts/insertParses.py merged.xml parserData/$CORPUS/parsed-$SIZE/$part temp.xml
    python Utils/ProteinNameSplitter.py -f temp.xml -o $OUTPUT -p McCC -t McCC -n McCC -s McCC

    rm merged.xml
    rm temp.xml
done
