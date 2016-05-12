PREFIX=$1
DIR=$2

python Core/DivideCorpus.py -i $DIR/$PREFIX-train.xml -o $DIR/folds
python Core/DivideCorpus.py -i $DIR/$PREFIX-devel.xml -o $DIR/folds

for i in {0..9} 
do
    TRAIN="" 
    for f in $DIR/folds/$PREFIX-*.xml.fold[^$i] 
    do
	TRAIN=$TRAIN,$f 
    done 
    TRAIN=${TRAIN:1}

    DEV="$DIR/folds/$PREFIX-train.xml.fold$i,$DIR/folds/$PREFIX-devel.xml.fold$i"

    echo $TRAIN
    echo $DEV 

    python Utils/InteractionXML/Catenate.py -i $TRAIN -o $DIR/fold-$i/$PREFIX-train.xml --fast
    python Utils/InteractionXML/Catenate.py -i $DEV -o $DIR/fold-$i/$PREFIX-devel.xml --fast
    cp $DIR/$PREFIX-test.xml $DIR/fold-$i

    python train.py --trainFile $PREFIX-train.xml --develFile $PREFIX-devel.xml --testFile $PREFIX-test.xml -o $DIR/fold-$i -t $PREFIX
    #MyScripts/trainModel.sh $PREFIX $DIR/fold-$i
    
done

rm -rf $DIR/folds
