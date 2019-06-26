import os
import json
import argparse
import sqlite3

from tqdm import tqdm
import pandas as pd
from pycocotools.coco import maskUtils
from chainercv.utils import mask_to_bbox


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
    df_img = pd.DataFrame.from_dict(d['images'])

    print('Refine bboxes using its segmentaion maps')
    tqdm.pandas()
    df_annt_items['bbox'] = df_annt_items.merge(
        df_img.rename(columns={'id': 'image_id'})[
            ['image_id', 'width', 'height']],
        on='image_id'
    ).progress_apply(refine_bbox, axis=1)

    print('Group by snap id')
    tqdm.pandas()
    cols = ['image_id']
    df_annt = df_annt_items\
        .groupby(cols)[
            df_annt_items.columns.difference(cols)]\
        .progress_apply(lambda df_: df_.to_dict('records'))\
        .rename('items')\
        .reset_index()

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


def refine_bbox(row):
    masks = segm_to_mask(
        row['segmentation'],
        row['width'], row['height'],
    )[None, :, :]
    bbox_ch = mask_to_bbox(masks)[0]
    bbox_mdnt = reform_bbox(bbox_ch)
    return bbox_mdnt


def segm_to_mask(segm, w, h):
    """
    Convert a segmentation map which can be polygons to a binary mask.
    Reference:
        https://github.com/cocodataset/cocoapi/blob/master/PythonAPI/pycocotools/coco.py

    Args:
        segm (list<list<int>> or list<int>):
            A segmentation map which can be polygons.
        w (int): Image width
        h (int): Image hight

    Returns:
        mask (np.array(H, W)):
            A segmentation mask of a particular class.
    """
    rle = segm_to_rle(segm, w, h)
    mask = maskUtils.decode(rle)
    return mask


def segm_to_rle(segm, w, h):
    """
    Convert segmentation map which can be polygons, uncompressed RLE to RLE.
    Reference:
        https://github.com/cocodataset/cocoapi/blob/master/PythonAPI/pycocotools/coco.py

    Args:
        segm (list<list<int>> or list<int>):
            A segmentation map which can be polygons.
        w (int): Image width
        h (int): Image hight

    Returns:
        rle: RLE
    """
    if type(segm) == list:
        # polygon -- a single object might consist of multiple parts
        # we merge all parts into one mask rle code
        rles = maskUtils.frPyObjects(segm, h, w)
        rle = maskUtils.merge(rles)
    elif type(segm['counts']) == list:
        # uncompressed RLE
        rle = maskUtils.frPyObjects(segm, h, w)
    else:
        # rle
        rle = segm
    return rle


def reform_bbox(bbox):
    """[summary]

    Args:
        bbox (np.array: (4, )):
            A chainercv format bbox.
            [ymin, xmin, ymax, xmax]

    Returns:
        ls_bbox (list<int>):
            A ModaNet format bbox.
            [x, y, width, height]
    """
    ymin, xmin, ymax, xmax = list(bbox)
    x = int(xmin)
    y = int(ymin)
    width = int(xmax - xmin)
    height = int(ymax - ymin)
    ls_bbox = [x, y, width, height]
    return ls_bbox


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--server_id',
        default=0,
        help='server_id must be in [0, 3]'
    )
    args = parser.parse_args()
    main(**vars(args))
