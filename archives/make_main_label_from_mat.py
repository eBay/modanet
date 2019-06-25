import os
import json

from tqdm import tqdm
import pandas as pd


def main():
    json_file = os.path.join(
        os.environ['DATASET_ROOT'],
        'raw/annotations/modanet2018_instances_train.json',
        # modanet2018_instances_val.json doesn't have annotations,
        # so it can't be used as a validation dataset.
    )
    print('Load ModaNet json file: {}'.format(json_file))
    df_annt_items = pd.DataFrame(
        json.load(open(json_file))['annotations']
    ).set_index(['image_id', 'id'])

    print('Group by snap id')
    tqdm.pandas()
    cols = ['image_id']
    df_annt = df_annt_items\
        .groupby(cols)[
            df_annt_items.columns.difference(cols)]\
        .progress_apply(lambda df_: df_.to_dict('records'))\
        .rename('items')\
        .reset_index()

    json_file = os.environ['PAPERDOLL_JSONFILE']
    print('Load PaperDoll json file: {}'.format(json_file))
    df_ppdl = pd.read_json(json_file)[
        ['snap_id', 'snap_url', 'post_url']]
    # all snap_url in PaperDoll is not used in ModaNet,
    # so need to crawl post_url to get correct snap images
    # used in ModaNet
    df_annt = df_annt\
        .merge(
            df_ppdl, left_on='image_id', right_on='snap_id',
            how='inner',
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
            df_annt.to_dict('records'),
            f, indent=4
        )


if __name__ == '__main__':
    main()
