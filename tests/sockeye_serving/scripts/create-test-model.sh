#!/usr/bin/env bash

# Outputs a test model to the directory "tiny"
echo "a" > train.de
echo "b" > train.en
python -m sockeye.train -s train.de \
                        -t train.en \
                        -vs train.de \
                        -vt train.en \
						--use-cpu \
                        -o tiny \
                        --encoder=rnn \
                        --decoder=rnn \
                        --num-layers=1:1 \
                        --rnn-num-hidden=2 \
                        --num-embed=1:1 \
                        --num-words=1:1 \
                        --batch-type=sentence \
                        --batch-size=1 \
                        --max-updates=4 \
                        --checkpoint-frequency=2
