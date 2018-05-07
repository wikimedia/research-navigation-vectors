import argparse
import os
import time

from config import get_config


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
    config = get_config()
    parser = argparse.ArgumentParser()
    parser.add_argument('--release', required=True)
    parser.add_argument('--lang', required=True)
    parser.add_argument('--dims', required=True)

    args = vars(parser.parse_args())
    args['output_dir'] = config['common']['hdfs_output_dir']

    for dim in args['dims'].split(','):
        args['dim'] = dim
        args['input_dir'] = '%(output_dir)s/%(release)s/'\
                            '%(release)s_sessions_%(lang)s' % args
        args['vectors_output_file'] = '%(output_dir)s/%(release)s/'\
                                      '%(release)s_%(lang)s_%(dim)s' % args
        args['binary_vectors_output_file'] = '%(output_dir)s/%(release)s/'\
                                             '%(release)s_%(lang)s_%(dim)s'\
                                             '.bin' % args
        args['word2vec_bin'] = config['common']['word2vec_bin']
        args['convertvec_bin'] = config['common']['convertvec_bin']

        t1 = time.time()

        cmd = """
            nice %(word2vec_bin)s \
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
            %(convertvec_bin)s txt2bin %(vectors_output_file)s
            %(binary_vectors_output_file)s
        """
        os.system(cmd % args)

        t2 = time.time()
        print(t2 - t1)
