PREFIX=$1
DIR=$2

python Core/DivideCorpus.py -i $DIR/$PREFIX-train.xml -o folds
python Core/DivideCorpus.py -i $DIR/$PREFIX-devel.xml -o folds

for i in {0..9} 
do
    TRAIN="" 
    for f in folds/$PREFIX-*.xml.fold[^$i] 
    do
	TRAIN=$TRAIN,$f 
    done 
    TRAIN=${TRAIN:1}

    DEV="folds/$PREFIX-train.xml.fold$i,folds/$PREFIX-devel.xml.fold$i"

    echo $TRAIN
    echo $DEV 

    python Utils/InteractionXML/Catenate.py -i $TRAIN -o $DIR/fold-$i/$PREFIX-train.xml --fast
    python Utils/InteractionXML/Catenate.py -i $DEV -o $DIR/fold-$i/$PREFIX-devel.xml --fast
    cp $DIR/$PREFIX-test.xml $DIR/fold-$i
    MyScripts/trainModel.sh $PREFIX $DIR/fold-$i
    
done

rm -rf folds
