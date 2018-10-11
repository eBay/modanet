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


