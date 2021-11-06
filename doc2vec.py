# -*- coding: utf-8 -*-
"""doc2vec.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CcVGroSRgPWf3UFdN7maS65bZM3JUb9y
"""

from __future__ import absolute_import,division,print_function
import codecs#encoding,word embedding
import glob#find all filenames matching a pattern
import logging#log events for libraries
import multiprocessing#concurrency
import os#dealing with operating system like reading file
import pprint#pretty print, human readable
import re#regular expression
import nltk#natural language toolkit
import gensim.models.word2vec as w2v#word2vec
import sklearn.manifold#dimensionality reduction
import numpy as np#math
import matplotlib.pyplot#plotting
import pandas as pd#parse dataset
import seaborn as sns#visualization
from sklearn.decomposition import PCA
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

#process our data
#clean data
#stopwords like the at a an, unnecesasry
#tokenization into sentences, punkt 
#http://www.nltk.org/
nltk.download("punkt")#pretrained tokenizer
nltk.download("stopwords")#words like,and,the,an,of,a

#get the paper names,matching text files
doc_filenames = sorted(glob.glob("/content/Data/*.txt"))
doc_filenames

#step 1 process data
#initialize rawunicode , we'll add all text to a big file in memory
corpus_raw = u""
#for each book, read it, open it un utf 8 format, 
#add it to the raw corpus
for doc in doc_filenames:
    print("Reading '{0}'...".format(doc))
    with codecs.open(doc, "r", "utf-8") as docs:
        corpus_raw += docs.read()
    print("Corpus is now {0} characters long".format(len(corpus_raw)))
    print()

#tokenizastion! saved the trained model here
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

#tokenize into sentences
raw_sentences = tokenizer.tokenize(corpus_raw)

#convert into list of words
#remove unecessary characters, split into words, no hyhens and shit
#split into words
def sentence_to_wordlist(raw):
    clean = re.sub("[^a-zA-Z]"," ", raw)
    words = clean.split()
    return words

#for each sentece, sentences where each word is tokenized
sentences = []
for raw_sentence in raw_sentences:
    if len(raw_sentence) > 0:
        sentences.append(sentence_to_wordlist(raw_sentence))

#print an example
print(raw_sentences[3])
print(sentence_to_wordlist(raw_sentences[5]))

#count tokens, each one being a sentence
token_count = sum([len(sentence) for sentence in sentences])
print("The book corpus contains {0:,} tokens".format(token_count))

#ONCE we have vectors
#step 3 - build model
#3 main tasks that vectors help with
#DISTANCE, SIMILARITY, RANKING

# Dimensionality of the resulting word vectors.
#more dimensions, more computationally expensive to train
#but also more accurate
#more dimensions = more generalized
num_features = 300
# Minimum word count threshold.
min_word_count = 3

# Number of threads to run in parallel.
#more workers, faster we train
num_workers = multiprocessing.cpu_count()

# Context window length.
context_size = 7

# Downsample setting for frequent words.
#0 - 1e-5 is good for this
downsampling = 1e-3

# Seed for the RNG, to make the results reproducible.
#random number generator
#deterministic, good for debugging
seed = 1

thrones2vec = w2v.Word2Vec(
    sg=1,
    seed=seed,
    workers=num_workers,
    size=num_features,
    min_count=min_word_count,
    window=context_size,
    sample=downsampling
)

thrones2vec.build_vocab(sentences)

print("Word2Vec vocabulary length:", len(thrones2vec.wv.vocab))

thrones2vec.train(sentences, total_examples=thrones2vec.corpus_count , epochs=100)

#save model
if not os.path.exists(os.path.join("trained",'sample')):
    os.makedirs(os.path.join("trained",'sample'))

thrones2vec.save(os.path.join("trained", "thrones2vec.w2v"))

#load model
thrones2vec = w2v.Word2Vec.load(os.path.join("trained", "thrones2vec.w2v"))

#squash dimensionality to 2,,t-SNE is a tool for data visualization
from sklearn.preprocessing import StandardScaler
tsne = sklearn.manifold.TSNE(n_components=2, random_state=0)

#put it all into a big matrix
all_word_vectors_matrix = thrones2vec.wv.vectors

#train t sne
all_word_vectors_matrix_2d = tsne.fit_transform(all_word_vectors_matrix)

#plot point in 2d space
points = pd.DataFrame(
    [ 
        (word, coords[0], coords[1])
        for word, coords in [
            (word, all_word_vectors_matrix_2d[thrones2vec.wv.vocab[word].index])
            for word in thrones2vec.wv.vocab
        ]
    ],
    columns=["word", "x", "y"]
)

points.head(1000)

#plot
sns.set_context("poster")

points.tail(1000)

ax=points.plot.scatter("x", "y", s=10, figsize=(20, 12))

#distance,similarity and ranking
def plot_region(x_bounds, y_bounds):
    slice = points[
        (x_bounds[0] <= points.x) &
        (points.x <= x_bounds[1]) & 
        (y_bounds[0] <= points.y) &
        (points.y <= y_bounds[1])
    ]
    
    ax = slice.plot.scatter("x", "y", s=35, figsize=(10, 8))
    for i, point in slice.iterrows():
        ax.text(point.x + 0.005, point.y + 0.005, point.word, fontsize=11)

plot_region(x_bounds=(4, 30), y_bounds=(-0.5, -0.1))

plot_region(x_bounds=(0, 8), y_bounds=(4, 7))

thrones2vec.wv.most_similar("thousand")

thrones2vec.wv.most_similar("88")

thrones2vec.wv.most_similar("people")

thrones2vec.wv.most_similar("tennis")

thrones2vec.wv.most_similar("match")

thrones2vec.wv.most_similar("the")

thrones2vec.wv.most_similar("plastic")

thrones2vec.wv.most_similar("container")

thrones2vec.wv.most_similar("see")

thrones2vec.wv.most_similar("img")

thrones2vec.wv.most_similar("src")

thrones2vec.wv.most_similar("drawing.jpg")

thrones2vec.wv.most_similar("alt")

! pip freeze -r req.txt

points.to_csv("/content/final.csv")