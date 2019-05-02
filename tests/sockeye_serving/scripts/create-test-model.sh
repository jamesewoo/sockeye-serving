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
                        --rnn-num-hidden=2 \
                        --rnn-attention-in-upper-layers \
                        --rnn-attention-type=dot \
                        --rnn-decoder-hidden-dropout=0.2 \
                        --embed-dropout=0.2 \
                        --num-layers=8:8 \
                        --weight-init=xavier \
                        --weight-init-scale=3.0 \
                        --weight-init-xavier-factor-type=avg \
                        --num-embed=1:1 \
                        --max-seq-len=100 \
                        --optimizer=adam \
                        --optimized-metric=perplexity \
                        --initial-learning-rate=0.0001 \
                        --learning-rate-reduce-num-not-improved=8 \
                        --learning-rate-reduce-factor=0.7 \
                        --max-num-checkpoint-not-improved=1 \
                        --batch-type=sentence \
                        --batch-size=128 \
                        --checkpoint-frequency=2000 \
                        --decode-and-evaluate=500 \
                        --keep-last-params=60
                        