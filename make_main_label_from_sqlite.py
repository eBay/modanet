import os
import json
import argparse
import sqlite3

from tqdm import tqdm
import pandas as pd


def main(server_id):
    json_file = os.path.join(
        os.environ['DATASET_ROOT'],
        'raw/annotations/modanet2018_instances_train.json',
        # modanet2018_instances_val.json doesn't have annotations,
        # so it can't be used as a validation dataset.
    )
    d = json.load(open(json_file))
    print('Load ModaNet json file: {}'.format(json_file))
    df_annt_items = pd.DataFrame(d['annotations'])

    print('Group by snap id')
    tqdm.pandas()
    cols = ['image_id']
    df_annt = df_annt_items\
        .groupby(cols)[
            df_annt_items.columns.difference(cols)]\
        .progress_apply(lambda df_: df_.to_dict('records'))\
        .rename('items')\
        .reset_index()
    
    df_img = pd.DataFrame.from_dict(d['images'])
    df_mdnt = df_img.merge(
        df_annt[df_annt.columns.difference(['id'])],
        left_on='id', right_on='image_id',
        how='inner'
    )

    db_file = os.environ['CHICTOPIA_SQLITE']
    print('Load PaperDoll sqlite file: {}'.format(db_file))
    conn_str = 'file:{}?mode=ro'.format(db_file)
    conn = sqlite3.connect(conn_str, uri=True)
    query = """
        SELECT
            id,
            path
        FROM
            photos
        WHERE
            photos.post_id IS NOT NULL
        AND
            photos.file_file_size IS NOT NULL
    """
    df_ppdl = pd.read_sql(query, con=conn).astype({
        'id': 'int64',
        'path': 'str',
    })

    df = df_mdnt[df_mdnt.columns.difference(['id'])].merge(
        df_ppdl,
        left_on='image_id', right_on='id',
        how='inner'
    )

    print('Make image_url')
    df['image_url'] = df['path'].progress_apply(
        lambda path_:
            'http://images{}.chictopia.com{}'.format(server_id, path_)
    )

    out_file = os.path.join(
        os.environ['DATASET_ROOT'],
        'main/labels/modanet_snaps.json'
    )
    out_dir = os.path.dirname(out_file)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    with open(out_file, 'w') as f:
        json.dump(
            df.to_dict('records'),
            f, indent=4
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--server_id',
        default=0,
        help='server_id must be in [0, 3]'
    )
    args = parser.parse_args()
    main(**vars(args))
