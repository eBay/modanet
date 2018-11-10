#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import random
import argparse
from glob import glob
import asyncio

import aiohttp
from tqdm import tqdm
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

# a helper coroutine to perform GET requests:
async def get_text(*args, **kwargs):
	async with aiohttp.ClientSession() as session:
		try:
			async with session.get(*args, **kwargs) as res:
				tqdm.write('Status: {}'.format(res.status))
				return await res.text()
		except:
			return None

async def get_image(*args, **kwargs):
	async with aiohttp.ClientSession() as session:
		try:
			async with session.get(*args, **kwargs) as res:
				tqdm.write('Status: {}'.format(res.status))
				return await res.content.read()
		except:
			return None


async def download_file(out_file, img_dir,
						snap_id, post_url, seconds):
	# this routine is protected by a semaphore
	with await sem:
		timeout = aiohttp.ClientTimeout(total=seconds)
		text = await get_text(post_url, timeout=timeout)

		# snap url
		try:
			soup = BeautifulSoup(text)
			snap_url = soup.find('div', id="image_wrap")\
				.find('img')['src']
			with open(out_file, 'a') as f:
				f.write('{}\t{}\n'.format(snap_id, snap_url))
		except:
			snap_url = None
			tqdm.write('(snap url) Error or Time out: {}'.format(post_url))

		# image
		if snap_url is not None:
			content = await get_image(snap_url, timeout=timeout)
			if content is not None:
				img_file = os.path.join(img_dir, '{:07}.jpg'.format(snap_id))
				with open(img_file, 'wb') as f:
					f.write(content)
			else:
				tqdm.write('(image) Error or Time out: {}'.format(snap_url))

'''
make nice progressbar
install it by using `pip install tqdm`
'''
async def wait_with_progressbar(coros):
	coros = [await f 
			 for f in tqdm(asyncio.as_completed(coros), total=len(coros))]
	return coros


if __name__=="__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'-r', '--num_requests',
		type=int,
		default=100)
	parser.add_argument(
		'-t',
		type=int,
		default=180,
		help='seconds to wait until time out')
	parser.add_argument(
		'-o', '--overwrite',
		action='store_true')
	args = parser.parse_args()

	out_file = './labels/image_urls.tsv'
	img_dir = './images'

	out_dir = os.path.dirname(out_file)
	if not os.path.isdir(out_dir):
		os.makedirs(out_dir)
	if not os.path.isdir(img_dir):
		os.makedirs(img_dir)

	if args.overwrite:
		if os.path.exists(out_file):
			print('out_file', out_file)
			os.remove(out_file)


	json_file = './annotations/modanet2018_instances_train.json'
	d = json.load(open(json_file))
	df = pd.DataFrame(d['images']).set_index('id').sort_index()
	df_ann = pd.DataFrame(d['annotations']).set_index(['image_id', 'id'])

	json_file = '../PaperDoll/labels/paperdoll.json'
	df_ppdl = pd.read_json(json_file)

	ids_exist = np.intersect1d(
		df_ppdl['snap_id'].values,
		df_ann.index.levels[0],
	)

	# avoid from downloading images that has been downloaded yet.
	img_files = glob(os.path.join(img_dir, '*'))
	ids_downloaded = np.array([
		int(os.path.basename(img_file).split('.')[0])
		for img_file in img_files])
	ids_exist = np.setdiff1d(ids_exist, ids_downloaded)


	sr_post_url = df_ppdl[['snap_id', 'post_url']]\
		[df_ppdl['snap_id'].isin(ids_exist)]\
		.set_index('snap_id')['post_url']
	sr_post_url
	it = sr_post_url.items()


	# avoid to many requests(coros) the same time.
	# limit them by setting semaphores (simultaneous requests)
	sem = asyncio.Semaphore(args.num_requests)

	coros = [download_file(out_file, img_dir,
						   snap_id, post_url, args.t) 
			 for snap_id, post_url in it]
	eloop = asyncio.get_event_loop()
	#eloop.run_until_complete(asyncio.wait(coros))
	eloop.run_until_complete(wait_with_progressbar(coros))
	eloop.close()