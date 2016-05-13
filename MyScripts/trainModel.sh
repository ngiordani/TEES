nlpsub -p high -m 4gb python train.py --trainFile $1-train.xml --develFile $1-devel.xml --testFile $1-test.xml -o $2 -t $1
