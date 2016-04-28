echo $1
tail -n 550 $1/log.txt | grep -A 23 strict | grep ALL
