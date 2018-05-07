import argparse
import datetime
import os

from pyspark import SparkConf, SparkContext

from config import get_config

"""
Given a hive table of requests grouped by IP, UA, XFF and day:
    1. convert hive data format to json
    2. break each days worth of request for each "client" into sessions
    3. remove Main-page and non-main namespace article from sessions
    4. Output [{
        'lang': wikipedia lang,
        'title': article title,
        'id': wikidata id
    }] for each session, ordered by time of request

Usage:
    spark-submit \
        --driver-memory 5g \
        --master yarn \
        --deploy-mode client \
        --num-executors 10 \
        --executor-memory 10g \
        --executor-cores 4 \
        --queue priority \
    get_sessions.py \
        --release test \
        --lang en
"""


def parse_requests(requests):
    ret = []
    for r in requests.split('||'):
        t = r.split('|')
        # should be list of (name, value) pairs and contain at least
        # id, ts, title
        if (len(t) % 2) != 0:
            continue
        data_dict = {t[i]: t[i + 1] for i in range(0, len(t), 2)}
        ret.append(data_dict)
    ret.sort(key=lambda x: x['ts'])  # sort by time
    return ret


def parse_dates(requests):
    clean = []
    for r in requests:
        try:
            r['ts'] = datetime.datetime.strptime(r['ts'], '%Y-%m-%d %H:%M:%S')
            clean.append(r)
        except Exception:
            pass
    return clean


def sessionize(requests):
    """
    Break request stream whenever
    there is 30 min gap in requests
    """
    sessions = []
    session = [requests[0]]
    for r in requests[1:]:
        d = r['ts'] - session[-1]['ts']
        if d > datetime.timedelta(minutes=30):
            sessions.append(session)
            session = [r, ]
        else:
            session.append(r)

    sessions.append(session)
    return sessions


def filter_consecutive_articles(requests):
    """
    Looking at the data, there are a lot of
    sessions with the same article
    requested 2 times in a row. This
    does not make sense for training, so
    lets collapse them into 1 request
    """
    r = requests[0]
    t = r['title']
    clean_rs = [r, ]
    prev_t = t
    for r in requests[1:]:
        t = r['title']
        if t == prev_t:
            continue
        else:
            clean_rs.append(r)
            prev_t = t
    return clean_rs


def filter_blacklist(requests):
    """
    If the session contains an article in the blacklist,
    drop the session. Currently, only the Main Page is
    in the black list
    """
    black_list = set(['Q5296', ])
    for r in requests:
        if r['id'] in black_list:
            return False
    return True


def scrub_dates(requests):
    for r in requests:
        del r['ts']
    return requests


if __name__ == '__main__':
    config = get_config()
    parser = argparse.ArgumentParser()
    parser.add_argument('--request_db',
                        default=config['sessions']['hive_db'],
                        help='hive db')
    parser.add_argument('--release', required=True, help='hive table')
    parser.add_argument('--lang',
                        required=True,
                        default=config['sessions']['wikidata'],
                        help='wikidata will use all langs')
    args = vars(parser.parse_args())

    args['table'] = args['release'].replace('-', '_') + '_requests'
    args['base_hdfs_output_dir'] = config['common']['hdfs_output_dir']
    args['base_local_output_dir'] = config['common']['local_output_dir']

    # create base dirs
    print('Creating output dirs.')
    print(os.system(
        'hadoop fs -mkdir %(base_hdfs_output_dir)s/%(release)s' % args))
    print(os.system('mkdir %(base_local_output_dir)s/%(release)s' % args))

    # define io paths
    args['input_dir'] = '/user/hive/warehouse/'\
                        '%(request_db)s.db/%(table)s' % args
    args['hdfs_output_dir'] = '%(base_hdfs_output_dir)s/%(release)s/'\
                              '%(release)s_sessions_%(lang)s' % args
    args['local_output_file'] = '%(base_local_output_dir)s/%(release)s/'\
                                '%(release)s_sessions_%(lang)s' % args
    args['local_output_dir'] = '%(base_local_output_dir)s/%(release)s/'\
                               '%(release)s_sessions_%(lang)s_dir' % args

    # clean up old data
    print('Cleaning up old data.')
    print(os.system('hadoop fs -rm -r %(hdfs_output_dir)s' % args))
    print(os.system('rm -rf %(local_output_file)s' % args))
    print(os.system('rm -rf %(local_output_dir)s' % args))

    conf = SparkConf()
    conf.set("spark.app.name", 'a2v preprocess')
    sc = SparkContext(conf=conf, pyFiles=[])

    requests = sc.textFile(args['input_dir']) \
        .map(parse_requests)

    if args['lang'] != 'wikidata':
        requests = requests.map(
            lambda rs: [r for r in rs if r['lang'] == args['lang']])

    if args['lang'] == 'wikidata':
        def to_str(x): return ' '.join([e['id'] for e in x])
    else:
        def to_str(x): return ' '.join([e['title'] for e in x])

    requests \
        .filter(filter_blacklist) \
        .filter(lambda x: len(x) > 1) \
        .map(filter_consecutive_articles) \
        .filter(lambda x: len(x) > 1) \
        .map(parse_dates) \
        .flatMap(sessionize) \
        .filter(lambda x: len(x) > 1) \
        .filter(lambda x: len(x) < 30) \
        .map(scrub_dates) \
        .map(to_str) \
        .saveAsTextFile(
            args['hdfs_output_dir'],
            compressionCodecClass="org.apache.hadoop.io.compress.GzipCodec")

    # transfer data to local
    os.system('hadoop fs -copyToLocal %(hdfs_output_dir)s'
              ' %(local_output_dir)s' % args)
    os.system('cat %(local_output_dir)s/* | gunzip >'
              ' %(local_output_file)s' % args)
    os.system('rm -rf %(local_output_dir)s' % args)
