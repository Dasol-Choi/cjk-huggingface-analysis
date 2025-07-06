import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time
import json
import datetime

API_TOKEN = ""
BASE_URL = "https://huggingface.co/datasets"
API_URL = "https://huggingface.co/api/datasets"
lang = 'zh'

def get_datasets_from_page(page_num):
    url = f"{BASE_URL}?modality=modality:text&language=language:{lang}&sort=downloads&p={page_num}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    dataset_links = soup.select('a[href^="/datasets/"]')
    dataset_ids = []

    for link in dataset_links:
        href = link['href'].strip('/')
        if href.startswith('datasets/'):
            dataset_id = href.replace('datasets/', '')
            if dataset_id not in dataset_ids:
                dataset_ids.append(dataset_id)

    return dataset_ids

def extract_size_categories(soup):
    size_info = {}

    try:
        header_props = json.loads(soup.find('div', {'data-target': 'DatasetHeader'})['data-props'])
        dataset_data = header_props.get('dataset', {})
        card_data = dataset_data.get('cardData', {})

        size_categories = card_data.get('size_categories', [])
        if size_categories:
            size_info['size_categories'] = '|'.join(size_categories)

        dataset_info = card_data.get('dataset_info', [])
        for config in dataset_info:
            config_name = config.get('config_name')
            if config_name:
                dataset_size = config.get('dataset_size')
                if dataset_size:
                    size_info[f'config_{config_name}'] = dataset_size
    except Exception as e:
        print(f"Error extracting size info: {e}")

    return size_info

def get_dataset_info(dataset_id, max_retries=3):
    headers = {"Authorization": f"Bearer {API_TOKEN}"}
    api_url = f"{API_URL}/{dataset_id}"

    for attempt in range(max_retries):
        try:
            response = requests.get(api_url, headers=headers)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            api_info = response.json()
            break
        except requests.exceptions.RequestException:
            if attempt == max_retries - 1:
                return None
            time.sleep(1 * (attempt + 1))

    web_url = f"{BASE_URL}/{dataset_id}"
    try:
        response = requests.get(web_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        arxiv_link = soup.find('a', href=lambda href: href and 'arxiv.org/abs/' in href)
        if arxiv_link:
            arxiv_id = arxiv_link['href'].split('/')[-1]
        else:
            arxiv_id = None

        header_props = json.loads(soup.find('div', {'data-target': 'DatasetHeader'})['data-props'])
        dataset_data = header_props.get('dataset', {})
        card_data = dataset_data.get('cardData', {})

        tasks = card_data.get('task_categories', []) + card_data.get('task_ids', [])
        languages = card_data.get('language', [])
        license_info = card_data.get('license', [])
        if isinstance(license_info, list):  
            license_value = license_info[0] if license_info else None
        elif isinstance(license_info, str):  
            license_value = license_info
        else:  
            license_value = None
        size_info = extract_size_categories(soup)
        downloads = dataset_data.get('downloads', 0)
        downloads_alltime = dataset_data.get('downloadsAllTime', 0)
        likes = dataset_data.get('likes', 0)

        api_info.update({
            'tasks': tasks,
            'languages': languages,
            'license': license_value,
            'size_info': size_info,
            'downloads': downloads,
            'downloads_alltime': downloads_alltime,
            'likes': likes,
            'arxiv_id': arxiv_id
        })

    except Exception as e:
        print(f"Error scraping webpage for {dataset_id}: {e}")

    return api_info

def process_dataset_info(info):
    if not info:
        return None

    def clean_text(text):
        if not isinstance(text, str):
            text = str(text)
        return ' '.join(text.replace('\n', ' ').replace('\t', ' ').replace(';', ' ').split())

    created_at = None
    if '_id' in info:
        try:
            timestamp_hex = info['_id'][:8]
            timestamp = int(timestamp_hex, 16)
            created_at = datetime.datetime.fromtimestamp(timestamp).isoformat()
        except Exception as e:
            print(f"Error extracting created_at from _id: {e}")

    languages = info.get('languages', [])
    if not languages:
        language_category = 'None'
    else:
        real_langs = [lang for lang in languages if 'code' not in lang.lower()]
        num_langs = len(real_langs)

        if num_langs == 0:
            language_category = 'None'
        elif num_langs == 1:
            language_category = 'mono'
        elif num_langs == 2:
            language_category = 'bi'
        else:
            language_category = 'multi'

    return {
        'id': clean_text(info.get('id', 'None')),
        'author': clean_text(info.get('author', 'None')),
        'created_at': created_at or 'None',
        'lastModified': clean_text(info.get('lastModified', 'None')),
        'sha': clean_text(info.get('sha', 'None')),
        'downloads_30': int(info.get('downloads', 0) or 0),
        'downloads_alltime': int(info.get('downloads_alltime', 0) or 0),
        'likes': int(info.get('likes', 0) or 0),
        'tags': ', '.join(info.get('tags', [])) or 'None',
        'tasks': ', '.join(info.get('tasks', [])) or 'None',
        'description': clean_text(info.get('description', ''))[:200] or 'None',
        'citation': clean_text(info.get('citation', 'None')),
        'languages': ', '.join(info.get('languages', [])) or 'None',
        'language_category': language_category,  # 새로운 필드 추가
        'size_categories': '|'.join(info.get('size_info', {}).get('size_categories', [])) or 'None',
        'paperswithcode_id': clean_text(info.get('paperswithcode_id', 'None')),
        'private': str(info.get('private', False)),
        'gated': str(info.get('gated', False)),
        'disabled': str(info.get('disabled', False)),
        'license': clean_text(info.get('license', 'None')),
        'arxiv_id': clean_text(info.get('arxiv_id', 'None')),
        'url': clean_text(info.get('url', 'None')),
        'task_ids': ', '.join(info.get('cardData', {}).get('task_ids', [])) or 'None'
    }

def main():
    all_dataset_ids = []

    for page in tqdm(range(25), desc="Collecting dataset IDs"):
        try:
            dataset_ids = get_datasets_from_page(page)
            if dataset_ids:
                all_dataset_ids.extend(dataset_ids)
            time.sleep(1)
        except Exception as e:
            print(f"Error on page {page}: {e}")
            continue

    print(f"\nFound {len(all_dataset_ids)} datasets")

    dataset_info_list = []
    for dataset_id in tqdm(all_dataset_ids, desc="Fetching dataset details"):
        info = get_dataset_info(dataset_id)
        processed_info = process_dataset_info(info)
        if processed_info:
            dataset_info_list.append(processed_info)
        time.sleep(0.5)

    df = pd.DataFrame(dataset_info_list)

    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['lastModified'] = pd.to_datetime(df['lastModified'])
    df['downloads_30'] = pd.to_numeric(df['downloads_30'], errors='coerce')
    df['downloads_alltime'] = pd.to_numeric(df['downloads_alltime'], errors='coerce')
    df['likes'] = pd.to_numeric(df['likes'], errors='coerce')

    df = df.fillna('None')
    df = df.sort_values('downloads_alltime', ascending=False)

    output_path = f'huggingface_datasets_{lang}.csv'
    df.to_csv(output_path,
             index=False,
             encoding='utf-8-sig',
             sep=',',
             quoting=1,
             escapechar='\\'
    )

    print(f"\nResults saved to: {output_path}")
    print("\nTop 10 datasets by downloads:")
    print(df.head(10)[['id', 'downloads_30', 'downloads_alltime', 'likes', 'languages', 'tasks', 'license', 'size_categories']])

if __name__ == "__main__":
    main()