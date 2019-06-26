
import argparse
import sys
import os
import shutil
import numpy as np
import pandas as pd
import random
import string
import json
from datetime import datetime, timedelta
from dateutil.tz import tzlocal

def get_daily_commits(start, end, weekdays_cfg, weekends_cfg):
    time_series = pd.date_range(start=start, end=end)
    lam = (weekdays_cfg['avg_daily_commits'], weekends_cfg['avg_daily_commits'])
    samples = np.random.poisson(lam=lam, size=(time_series.size, 2))

    df = pd.DataFrame(data=samples, index=time_series, columns=['weekday_n_commits', 'weekend_n_commits'])

    is_weekend = (df.index.dayofweek == 5) | (df.index.dayofweek == 6)
    df['is_weekend'] = is_weekend
    df['n_commits'] = 0
    df.loc[is_weekend, 'n_commits'] = df['weekend_n_commits']
    df.loc[~is_weekend, 'n_commits'] = df['weekday_n_commits']

    return df

def get_datetimes_single_day(date, n_commits, cfg):
    def close_to(x, samples, min_distance):
        for s in samples:
            if abs(s - x) < min_distance:
                return True
        return False

    def seconds_in_hours(x):
        return x / (60 * 60)

    mu = cfg['commit_hour_mu']
    sigma = cfg['commit_hour_sigma']
    rng = cfg['commit_range']
    min_distance = seconds_in_hours(cfg['minimum_seconds_between_commits'])

    samples = []
    while len(samples) != n_commits:
        s = np.random.normal(mu, sigma)
        if s < rng[0]:
            continue
        elif s >= rng[1]:
            continue

        if close_to(s, samples, min_distance):
            continue

        samples += [s]

    samples = sorted(samples)
    return [date + timedelta(hours=x) for x in samples]

def get_datetimes_for_commits(df, weekdays_cfg, weekends_cfg):
    samples = []
    for ix, row in df.iterrows():
        cfg = weekends_cfg if row['is_weekend'] else weekdays_cfg
        datetimes = get_datetimes_single_day(ix, row['n_commits'], cfg)

        samples += datetimes

    return samples

def create_project(project):
    os.makedirs(project, exist_ok=True)
    os.chdir(project)

    if os.path.isdir('.git'):
        shutil.rmtree('.git')

    os.system('git init')

def make_commits(times, tz):
    total = len(times)
    for i, t in enumerate(times):
        if i % 10 == 0:
            print('doing {} of {}'.format(i, total))

        formatted_date = t.strftime(r'%c {}'.format(tz))
        random_text = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(64))
        open('output.txt', 'w').write(random_text)

        os.putenv('GIT_COMMITTER_DATE', formatted_date)
        os.system('git add . && git commit -m "." --date "{}" > /dev/null'.format(formatted_date))
    print('DONE!')

def main(args):
    config = json.load(args.config)
    weekdays_cfg = config['weekdays']
    weekends_cfg = config['weekends']

    print('Generating commit dates...')
    df = get_daily_commits(args.start, args.end, weekdays_cfg, weekends_cfg)
    times = get_datetimes_for_commits(df, weekdays_cfg, weekends_cfg)

    print('Creating git project...')
    create_project(args.output)

    print('Making commits')
    tz = config.get('timezone', datetime.now(tzlocal()).strftime('%z'))
    make_commits(times, tz)

if __name__ == '__main__':
    yesterday = (datetime.today() - timedelta(days=1)).strftime(r'%Y-%m-%d')

    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description='Create a project in order to Greenify your Github profile',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        '-o',
        '--output',
        type=str,
        default='MyProject',
        help='Path to the project directory',
    )
    parser.add_argument(
        '-c',
        '--config',
        type=argparse.FileType('r'),
        default='config.json',
        help='Configuration file, This is where the meta parameters are',
    )
    parser.add_argument(
        '-s',
        '--start',
        type=lambda x: datetime.strptime(x, r'%Y-%m-%d'),
        default='2019-01-01',
        help='"Start" of the project date',
    )
    parser.add_argument(
        '-e',
        '--end',
        type=lambda x: datetime.strptime(x, r'%Y-%m-%d'),
        default=yesterday,
        help='"End" of the project date',
    )


    args = parser.parse_args(sys.argv[1:])
    main(args)