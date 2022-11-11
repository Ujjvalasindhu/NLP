# -*- coding: utf-8 -*-
"""Team13codefinal.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1soL2bsd3aZ9Wfr3AtD5JVMvbKK5ZUezn
"""

# Commented out IPython magic to ensure Python compatibility.
#  %%capture
!pip install tensorflow_text==2.6.0

import os 
os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'



# Commented out IPython magic to ensure Python compatibility.
from tqdm import tqdm
import numpy as np
import pandas as pd 
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import plotly.express as px

from numpy import newaxis
from wordcloud import WordCloud, STOPWORDS

from tqdm import tqdm

from sklearn import preprocessing, decomposition, model_selection, metrics, pipeline
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import TruncatedSVD

from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression

import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from string import punctuation

import xgboost as xgb
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, Bidirectional, Activation, GRU, BatchNormalization
from tensorflow.keras.layers import GlobalMaxPooling1D, Conv1D, MaxPooling1D, Flatten, Bidirectional, SpatialDropout1D
from tensorflow.keras.layers import Embedding
from tensorflow.keras.preprocessing import sequence, text
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau

from tensorflow.keras.optimizers import Adam

# %matplotlib inline
sns.set(style='whitegrid', palette='muted', font_scale=1.2)

plt.rcParams['figure.figsize'] = 12, 8

RANDOM_SEED = 42
nltk.download('stopwords')
stop_words = stopwords.words('english')

module_url = 'https://tfhub.dev/google/universal-sentence-encoder-multilingual-large/3'
use = hub.load(module_url)

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
df_reviews = pd.read_csv("/content/drive/MyDrive/goodreads_train.csv")
df_reviews

df_reviews=df_reviews.drop(columns=['user_id', 'book_id','review_id' ,'date_added', 'date_updated', 'read_at', 'started_at','n_votes','n_comments'], axis=0)
df_reviews

df_reviews.drop(df_reviews.index[100000:900000], inplace=True)
df_reviews

df_reviews["review_type"] = df_reviews["rating"].apply(
    lambda x: "very bad" if x == 0 else "bad" if x==1 else "good" if x==2 else "very good" if x==3 else "excelent")
df_reviews.rename(columns = {'review_text':'review'}, inplace = True)
df_reviews



import re
df = df_reviews
def text_to_wordlist(text, remove_stopwords=False, stem_words=False):
    text = text.lower().split()
    if remove_stopwords:
        stops = set(stopwords.words("english"))
        text = [w for w in text if not w in stops]
    
    text = " ".join(text)
    text = re.sub(r"[^A-Za-z0-9^,!.\/'+-=]", " ", text)
    text = re.sub(r"what's", "what is ", text)
    text = re.sub(r"\'s", " ", text)
    text = re.sub(r"\'ve", " have ", text)
    text = re.sub(r"can't", "cannot ", text)
    text = re.sub(r"n't", " not ", text)
    text = re.sub(r"i'm", "i am ", text)
    text = re.sub(r"\'re", " are ", text)
    text = re.sub(r"\'d", " would ", text)
    text = re.sub(r"\'ll", " will ", text)
    text = re.sub(r",", " ", text)
    text = re.sub(r"\.", " ", text)
    text = re.sub(r"!", " ! ", text)
    text = re.sub(r"\/", " ", text)
    text = re.sub(r"\^", " ^ ", text)
    text = re.sub(r"\+", " + ", text)
    text = re.sub(r"\-", " - ", text)
    text = re.sub(r"\=", " = ", text)
    text = re.sub(r"'", " ", text)
    text = re.sub(r":", " : ", text)
    text = re.sub(r" e g ", " eg ", text)
    text = re.sub(r" b g ", " bg ", text)
    text = re.sub(r"\0s", "0", text)
    text = re.sub(r"e - mail", "email", text)
    text = re.sub(r"\s{2,}", " ", text)
    
    if stem_words:
        text = text.split()
        stemmer = SnowballStemmer('english')
        stemmed_words = [stemmer.stem(word) for word in text]
        text = " ".join(stemmed_words)
    
    return(text)

data = df.copy()
data['review'] = data['review'].apply((lambda x: re.sub('RT ','',x)))
cleanedText = []
for text in data["review"].values:
    text = text+" "
    text = re.sub(r'https?:\/\/.*[\r\n]*', ' ', text, flags=re.MULTILINE)
    text = re.sub(r'(@){1}.+?( ){1}', ' ', text, flags=re.MULTILINE)
    text = re.sub(r'(#){1}.+?( ){1}', ' ', text, flags=re.MULTILINE)
    cleanedText.append(text_to_wordlist(text))
data['cleanedText'] = cleanedText

data.head(15)

data.drop(columns=['review'],axis=1, inplace=True)
data.rename(columns = {'cleanedText':'review'}, inplace = True)
df_reviews = data
df_reviews

fig = px.histogram(df_reviews, x="review_type", title='how good the book is', text_auto=True)
fig.show()

excelent_reviews = df_reviews[df_reviews.review_type == "excelent"]
very_good_reviews = df_reviews[df_reviews.review_type == "very good"]
good_reviews = df_reviews[df_reviews.review_type == "good"]
bad_reviews = df_reviews[df_reviews.review_type == "bad"]
very_bad_reviews = df_reviews[df_reviews.review_type == "very_bad"]

excelent_reviews_text = " ".join(excelent_reviews.review.to_numpy().tolist())
very_good_reviews_text = " ".join(very_good_reviews.review.to_numpy().tolist())
good_reviews_text = " ".join(good_reviews.review.to_numpy().tolist())
bad_reviews_text = " ".join(bad_reviews.review.to_numpy().tolist())
very_bad_reviews_text = " ".join(very_bad_reviews.review.to_numpy().tolist())

excelent_df = excelent_reviews.sample(n=len(very_good_reviews)+len(good_reviews)+len(bad_reviews)+len(very_bad_reviews), random_state=RANDOM_SEED, replace=True)

excelent_df = excelent_df.append(very_good_reviews).reset_index(drop=True)
excelent_df = excelent_df.append(good_reviews).reset_index(drop=True)
excelent_df = excelent_df.append(bad_reviews).reset_index(drop=True)
df_review_resampled = excelent_df.append(very_bad_reviews).reset_index(drop=True)
#df_review_resampled = excelent_df.extend(very_good_reviews,good_reviews,bad_reviews,very_bad_reviews).reset_index(drop=True)
df_review_resampled.shape

df_review_resampled

label_enc = preprocessing.LabelEncoder()
encoded_review = label_enc.fit_transform(df_review_resampled.review_type.values)

train_reviews, test_reviews, y_train, y_test = train_test_split(
    df_review_resampled.review, 
    encoded_review, 
    test_size=0.25, 
    random_state=RANDOM_SEED
  )

X_train = []
for r in tqdm(train_reviews):
    emb = use(r)
    review_emb = tf.reshape(emb, [-1]).numpy()
    X_train.append(review_emb)

X_train = np.array(X_train)

X_test = []
for r in tqdm(test_reviews):
    emb = use(r)
    review_emb = tf.reshape(emb, [-1]).numpy()
    X_test.append(review_emb)

X_test = np.array(X_test)

print(X_train.shape, X_test.shape)

print(y_train.shape, y_test.shape)



def plot_history(history):
    accuracy = history.history['accuracy']
    val_accuracy= history.history['val_accuracy']
    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs = range(1, len(accuracy) + 1)
    plt.plot(epochs, accuracy, 'bo', label='Training accuracy')
    plt.plot(epochs, val_accuracy, 'b', label='Validation accuracy')

    plt.title('Training and validation accuracy')
    plt.legend()
    plt.figure()

    plt.plot(epochs, loss, 'bo', label='Training loss')
    plt.plot(epochs, val_loss, 'b', label='Validation loss')
    plt.title('Training and validation loss')
    plt.legend()
    plt.show()

    
def plot_model(model):
    model.summary()
    return tf.keras.utils.plot_model(
    model,
    to_file="model.png",
    show_shapes=True,
    show_dtype=False,
    show_layer_names=True,
    rankdir="TB",
    expand_nested=True,
    dpi=96,
    layer_range=None,
    )

y_train.shape

X_train_reshaped = X_train[:, newaxis,:]
X_test_reshaped = X_test[:, newaxis,:]

X_train_reshaped.shape

# input_shape
1,X_train_reshaped.shape[2]

def build_model_lstm():
    model = Sequential()
    model.add(LSTM(512, activation='sigmoid', return_sequences=True,
                 input_shape=(1,X_train_reshaped.shape[2])
                 ))
   # model.add(SpatialDropout1D(0.2))
    #model.add(LSTM(256, dropout=0.2))
    #model.add(LSTM(128, dropout=0.2))
    model.add(LSTM(256, dropout=0.2, activation='sigmoid', return_sequences=True))
    model.add(LSTM(128, dropout=0.2, activation='sigmoid', return_sequences=True))
    model.add(Dense(34, activation='tanh'))
    model.add(Dense(32, activation='tanh'))
    model.add(Dense(5, activation='softmax'))

    model.compile(loss='sparse_categorical_crossentropy',
            metrics=['accuracy'],
            optimizer=Adam(learning_rate=0.0005))
    return model

model_lstm = build_model_lstm()

plot_model(model_lstm)

# Commented out IPython magic to ensure Python compatibility.
# %%time
# history = model_lstm.fit(
#     X_train_reshaped, y_train, 
#     epochs=30, 
#     batch_size=10, 
#     validation_split=0.1, 
#     verbose=1, 
#     shuffle=True
# )

model_lstm.evaluate(X_test_reshaped, y_test)

model_lstm.save("lstm_sentiment_model9.h5")
model_lstm.save("/content/drive/MyDrive/lstm_sentiment_model9.h5")