import requests
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from datetime import datetime

API_KEY = '502SQHC4SU99N03B'
BASE_URL = 'https://www.alphavantage.co/query'
FUNCTION = 'NEWS_SENTIMENT'

def get_news_data(ticker):
    params = {
        'function': FUNCTION,
        'tickers': ticker,
        'apikey': API_KEY,
    }

    try:
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            news_data = response.json()
            return news_data.get('feed', [])
        else:
            return []
    except requests.RequestException:
        return []

def process_news_data(news_items, ticker):
    titles, published_dates, urls, sentiment_labels, sentiment_scores, relevance_scores = [], [], [], [], [], []

    for news in news_items:
        news_time = datetime.strptime(news.get('time_published'), "%Y%m%dT%H%M%S")
        for ticker_info in news.get('ticker_sentiment', []):
            if ticker_info['ticker'] == ticker:
                titles.append(news.get('title'))
                published_dates.append(news_time)
                urls.append(news.get('url'))
                sentiment_labels.append(ticker_info.get('ticker_sentiment_label'))
                sentiment_scores.append(float(ticker_info.get('ticker_sentiment_score')))
                relevance_scores.append(float(ticker_info.get('relevance_score')))

    df = pd.DataFrame({
        'Title': titles,
        'Published Date': published_dates,
        'URL': urls,
        'Sentiment Label': sentiment_labels,
        'Sentiment Score': sentiment_scores,
        'Relevance Score': relevance_scores
    })
    return df

def plot_scores(df):
    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [
        '#8B0000' if row['Sentiment Score'] < 0 and row['Relevance Score'] > 0.5 else
        '#023859' if row['Sentiment Score'] > 0 and row['Relevance Score'] > 0.5 else
        '#FF6F6F' if row['Sentiment Score'] <= 0 and row['Relevance Score'] <= 0.5 else
        '#7EC8E3'
        for _, row in df.iterrows()
    ]
    ax.scatter(df['Sentiment Score'], df['Relevance Score'], c=colors)
    ax.set_title('Sentiment vs Relevance')
    ax.set_xlabel('Sentiment Score')
    ax.set_ylabel('Relevance Score')
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylim(0, 1)
    ax.axhline(y=0.5, color='black', linestyle='--', linewidth=1)
    ax.axvline(x=0, color='black', linestyle='--', linewidth=1)
    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    
    return plot_url