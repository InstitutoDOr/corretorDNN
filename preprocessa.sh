fairseq-preprocess --source-lang fr --target-lang en \
    --trainpref data/ptbr/train.tok \
    --validpref data/ptbr/dev.tok \
    --destdir bin/ptbr \
    --workers 15

