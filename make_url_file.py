import os
import argparse

import pandas as pd


def main(size):
    json_file = os.path.join(
        os.environ['DATASET_ROOT'],
        '{}/labels/modanet_snaps.json'.format(size)
    )
    df = pd.read_json(json_file)

    df_ = df[['image_url', 'file_name']]

    out_file = os.path.join(
        os.path.dirname(json_file),
        'image_urls.csv'
    )
    out_dir = os.path.dirname(out_file)
    if not os.path.isdir(out_dir):
        print('Make dir: {}'.format(out_dir))
        os.makedirs(out_dir)

    df_.to_csv(out_file, index=None, header=None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--size',
        default='main',
        choices=['main', 'tiny'],
    )
    args = parser.parse_args()
    main(**vars(args))