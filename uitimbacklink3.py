import os
import requests
import pandas as pd
from tqdm import tqdm
from serpapi import GoogleSearch
import threading
import time
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

SERPAPI_KEY = "1581c7ec7ff9408684827966b1c79d632753553ac124e7189888faffbc4f0089"
SEARCH_LIMIT = 100
OUTPUT_DIR = "output"

CATEGORIES = {
    "1": "báo trí",
    "2": "diễn đàn ô tô",
    "3": "diễn đàn phụ kiện xe ô tô",
    "4": "diễn đàn công nghệ",
    "5": "diễn đàn độ xe",
    "6": "diễn đàn nước ngoài",
    "7": "website diễn đàn",
    "8": "social bookmarking"
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

def check_url_status(url):
    try:
        start_time = time.time()
        response = requests.head(url, timeout=5)
        response_time = round(time.time() - start_time, 2)
        return response.status_code == 200, response_time
    except requests.RequestException:
        return False, None

def search_forums(category):
    params = {
        "engine": "google",
        "q": category,
        "num": 10,
        "api_key": SERPAPI_KEY
    }
    all_urls = set()
    page = 0
    while len(all_urls) < SEARCH_LIMIT:
        params["start"] = page * 10
        search = GoogleSearch(params)
        results = search.get_dict()

        if "organic_results" in results:
            for result in results["organic_results"]:
                if "link" in result:
                    all_urls.add(result["link"])

        if len(results.get("organic_results", [])) == 0:
            break

        page += 1
        if page > 10:
            break

    return list(all_urls)

class ForumApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

        self.category_input = TextInput(hint_text='Nhập số danh mục (1-8)')
        self.add_widget(self.category_input)

        self.search_button = Button(text='Tìm kiếm')
        self.search_button.bind(on_press=self.run_search)
        self.add_widget(self.search_button)

        self.result_label = Label(text="")
        self.add_widget(self.result_label)

        self.progress_bar = ProgressBar(max=100)
        self.add_widget(self.progress_bar)

    def run_search(self, instance):
        category_key = self.category_input.text
        category = CATEGORIES.get(category_key, None)
        if not category:
            self.result_label.text = "Danh mục không hợp lệ"
            return

        urls = search_forums(category)
        self.result_label.text = f"Tìm được {len(urls)} kết quả"
        self.progress_bar.value = 100

class ForumAppApp(App):
    def build(self):
        return ForumApp()

if __name__ == "__main__":
    ForumAppApp().run()
