# -*- coding: utf-8 -*-
"""Financial News - Sentiment Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wbjma_ufgTQMZKLsE6yqCzlIsxpNulcc

**Introduction:**
In today's fast-paced financial markets, staying informed about market sentiment is crucial for investors, traders, and financial analysts. Market sentiment, often influenced by financial news, plays a significant role in shaping investor decisions, market predictions, risk management strategies, and understanding market psychology. The project focused on extracting, analyzing, and correlating financial news sentiment with stock market trends, with a particular emphasis on news related to NVIDIA Corporation.

**Motivation:**
My enthusiasm for trading and the stock market has always propelled me towards projects that allow me to integrate my learning with my interests. By analyzing financial news sentiment, I sought to gain insights into its influence on investor decisions, market predictions, and risk management strategies. This project serves as a platform to connect theoretical knowledge with practical applications, fostering a deeper understanding of market psychology and dynamics.

**Problem Statement:**
The core objective of this project revolves around analyzing financial news sentiment and its correlation with stock market trends, particularly focusing on NVIDIA Corporation. By delving into this analysis, I aimed to address fundamental questions:

-How does sentiment in financial news articles impact market sentiment and investor behavior?
-What is the relationship between news sentiment and stock prices, particularly adjusted closing prices?
-Can sentiment analysis of financial news articles provide predictive insights into market movements and trends?

**Methodology:**
Data Collection: I scraped financial news articles related to NVIDIA Corporation from Investing.com, overcoming challenges such as website security measures and changes in website structures.
Text Preprocessing: The scraped news articles underwent preprocessing, including tokenization, stop word removal, and lemmatization, to prepare them for sentiment analysis.
Sentiment Analysis: Utilizing the VADER sentiment analysis tool, I analyzed the sentiment of news articles, obtaining polarity scores for positive, neutral, and negative sentiments.
Correlation Analysis: Correlation matrices were computed to investigate the relationship between news sentiment and stock market data, focusing on adjusted closing prices and trading volume.
Visualization: I visualized the correlations and trends between news sentiment and stock market data through heatmaps and line plots, facilitating the interpretation of analysis results.

Importing Important Libraries
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import urlopen, Request
from urllib.parse import urljoin
import re
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import pyarrow
nltk.download('stopwords')
nltk.download('punkt')

"""**Scraping Financial News:**

The code utilizes the requests library to send HTTP requests to the Investing.com website and fetch the HTML content of the news pages BeautifulSoup from the bs4 (Beautiful Soup 4) package is employed to parse the HTML content and extract relevant information from the webpage, such as titles and links.The find_all() method of BeautifulSoup is utilized to locate all instances of news articles on the page based on specified class attributes. Iterating through multiple pages of news articles is achieved using a loop that generates URLs for different pages and fetches their content.


"""

base_url = "https://www.investing.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
}
href_list = []
title_list = []

for page_number in range(1, 100):
    url = f"https://www.investing.com/equities/nvidia-corp-news/{page_number}"
    req = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    news_instances = soup.find_all('article', class_='flex py-6 sm:flex-row-reverse md:flex-row')

# Iterate through pages 1 to 99
for page_number in range(1, 100):
    url = f"https://www.investing.com/equities/nvidia-corp-news/{page_number}"
    req = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    news_instances = soup.find_all('article', class_='flex sm:flex-row-reverse md:flex-row py-6')

    for instance in news_instances:
        link = instance.find('a', class_='inline-block')
        if link:
            href = link.get('href')
            #print(href)
            if href:
                href = base_url + href
                href_list.append(href)
                title = link.get_text(strip=True)
                title_list.append(title)

"""**Extracting Content and Dates:**

After scraping the links to individual news articles, the code proceeds to extract the content and publication dates of each article. Another round of HTTP requests is made using requests.get() to access the content of each article.
The article content is extracted from HTML elements using BeautifulSoup, focusing on specific classes that contain the textual content of the news.
Dates are extracted similarly, locating the relevant HTML elements containing the publication date information.
"""

# Create a dataframe
data = {'Title': title_list, 'Href': href_list}
news_data = pd.DataFrame(data)

# Add TitleID column
news_data['TitleID'] = news_data.index + 1

# Reorder columns
news_data = news_data[['TitleID', 'Title', 'Href']]

news_data = news_data[~news_data['Href'].str.startswith("https://www.investing.com/pro/offers/breaking")]

news_data.head(20)

"""The extract_content() function encapsulates the essential steps involved in extracting relevant textual information and metadata from financial news articles, contributing to the comprehensive analysis of sentiment in the provided dataset. Its robust design and integration with BeautifulSoup make it a pivotal component in the automated retrieval and preprocessing of news data for sentiment analysis."""

def extract_content(href):
    news_url = href
    req1 = requests.get(url=news_url, headers=headers)
    soup = BeautifulSoup(req1.text, features='html.parser')

    # Extracting content
    article_elements = soup.find_all(class_="WYSIWYG articlePage")
    extracted_text = []

    for element in article_elements:
        p_tags = element.find_all('p')
        for p_tag in p_tags:
            if p_tag.get_text().strip() != "Position added successfully to:":
                extracted_text.append(p_tag.get_text())

    content = '\n'.join(extracted_text)

    # Extracting date and time
    pub_date_elements = soup.find_all('div', {'class': "contentSectionDetails"})
    date = None
    time = None

    if len(pub_date_elements) == 2:
        date_time_text = pub_date_elements[1].span.text.strip()
        date = date_time_text.split()[1:4]
        time = date_time_text.split()[4:5]
    elif len(pub_date_elements) == 1:
        date_time_text = pub_date_elements[0].span.text.strip()
        date = date_time_text.split()[1:4]
        time = date_time_text.split()[4:5]

    return content, date, time

for index, row in news_data.iterrows():
    content,date,time = extract_content(row['Href'])
    date = ' '.join(date)
    date_object = datetime.strptime(date, '%b %d, %Y').date()
    time_obj = ' '.join(time)
    news_data.at[index, 'Content'] = content
    news_data.at[index, 'Date']=date_object
    news_data.at[index, 'Time']=time_obj

news_data.tail(100)

news_data.to_csv('news_data.csv', index=False)

news_data = pd.read_csv('/content/news_data.csv')

news_data.TitleID=news_data.index + 1

"""**Text Preprocessing:**

Text preprocessing involves cleaning and preparing the extracted content for sentiment analysis. The nltk package is used for text preprocessing tasks such as tokenization, stop word removal, and lemmatization.nltk.tokenize.WhitespaceTokenizer is employed for tokenizing the text into individual words. Stop words (commonly occurring words with little semantic value) are removed using nltk.corpus.stopwords. Lemmatization is performed using nltk.stem.WordNetLemmatizer to reduce words to their base or dictionary form.
"""

from nltk.tokenize import WhitespaceTokenizer
from nltk.stem import WordNetLemmatizer
def clean_text(text):
    text = str(text)

    # Initialize lemmatizer and tokenizer
    lemmatizer = WordNetLemmatizer()
    word_tokens = word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in word_tokens if word.lower() not in stop_words]

    # Lemmatize tokens
    lemmatized_tokens = [lemmatizer.lemmatize(word) for word in filtered_tokens]

    # Join lemmatized tokens into a single string
    cleaned_text = ' '.join(lemmatized_tokens)

    return cleaned_text

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('vader_lexicon')

news_data['Cleaned_Content'] = news_data['Content'].apply(clean_text)

news_data.head(5)

print(news_data.Cleaned_Content[1])
print("*************************************************************************")
print(news_data.Content[1])

"""**Sentiment Analysis:**

The sentiment analysis is conducted using the VADER (Valence Aware Dictionary and sEntiment Reasoner) sentiment analysis tool from the nltk.sentiment.vader module.
VADER is specifically designed for analyzing sentiment in text data and provides polarity scores for negative, neutral, positive, and compound sentiments.
The SentimentIntensityAnalyzer class from VADER is utilized to compute sentiment scores for each news article.
"""

def analyze_sentiment(content):
    sid = SentimentIntensityAnalyzer()
    scores = sid.polarity_scores(content)
    return scores

# Apply sentiment analysis to the Content column
sentiment_scores = news_data['Content'].apply(analyze_sentiment)

# Convert sentiment scores to DataFrame and concatenate it with the original DataFrame
sentiment_df = pd.DataFrame(sentiment_scores.tolist())
news_data = pd.concat([news_data, sentiment_df], axis=1)

# Print the DataFrame with sentiment scores
news_data.head(5)

news_data.head(5)

agg_sentiment = news_data.groupby('Date').agg({'neg': 'mean', 'neu': 'mean', 'pos': 'mean', 'compound': 'mean'})
agg_sentiment.reset_index(inplace=True)

agg_sentiment.head(5)

stock_price_data = pd.read_csv('/content/NVDA.csv')
#stock_price_data = stock_price_data.sort_values(by='Date', ascending=False)

stock_price_data.head(20)

analysis_data = pd.merge(agg_sentiment, stock_price_data, on='Date', how='inner')
analysis_data.head(10)

"""**Correlation Analysis:**

Sentiment scores are aggregated by date, and correlation matrices are calculated to analyze the relationship between news sentiment and stock market trends.
The pandas package is used extensively for data manipulation and aggregation tasks.
Correlation coefficients are calculated using the corr() method in pandas to quantify the degree of linear relationship between sentiment scores and stock prices or trading volume.
"""

import matplotlib.pyplot as plt
import seaborn as sns


# Calculate correlation matrices
sentiment_corr = analysis_data[['Adj Close', 'neg', 'neu', 'pos', 'compound']].corr()
volume_corr = analysis_data[['Volume', 'neg', 'neu', 'pos', 'compound']].corr()

# Plotting
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Plot correlation between Adj Close and sentiment scores
sns.heatmap(sentiment_corr, annot=True, cmap='coolwarm', ax=axes[0])
axes[0].set_title('Correlation between Adj Close and sentiment scores')

# Plot correlation between Adj Close and volume
sns.heatmap(volume_corr, annot=True, cmap='coolwarm', ax=axes[1])
axes[1].set_title('Correlation between Adj Close and volume')

plt.tight_layout()
plt.show()

"""**Plotting Graphs:**

Visualization of the results is performed using matplotlib and seaborn for creating informative plots.
Heatmaps are generated to visualize correlations between sentiment scores and stock prices or trading volume.
Line plots are created to compare sentiment scores with stock prices and trading volume over time, providing insights into potential relationships between news sentiment and market activity.
"""

import matplotlib.pyplot as plt

last_10_days_df = analysis_data.tail(30)
# Create a figure and axis objects
fig, ax1 = plt.subplots()


ax1.plot(last_10_days_df['Date'], last_10_days_df['compound'], color='blue', label='Neutral Sentiment')

ax1.set_xlabel('Date')
ax1.set_ylabel('Sentiment Score')
ax1.tick_params(axis='x', rotation=45)
ax1.legend(loc='upper left')

# Create a second y-axis for stock prices
ax2 = ax1.twinx()
ax2.plot(last_10_days_df['Date'], last_10_days_df['Adj Close'], color='black', linestyle='--', label='Volume')
ax2.set_ylabel('Adj Close')
ax2.legend(loc='upper right')

# Set title and show plot
plt.title('Sentiment Score vs. Stock Price')
plt.show()

last_10_days_df = analysis_data.tail(30)
# Create a figure and axis objects
fig, ax1 = plt.subplots()


ax1.plot(last_10_days_df['Date'], last_10_days_df['neg'], color='blue', label='Negative Sentiment')

ax1.set_xlabel('Date')
ax1.set_ylabel('Sentiment Score')
ax1.tick_params(axis='x', rotation=45)
ax1.legend(loc='upper left')

# Create a second y-axis for stock prices
ax2 = ax1.twinx()
ax2.plot(last_10_days_df['Date'], last_10_days_df['Volume'], color='black', linestyle='--', label='Volume')
ax2.set_ylabel('Volume')
ax2.legend(loc='upper right')

# Set title and show plot
plt.title('Sentiment Score vs. Volume')
plt.show()

"""**Important Learnings and Insights:**
Financial news sentiment significantly influences market sentiment and investor behavior, driving market dynamics and stock price movements.
Neutral sentiment in news articles exhibits a strong correlation with adjusted closing prices, indicating its importance in market predictions and trends.
Negative sentiment tends to trigger higher trading volume, reflecting intensified investor activity in response to negative news events.
Incorporating sentiment analysis into market analysis strategies enhances decision-making processes and risk management practices, offering valuable insights for investors and traders.

**Challenges:**
Scraping financial news data posed challenges due to website security measures and the dynamic nature of website structures, necessitating adaptability and persistence in data collection efforts.
Ensuring the accuracy and reliability of sentiment analysis results required meticulous preprocessing of text data and selection of appropriate sentiment analysis tools.
Interpreting correlations between news sentiment and stock market trends demanded consideration of various influencing factors and market dynamics, highlighting the complexity of market analysis.

**Future Scope:**
Exploring advanced sentiment analysis techniques, such as deep learning models, to enhance the accuracy and granularity of sentiment analysis results.
Integrating additional data sources, such as social media sentiment and company-specific metrics, to enrich the analysis and prediction of market trends.
Conducting longitudinal studies to examine the long-term impact of news sentiment on stock prices and investor sentiment, providing insights into market behavior over time.
Implementing real-time sentiment analysis capabilities to enable timely decision-making and proactive risk management in dynamic market environments.
In conclusion, this project serves as a testament to the intricate interplay between financial news sentiment, market dynamics, and investor behavior. By dissecting and analyzing news sentiment, I have gained valuable insights into the driving forces behind market movements, empowering me with knowledge and understanding to navigate the complexities of the financial markets with confidence and proficiency.
"""