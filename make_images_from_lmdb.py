import io
import os
import argparse

from PIL import Image
from tqdm import tqdm
import lmdb
import pandas as pd


def main(size):
    json_file = os.path.join(
        os.environ['DATASET_ROOT'],
        '{}/labels/modanet_snaps.json'.format(size)
    )
    df = pd.read_json(json_file)

    db_file = os.environ['PAPERDOLL_LMDBFILE']
    photo_data = PhotoData(db_file)

    img_dir = os.path.join(
        os.environ['DATASET_ROOT'],
        '{}/images'.format(size)
    )
    if not os.path.isdir(img_dir):
        print('Make dirs: {}'.format(img_dir))
        os.makedirs(img_dir)

    def _save_image(row):
        save_image(
            row=row,
            photo_data=photo_data,
            img_dir=img_dir
        )

    tqdm.pandas()
    df.progress_apply(_save_image, axis=1)


def save_image(row, photo_data, img_dir):
    img_id = row['id']
    img_name = row['file_name']
    pil_img = photo_data[img_id]
    out_file = os.path.join(img_dir, img_name)
    pil_img.save(out_file, quality=95)


class PhotoData(object):
    def __init__(self, path):
        self.env = lmdb.open(
            path, map_size=2**36, readonly=True, lock=False
        )

    def __iter__(self):
        with self.env.begin() as t:
            with t.cursor() as c:
                for key, value in c:
                    yield key, value

    def __getitem__(self, index):
        key = str(index).encode('ascii')
        with self.env.begin() as t:
            data = t.get(key)
        if not data:
            return None
        with io.BytesIO(data) as f:
            image = Image.open(f)
            image.load()
            return image

    def __len__(self):
        return self.env.stat()['entries']


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s', '--size',
        default='main',
        choices=['main', 'tiny'],
    )
    args = parser.parse_args()
    main(**vars(args))
