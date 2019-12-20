# -*- coding: utf-8 -*-
"""
Created on Mon Dec  9 16:31:48 2019

@author: rohit.wardole
"""

import pandas as pd

df = pd.read_csv("twitterBot_NoBot.csv")

from nltk.sentiment.util import mark_negation
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
tfidf = TfidfVectorizer(analyzer="word",ngram_range=(1, 2),tokenizer=lambda text: mark_negation(word_tokenize(text)),preprocessor=lambda text: text.replace("<br />", " "))
X = tfidf.fit_transform(df['tweet'])
y = df['Bot_NoBot'].values

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state = 48)

# =============================================================================
from sklearn.linear_model import LogisticRegression 
classifier = LogisticRegression(penalty='l1',solver='saga',C=4.0,max_iter=5000)
classifier.fit(X_train,y_train)

y_pred = classifier.predict(X_test)

from sklearn.metrics import accuracy_score
print('accuracy for Logistic Regression :',accuracy_score(y_test,y_pred)) 
#accuracy for Logistic Regression : 0.7624821683309557
# =============================================================================
# Fitting K-NN to the Training set
from sklearn.neighbors import KNeighborsClassifier
classifier = KNeighborsClassifier(n_neighbors = 5, metric = 'minkowski', p = 2)
classifier.fit(X_train, y_train)

y_pred = classifier.predict(X_test)

from sklearn.metrics import accuracy_score
print('accuracy for KNN :',accuracy_score(y_test,y_pred)) 
#accuracy for KNN : 0.6676176890156919
# =============================================================================
# Fitting SVM to the Training set
from sklearn.svm import SVC
classifier = SVC(kernel = 'linear', random_state = 0)
classifier.fit(X_train, y_train)

# Predicting the Test set results
y_pred = classifier.predict(X_test)

from sklearn.metrics import accuracy_score
print('accuracy for SVM :',accuracy_score(y_test,y_pred))
#accuracy for SVM : 0.7667617689015692 
# =============================================================================

# Fitting Decision Tree Classification to the Training set
from sklearn.tree import DecisionTreeClassifier
classifier = DecisionTreeClassifier(criterion = 'entropy', random_state = 0)
classifier.fit(X_train, y_train)

# Predicting the Test set results
y_pred = classifier.predict(X_test)

from sklearn.metrics import accuracy_score
print('accuracy for Decision Tree :',accuracy_score(y_test,y_pred))
#accuracy for Decision Tree : 0.7018544935805991
# =============================================================================

# Fitting Random Forest Classification to the Training set
from sklearn.ensemble import RandomForestClassifier
classifier = RandomForestClassifier(n_estimators = 20, criterion = 'entropy', random_state = 0)
classifier.fit(X_train, y_train)

# Predicting the Test set results
y_pred = classifier.predict(X_test)

from sklearn.metrics import accuracy_score
print('accuracy for Random Forest :',accuracy_score(y_test,y_pred))
#accuracy for Random Forest : 0.7624821683309557
# =============================================================================

test_sentence = ["""its raining in delhi... winter finally arrived...."""]
X_new = tfidf.transform(test_sentence)
new_pred = classifier.predict(X_new)
new_prob = classifier.predict_proba(X_new)
result = new_prob[-1:]

print("Bot: " , result[0][0] * 100)
print("Human: " , result[0][1] * 100)

# =============================================================================
# Word Cloud for Bot
# =============================================================================
df_bot = df[df['Bot_NoBot'] == 'Bot']
from wordcloud import WordCloud, STOPWORDS 
import matplotlib.pyplot as plt 
import pandas as pd

comment_words = ' '
stopwords = set(STOPWORDS) 

for val in df_bot.tweet:       
    # typecaste each val to string 
    val = str(val)   
    # split the value 
    tokens = val.split()       
    # Converts each token into lowercase 
    for i in range(len(tokens)): 
        tokens[i] = tokens[i].lower() 
          
    for words in tokens: 
        comment_words = comment_words + words + ' '
        
wordcloud = WordCloud(width = 800, height = 800, background_color ='white', stopwords = stopwords, min_font_size = 10).generate(comment_words)         

# plot the WordCloud image                        
plt.figure(figsize = (8, 8), facecolor = None) 
plt.imshow(wordcloud) 
plt.axis("off") 
plt.tight_layout(pad = 0) 
plt.show()

# =============================================================================
# Word Cloud for Non-Bot
# =============================================================================
df_NoBot = df[df['Bot_NoBot'] == 'NoBot']
from wordcloud import WordCloud, STOPWORDS 
import matplotlib.pyplot as plt 
import pandas as pd

comment_words = ' '
stopwords = set(STOPWORDS) 

for val in df_NoBot.tweet:       
    # typecaste each val to string 
    val = str(val)   
    # split the value 
    tokens = val.split()       
    # Converts each token into lowercase 
    for i in range(len(tokens)): 
        tokens[i] = tokens[i].lower() 
          
    for words in tokens: 
        comment_words = comment_words + words + ' '
        
wordcloud = WordCloud(width = 800, height = 800, background_color ='white', stopwords = stopwords, min_font_size = 10).generate(comment_words)         

# plot the WordCloud image                        
plt.figure(figsize = (8, 8), facecolor = None) 
plt.imshow(wordcloud) 
plt.axis("off") 
plt.tight_layout(pad = 0) 
plt.show()
