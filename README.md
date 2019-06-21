[![License: CC BY-NC 4.0](https://licensebuttons.net/l/by-nc/4.0/80x15.png)](https://creativecommons.org/licenses/by-nc/4.0/)
# ModaNet

<details><summary>Table of Contents</summary><p>

* [Why we made ModaNet](#why-we-made-modanet)
* [Labels](#labels)
* [Contributing](#contributing)
* [Contact](#contact)
* [Citing ModaNet](#citing-modanet)
</p></details><p></p>


**ModaNet** is a street fashion images dataset consisting of annotations related to RGB images. 
ModaNet provides multiple polygon annotations for each image.  
Each polygon is associated with a label from 13 meta fashion categories. The annotations are based on images in the [PaperDoll image set](http://vision.is.tohoku.ac.jp/~kyamagu/research/paperdoll/), which has only a few hundred images annotated by the superpixel-based tool. The contribution of ModaNet is to provide new and extra **polygon** annotations for the images.


## Why we made ModaNet

ModaNet is intended to serve an educational purpose by providing a benchmark annotation set for emerging computer vision research including **semantic segmentation**, **object detection**, **instance segmentation**, **polygon detection**, and etc.


### Labels
Each polygon (bounding box, segmentation mask) annotation is assigned to one of the following labels:

| Label | Description |
| --- | --- |
| 1 | bag |
| 2 | belt |
| 3 | boots |
| 4 | footwear |
| 5 | outer |
| 6 | dress |
| 7 | sunglasses |
| 8 | pants |
| 9 | top |
|10 | shorts |
|11 | skirt |
|12 | headwear |
|13 | scarf & tie |

The annotation data format of ModaNet follows the same style as [COCO-dataset](http://cocodataset.org).


#### Data format
```
{
'info' : info, 'images' : [image], 'annotations' : [annotation], 'licenses' : [license],'year': year, 'categories': [category], 'type': type
}

info{
'version' : str, 'description' : str, 'contributor' : str, 'date_created' : datetime,
}

image{
'id' : int, 'width' : int, 'height' : int, 'file_name' : str, 'license' : int
}

license{
'id' : int, 'name' : str, 'url' : str,
}

annotation{
  'area': int, 
  'bbox': [x,y,width,height],
  'segmentation': [polygon],
  'image_id': int,
  'id': int,
  'category_id': int,
  'iscrowd': int
}
category{
  'supercategory': str, 'id': int, 'name': str,
}
```


#### Setup

```
pipenv sync
```

or

```
pip install -r requirements.txt
```

Excute the following command at **the parent directory of this repository** (e.g. `modanet/..`)

```
git clone https://github.com/hrsma2i/dataset-PaperDoll.git PaperDoll
```

- Setup PaperDoll dataset according to the instruction in [hrsma2i/dataset-PaperDoll](https://github.com/hrsma2i/dataset-PaperDoll).
  - Skip the step of downloading images.
- **Caution**
  - ModaNet dataset has some image ids that don't exist in PaperDoll dataset. The number of images that exist in the both, is 32,337.
  - The all `url`s(`snap_url`) in PaperDoll are not linked to main snap images that are annotated in ModaNet, so it needs to run `download_images.py`.


```
python download_images.py
```

This scripts downlaod

- main snap images in `images`
- their URLs in `labels/image_urls.tsv`


#### Submitting results to leaderboard

You can participate only the Object Detection task by submitting results as follows

```
[{
'image_id' : int, 'category_id' : int, 'bbox' : [x,y,width,height], 'score' : float,
}]
```
Example
```
[{'bbox': [192, 30, 20, 28],
  'category_id': 13,
  'image_id': 100014,
  'score': 0.8}]
```

You can participate only the Instance Segmentation/Semantic Segmentation/Polygon prediction tasks by submitting results as follows
```
[{
'image_id' : int, 'category_id' : int, 'segmentation' : polygon, 'score' : float,
}]
```

Example
```
[{'segmentation': [[210,
    31,
    212,
    35,
    204,
    37,
    204,
    45,
    205,
    54,
    199,
    58,
    194,
    52,
    198,
    42,
    192,
    32,
    194,
    30,
    201,
    33]],
  'category_id': 13,
  'image_id': 100014,
  'score': 0.8 }]
```

You can participate the task of joint detection and segmentation by submitting results as follows


```
[{
'image_id' : int, 'category_id' : int, 'segmentation' : polygon, 'score' : float, 'bbox' : [x,y,width,height]
}]
```
Example
```
[{'bbox': [192, 30, 20, 28],
  'category_id': 13,
  'image_id': 100014,
  'segmentation': [[210,
    31,
    212,
    35,
    204,
    37,
    204,
    45,
    205,
    54,
    199,
    58,
    194,
    52,
    198,
    42,
    192,
    32,
    194,
    30,
    201,
    33]],
  'score': 0.8}]
```

We acknowledge the contribution of COCOdataset team and all the format would follow the same style as those in the COCOdataset.

## Contributing
You are more than welcome to contribute to this github repo! Either by submitting a bug report, or providing feedback about this dataset. Please open issues for specific tasks or post to the contact Google group below.


## Contact
To discuss the dataset, please contact [Moda-net Google Group](https://groups.google.com/forum/#!forum/moda-net).


## Citing ModaNet
If you use ModaNet, we would appreciate reference to the following paper:

Shuai Zheng, Fan Yang, M. Hadi Kiapour, Robinson Piramuthu. ModaNet: A Large-Scale Street Fashion Dataset with Polygon Annotations. ACM Multimedia, 2018.


Biblatex entry:
```
@inproceedings{zheng/2018acmmm,
  author       = {Shuai Zheng and Fan Yang and M. Hadi Kiapour and Robinson Piramuthu},
  title        = {ModaNet: A Large-Scale Street Fashion Dataset with Polygon Annotations},
  booktitle    = {ACM Multimedia},
  year         = {2018},
}
```
## License
This annotation data is released under the [Creative Commons Attribution-NonCommercial license 4.0](https://creativecommons.org/licenses/by-nc/4.0/).


