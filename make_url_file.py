import os
import sys
import argparse
import asyncio

import aiohttp
from tqdm import tqdm
import pandas as pd
import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-j', '--json_file',
        default=os.path.join(
            os.environ['DATASET_ROOT'],
            'main/labels/modanet_snaps.json'
        ),
    )
    parser.add_argument(
        '-o', '--out_file'
    )
    parser.add_argument(
        '-e', '--error_file'
    )
    parser.add_argument(
        '-r', '--n_requests',
        type=int,
        default=25)
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=6000,
        help='seconds to wait until time out')
    parser.add_argument(
        '-f', '--force',
        action='store_true')
    args = parser.parse_args()

    make_url_file(**vars(args))


def make_url_file(json_file, out_file, error_file, n_requests, timeout, force):
    print(locals())

    df = pd.read_json(json_file)

    if out_file is None:
        out_dir = os.path.dirname(json_file)
        out_file = os.path.join(out_dir, 'image_urls.csv')

    if error_file is None:
        out_dir = os.path.dirname(json_file)
        error_file = os.path.join(out_dir, 'error_post_urls.csv')

    if os.path.exists(out_file):
        if not force:
            overwrite = input(
                '{} already exists. Overwite? [y/n]: '.
                format(out_file)) in ['y', 'yes']

            if not overwrite:
                print('Canceled.')
                sys.exit()

        os.remove(out_file)
        os.remove(error_file)

    out_dir = os.path.dirname(out_file)
    if not os.path.isdir(out_dir):
        print('Make dir: {}'.format(out_dir))
        os.makedirs(out_dir)

    # avoid to many requests(coros) the same time.
    # limit them by setting semaphores (simultaneous requests)
    sem = asyncio.Semaphore(n_requests)
    writer = AsyncWriter(out_file, error_file, sem, timeout)

    coros = [
        writer.write_image_url(row)
        for i, row in df.iterrows()]
    eloop = asyncio.get_event_loop()
    # eloop.run_until_complete(asyncio.wait(coros))
    eloop.run_until_complete(wait_with_progressbar(coros))
    eloop.close()


class AsyncWriter:
    def __init__(self, out_file, error_file, sem, timeout):
        self.out_file = out_file
        self.error_file = error_file
        self.sem = sem
        self.timeout = timeout

    async def write_image_url(self, row):
        post_url = row['post_url']
        image_id = row['image_id']

        with await self.sem:
            _timeout = aiohttp.ClientTimeout(total=self.timeout)
            text = await self.get_text(
                post_url, image_id,
                timeout=_timeout)

            if text is not None:
                soup = BeautifulSoup(text, features='html.parser')
                if soup is not None:
                    image_url = soup.find('div', id="image_wrap")\
                        .find('img')['src']
                    # e.g., .jpg
                    ext = image_url.split('.')[-1]
                    out_name = '{:07}.{}'.format(image_id, ext)
                    with open(self.out_file, 'a') as f:
                        f.write('{},{}\n'.format(image_url, out_name))
                else:
                    print(text)

    async def get_text(self, post_url, image_id, *args, **kwargs):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(post_url, *args, **kwargs) as res:
                    if res.status == requests.codes.ok:
                        return await res.text()
                    else:
                        res.raise_for_status()
            except Exception as e:
                tqdm.write('{}: {}'.format(post_url, e))
                with open(self.error_file, 'a') as f:
                    f.write('{},{},{}\n'.format(post_url, image_id, e))
                return None


async def wait_with_progressbar(coros):
    '''
    make nice progressbar
    install it by using `pip install tqdm`
    '''
    coros = [await f
             for f in tqdm(asyncio.as_completed(coros), total=len(coros))]
    return coros


if __name__ == '__main__':
    main()
