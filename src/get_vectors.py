import time
import argparse
import os

# Prefixed with '/user/' in HDFS and '/home/' under local file system.
OUTPUT_DIR = 'bmansurov/data/navigation_vectors'
WORD2VEC_BIN = '/home/bmansurov/word2vec/word2vec'
CONVERTVEC_BIN = '/home/bmansurov/convertvec/convertvec'

"""
Given a file of sessions, train a word2vec model where
articles::sessions and words::sentences in the original formulation. We
either learn embeddings for articles within a Wikipedia, or for Wikidata
items,depending on the lang parameter. When lang=wikidata, we learn
Wikidata embeddings.

Usage:
    python get_vectors.py \
        --release test \
        --lang en \
        --dims 100
"""


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--release', required=True)
    parser.add_argument('--lang', required=True)
    parser.add_argument('--dims', required=True)

    args = vars(parser.parse_args())

    for dim in args['dims'].split(','):
        args['dim'] = dim
        args['input_dir'] = '%(output_dir)/%(release)s/'\
                            '%(release)s_sessions_%(lang)s' % args
        args['vectors_output_file'] = '%(output_dir)/%(release)s/'\
                                      '%(release)s_%(lang)s_%(dim)s' % args
        args['binary_vectors_output_file'] = '$(output_dir)/%(release)s/'\
                                             '%(release)s_%(lang)s_%(dim)s'\
                                             '.bin' % args
        args['word2vec_bin'] = WORD2VEC_BIN
        args['convertvec_bin'] = CONVERTVEC_BIN

        t1 = time.time()

        cmd = """
        nice %(word2vec_bin) \
        -train %(input_dir)s \
        -output %(vectors_output_file)s \
        -size %(dim)s \
        -threads 18 \
        -min-count 50 \
        -binary 0 \
        -cbow 0 \
        -iter 10 \
        -negative 3 \
        -sample 0.001 \
        -window 6
        """

        print(cmd % args)
        os.system(cmd % args)

        cmd = """
            %(convertvec_bin) txt2bin %(vectors_output_file)s
            %(binary_vectors_output_file)s
        """
        os.system(cmd % args)

        t2 = time.time()
        print(t2 - t1)
