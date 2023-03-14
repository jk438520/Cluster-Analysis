Tired of Topic Models? Clusters of Pretrained Word Embeddings Make for Fast and Good Topics too! (2020; Code for paper)
==============================

This repo fixes reproducibility problems with the implementation of the paper [Tired of Topic Models? Clusters of Pretrained Word Embeddings Make for Fast and Good Topics too!]( https://aclanthology.org/2020.emnlp-main.135.pdf) (Sia, Dalmia, and Mieke; EMNLP, 2020).


## How to use the code
* Install requirements by `pip install -r requirements.txt`. 
* Download pre-trained models, for example `wget https://figshare.com/ndownloader/files/10798046 -O GoogleNews-vectors-negative300.bin` or (for a smaller model) `wget https://github.com/eyaler/word2vec-slim/raw/master/GoogleNews-vectors-negative300-SLIM.bin.gz` and `gzip -d GoogleNews-vectors-negative300-SLIM.bin.gz`.
* To cluster the word embeddings to discover the latent topics, run
```python code/score.py <arguments>```. The description of the arguments is given below:

### Required:
`--entities` : The type of pre-trained word embedding you are clustering with\
choices= word2vec, fasttext, glove, KG 
KG stands for your own set of embeddings 

`--entities_file`: The file name contain the embeddings 

`--clustering_algo`: The clustering algorithm to use  
choices= KMeans, SPKMeans, GMM, KMedoids, Agglo, DBSCAN , Spectral, VMFM

`--vocab`: List of vocab files to use for tokenization, for example `/usr/share/dict/words`

### Not Required:
`--dataset`: Dataset to test clusters against against\
default = 20NG 
choices= 20NG, reuters

`--preprocess`: Cuttoff threshold for words to keep in the vocab based on frequency 

`--use_dims`: Dimensions to scale with PCA (much be less than orginal dims)

`--num_topics`: List of number of topics to try 
default: 20

`--doc_info`: How to add document information
 choices= DUP, WGT
 
`--rerank`: Value used for reranking the words in a cluster  
choices=tf, tfidf, tfdf

Example call:
`python3 code/score.py --clustering_algo KMeans --vocab /usr/share/dict/words --entities word2vec`

## How to cite

To cite the original paper and this fork, use
``` bibtex
@inproceedings{sia-etal-2020-tired,
    title = "Tired of Topic Models? Clusters of Pretrained Word Embeddings Make for Fast and Good Topics too!",
    author = "Sia, Suzanna  and
      Dalmia, Ayush  and
      Mielke, Sabrina J.",
    booktitle = "Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing (EMNLP)",
    month = nov,
    year = "2020",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2020.emnlp-main.135",
    doi = "10.18653/v1/2020.emnlp-main.135",
    pages = "1728--1736",
}

@software{Skorski_A_working_implmentation_2023,
author = {Skorski, Maciej},
month = {3},
title = {{A working implmentation of the paper Tired of Topic Models? Clusters of Pretrained Word Embeddings...}},
url = {https://github.com/maciejskorski/Cluster-Analysis},
version = {1.0.0},
year = {2023}
}
```
