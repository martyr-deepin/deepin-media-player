#! /bin/sh

var = $#
    for i in $@
    do
        echo $i
        python ./main.py $i
        break
    done    


