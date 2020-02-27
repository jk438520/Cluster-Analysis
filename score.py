from sklearn.datasets import fetch_20newsgroups
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.metrics import pairwise_distances_argmin_min
import scipy.stats
import sys
import argparse
import string
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

import gensim

import fasttext.util
import fasttext



def main():
    args = parse_args()
    stopwords = set(line.strip() for line in open('stopwords_en.txt'))
    train_word_to_file, files_num = create_vocab_and_files(stopwords, "train")


    intersection = None
    words_index_intersect = None


    if args.entities == "word2vec":
        model = gensim.models.KeyedVectors.load_word2vec_format('models/GoogleNews-vectors-negative300.bin', binary=True)
        intersection, words_index_intersect = find_intersect(model.vocab, train_word_to_file, model)

    if args.entities == "fasttext":
        ft = fasttext.load_model('models/wiki.en.bin')
        intersection, words_index_intersect = create_entities_ft(ft, train_word_to_file)
        print(intersection.shape)



    elif args.entities == "KG":
        data, word_index = read_entity_file(args.entities, args.id2name)
        intersection, words_index_intersect = find_intersect(word_index, train_word_to_file, data)

    #name = args.entities.split("-")[1]
    #type = args.entities.split("-")[2].split("-")[0]





    intersection_red = PCA_dim_reduction(intersection, 2)
    intersection_red = intersection_red.T

    #intersection = PCA_dim_reduction(intersection, 400)

    test_word_to_file, test_files_num = create_vocab_and_files(stopwords, "test")

    npmis = []
    labels = None
    top_k = None
    for rand in range(5):
        if args.clustering_algo == "KMeans":
            labels, top_k  = KMeans_model(intersection, rand)
        elif args.clustering_algo == "GMM":
            labels, top_k  = GMM_model(intersection, rand)

        bins, top_k_words = sort(labels, top_k, words_index_intersect)
        npmis.append(npmi(top_k_words, test_word_to_file, test_files_num))
    print("NPMI mean:" + str(np.mean(npmis)))

    #print_bins(bins, "word2vec", "")
    #print_top_k(top_k_words,"word2vec", "")





def sort(labels, indices, word_index):
    bins = {}
    index = 0
    top_k_bins = []
    for label in labels:
        if label not in bins:
            bins[label] = [word_index[index]]
        else:
            bins[label].append(word_index[index])
        index += 1;
    for i in range(0, 20):
        ind = indices[i]
        top_k = []
        for word_ind in ind:
            top_k.append(word_index[word_ind])
        top_k_bins.append(top_k)
    return bins, top_k_bins


def print_bins(bins, name, type):
    f = open(name + "_" + type + "_corpus_bins.txt","w+")
    for i in range(0, 20):
        f.write("Bin " + str(i) + ":\n")
        for word in bins[i]:
            f.write(word + ", ")
        f.write("\n\n")

    f.close()

def print_top_k(top_k_bins, name, type):
    f = open(name + "_" + type + "_corpus_top_k.txt","w+")
    for i in range(0, 20):
        f.write("Bin " + str(i) + ":\n")
        top_k = top_k_bins[i]
        for word in top_k:
            f.write(word + ", ")
        f.write("\n\n")
    f.close()

def create_id_dict(id2name):
    data = {}
    for line in open(id2name):
        mapping = line.split()
        data[mapping[0]] = mapping[1]
    return data



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--entities", type=str, required=True, choices=["word2vec", "fasttext", "KG"])
    parser.add_argument("--clustering_algo", type=str, required=True, choices=["KMeans", "GMM"])
    parser.add_argument( "--entities_file", type=str, help="entity file")
    parser.add_argument('--id2name', type=Path, help="id2name file")
    args = parser.parse_args()
    return args


def read_entity_file(file, id_to_word):
    data = []
    word_index = {}
    index = 0
    mapping = None
    if id_to_word != None:
        mapping = create_id_dict(id_to_word)

    for line in open(file):
        embedding = line.split()
        if id_to_word != None:
            embedding[0] = mapping[embedding[0]][1:]
        word_index[embedding[0].lower()] = index
        index +=1
        embedding = list(map(float, embedding[1:]))
        data.append(embedding)


    print("KG: " + str(len(data)))
    return data, word_index

def PCA_dim_reduction(intersection, dim):
    sigma = np.cov(intersection.T)
    eigVals, eigVec = np.linalg.eig(sigma)
    sorted_index = eigVals.argsort()[::-1]

    eigVals = eigVals[sorted_index]
    eigVec = eigVec[:,sorted_index]

    eigVec = eigVec[:,:dim]
    transformed = intersection.dot(eigVec)
    return transformed

def find_intersect(word_index, vocab, data):
    words = []
    vocab_embeddings = []

    intersection = set(word_index.keys()) & set(vocab.keys())
    print("Intersection: " + str(len(intersection)))

    intersection = np.sort(np.array(list(intersection)))


    for word in intersection:
        vocab_embeddings.append(data[word])
        words.append(word)
    vocab_embeddings = np.array(vocab_embeddings)
    return vocab_embeddings, words


def create_entities_ft(model, train_word_to_file):
    vocab_embeddings = []
    words = []
    for word in train_word_to_file:
        vocab_embeddings.append(model.get_word_vector(word))
        words.append(word)
    vocab_embeddings = np.array(vocab_embeddings)
    return vocab_embeddings, words



def KMeans_model(vocab_embeddings, rand):
    kmeans = KMeans(n_clusters=20, random_state=rand).fit(vocab_embeddings)
    m_clusters = kmeans.labels_.tolist()
    centers = np.array(kmeans.cluster_centers_)


    indices = []

    for i in range(20):
        center_vec = centers[i]
        data_idx_within_i_cluster = [ idx for idx, clu_num in enumerate(m_clusters) if clu_num == i ]

        one_cluster_tf_matrix = np.zeros((len(data_idx_within_i_cluster) , centers.shape[1]))

        for row_num, data_idx in enumerate(data_idx_within_i_cluster):
            one_row = vocab_embeddings[data_idx]
            one_cluster_tf_matrix[row_num] = one_row


        dist_X =  np.sum((one_cluster_tf_matrix - center_vec)**2, axis = 1)
        topk = min(10, len(data_idx_within_i_cluster))
        topk_vals = dist_X.argsort()[-topk:][::-1].astype(int)
        ind = []
        for i in topk_vals:
            ind.append(data_idx_within_i_cluster[i])

        indices.append(ind)

    return kmeans.labels_, indices



def GMM_model(vocab_embeddings, rand):
    GMM = GaussianMixture(n_components=20, random_state=rand).fit(vocab_embeddings)
    indices = []
    for i in range(GMM.n_components):
        density = scipy.stats.multivariate_normal(cov=GMM.covariances_[i], mean=GMM.means_[i]).logpdf(vocab_embeddings)
        topk_vals = density.argsort()[-10:][::-1]
        ind = []
        for i in topk_vals:
            ind.append(i)

        indices.append(ind)

    return GMM.fit_predict(vocab_embeddings), indices

        #centers[i, :] = X[np.argmax(density)]


def create_vocab_and_files(stopwords, type):
    word_to_file = {}
    train_data = fetch_20newsgroups(data_home='./data/', subset=type, remove=('headers', 'footers', 'quotes'))
    files = train_data['data'];
    print(len(files))
    for file_num in range(0, len(files)):
        words = files[file_num].lower().split()
        for word in words:
            word = word.translate(str.maketrans('', '', string.punctuation))
            word = word.translate(str.maketrans('', '', string.digits))
            if word in stopwords:
                continue
            #word = "/" + word
            if word in word_to_file:
                word_to_file[word].add(file_num)
            else:
                word_to_file[word]= set()
                word_to_file[word].add(file_num)

    for word in list(word_to_file):
        if len(word_to_file[word]) < 5:
            word_to_file.pop(word, None)

    print("Vocab: " + str(len(word_to_file)))

    return word_to_file, len(files)





def npmi(top_k_bins, vocab, files_num):
    e = 10**(-12)
    npmi = np.zeros(20)
    for i in range(20):
        for j in range(len(top_k_bins[i])):
            if(len(top_k_bins[i]) != 10):
                print("error")
            for k in range(j + 1, len(top_k_bins[i])):
                word_j = top_k_bins[i][j]
                word_k = top_k_bins[i][k]
                intersect = list(set(vocab.get(word_j, [])) & set(vocab.get(word_k, [])))

                prob_j = len(vocab.get(word_j, []))/files_num
                prob_k = len(vocab.get(word_k, []))/files_num
                prob_j_k = (len(intersect)/ files_num) + e

                npmi_j_k = (np.log(prob_j_k/(prob_j * prob_k + e)))/ (-1*np.log(prob_j_k))
                npmi[i] = npmi[i] + npmi_j_k


    print(np.mean(npmi))
    return(np.mean(npmi))


if __name__ == "__main__":
    main()