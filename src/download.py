"""
I want to create a python script to download html from a website. The website's URL is "https://www.philosophizethis.org/transcripts". The website links out to transcripts with urls like https://www.philosophizethis.org/transcript/episode-191-transcript
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
import time
import tqdm

START_TIME = datetime.now().strftime("%m%d%Y_%H%M")
DATA_DIR = f'C:\\Users\\David\\Documents\\Projects\\podcast-bot\\data\\{START_TIME}\\'


def extract_transcript(html_content):
    """
    Extracts text from all <p> elements within a <div> with the class "blog-item-content-wrapper".

    Parameters:
    html_content (str): The HTML content of the page.

    Returns:
    list: A list containing the text from each <p> element.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    text_array = []

    # Find the div with the class 'blog-item-content-wrapper'
    div = soup.find('div', class_='blog-item-content-wrapper')
    if div:
        # Find all <p> elements within this div and extract their text
        paragraphs = div.find_all('p')
        for p in paragraphs:
            text_array.append(p.get_text())

    return text_array


def get_number(href) -> int:
    pattern = re.compile(r'/transcript/.*-(\d{1,3})-')
    numbers = re.findall(pattern, href)
    if len(numbers) > 0:
        return int(numbers[0])
    return None


def valid_transcript(href: str) -> bool:
    pattern = re.compile(r'/transcript/.*-\d{1,3}-')
    number = re.search(pattern, href)
    return number is not None

# Send a GET request and parse the HTML content if successful
BASE_URL = 'https://www.philosophizethis.org'
response = requests.get(BASE_URL + '/transcripts')
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    pattern = re.compile(r'/transcript/.*-\d{1,3}-')
    transcript_urls = [BASE_URL + link.get('href') for link in soup.find_all('a', href=pattern)]
    print(transcript_urls)

    for link in tqdm.tqdm(transcript_urls):
        if not valid_transcript(link):
            continue

        response = requests.get(link)
        if response.status_code != 200:
            print('couldnt download',link)
            time.sleep(3)
            continue

        transcript = extract_transcript(response.text)

        if not os.path.isdir(DATA_DIR):
            os.mkdir(DATA_DIR)
        
        number = get_number(link)
        
        with open(os.path.join(DATA_DIR, f'pod-{number}.txt'), 'w') as f:
            f.writelines(transcript)
        
        time.sleep(.1)
        
else:
    print("Failed to retrieve the main page. Status code:", response.status_code)


