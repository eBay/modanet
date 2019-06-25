import os

import pandas as pd
from pycocotools.coco import COCO


def main():
    json_file = os.path.join(
        os.environ['DATASET_ROOT'],
        'raw/annotations/modanet2018_instances_train.json'
    )
    coco = COCO(json_file)
    cats = coco.loadCats(coco.getCatIds())
    all_ctgs = [cat['name'] for cat in cats]
    all_ctg_ids = coco.getCatIds(catNms=all_ctgs)
    df_ctg = pd.DataFrame({
        'category_id': all_ctg_ids,
        'category': all_ctgs,
    })

    out_file = os.path.join(
        os.environ['DATASET_ROOT'],
        'main/labels/master_category.csv'
    )
    out_dir = os.path.dirname(out_file)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    df_ctg.to_csv(out_file, index=False)


if __name__ == '__main__':
    main()