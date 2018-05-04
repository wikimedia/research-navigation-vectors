import argparse
import os
import sys

# Prefixed with '/user/' in HDFS and '/home/' under local file system.
OUTPUT_DIR = 'bmansurov/data/navigation_vectors'
# Used to find other accompanying scripts
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


"""
python run.py \
    --get_requests \
    --get_sessions \
    --get_vectors \
    --start 2016-02-01 \
    --stop  2016-02-07 \
    --release 2016_02_01_2016_02_07 \
    --langs wikidata,en \
    --dims 50,100,300

python run.py \
    --get_requests \
    --start 2016-02-01 \
    --stop  2016-02-01 \
    --release test2

python run.py \
    --get_sessions \
    --release test2 \
    --langs wikidata,en

python run.py \
    --get_vectors \
    --release test2 \
    --langs wikidata,en \
    --dims 10,20
"""


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--get_requests', default=False, action='store_true')
    parser.add_argument('--get_sessions', default=False, action='store_true')
    parser.add_argument('--get_vectors', default=False, action='store_true')
    parser.add_argument('--start', required=False)
    parser.add_argument('--stop', required=False)
    parser.add_argument('--release', required=True)
    parser.add_argument('--langs', required=False)
    parser.add_argument('--dims', required=False)
    args = vars(parser.parse_args())
    args['output_dir'] = OUTPUT_DIR
    args['script_dir'] = SCRIPT_DIR

    if args['get_requests']:
        if 'start' in args and 'stop' in args:
            cmd = """
                python %(script_dir)/get_requests.py \
                --start %(start)s \
                --stop  %(stop)s \
                --release %(release)s \
                --priority
            """
            os.system(cmd % args)
        else:
            print('need "start" and "stop" to get_requests')
            sys.exit()

    if args['get_sessions']:
        if 'langs' in args:
            os.system(
                "hadoop fs -mkdir /user/%(output_dir)/%(release)s" % args)
            cmd = """
                spark-submit \
                    --driver-memory 5g \
                    --master yarn \
                    --deploy-mode client \
                    --num-executors 10 \
                    --executor-memory 10g \
                    --executor-cores 4 \
                    --queue priority \
                %(script_dir)/get_sessions.py \
                    --release %(release)s \
                    --lang %(lang)s
            """
            for lang in args['langs'].split(','):
                args['lang'] = lang
                os.system(cmd % args)
        else:
            print('need langs to get sessions')
            sys.exit()

    if args['get_vectors']:
        cmds = []
        if 'langs' in args and 'dims' in args:
            os.system("mkdir /home/%(output_dir)/%(release)s" % args)
            cmd = """
            python %(script_dir)/get_vectors.py \
                --release %(release)s \
                --lang %(lang)s \
                --dims %(dim)s \
            """
            for lang in args['langs'].split(','):
                args['lang'] = lang
                for dim in args['dims'].split(','):
                    args['dim'] = dim
                    cmds.append(cmd % args)
            for c in cmds:
                os.system(c)
        else:
            print('need "langs" and "dims" to get models')
            sys.exit()
