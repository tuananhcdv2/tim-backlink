import os
import requests
import pandas as pd
from tqdm import tqdm
from serpapi import GoogleSearch
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

# Thông tin API SerpApi
SERPAPI_KEY = "1581c7ec7ff9408684827966b1c79d632753553ac124e7189888faffbc4f0089"
SEARCH_LIMIT = 100
OUTPUT_DIR = "output"

CATEGORIES = {
    1: "báo trí",
    2: "diễn đàn ô tô",
    3: "diễn đàn phụ kiện xe ô tô",
    4: "diễn đàn công nghệ",
    5: "diễn đàn độ xe",
    6: "diễn đàn nước ngoài",
    7: "website diễn đàn",
    8: "social bookmarking"
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

def check_url_status(url):
    """Kiểm tra trạng thái URL và trả về trạng thái và thời gian phản hồi."""
    try:
        start_time = time.time()
        response = requests.head(url, timeout=5)
        response_time = round(time.time() - start_time, 2)
        return response.status_code == 200, response_time
    except requests.RequestException:
        return False, None

def search_forums(category):
    """Tìm kiếm diễn đàn với từ khóa và lấy kết quả."""
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

        # Nếu không còn kết quả mới hoặc bị giới hạn
        if len(results.get("organic_results", [])) == 0:
            break

        page += 1
        if page > 10:  # Giới hạn truy vấn tối đa 10 trang
            break

    return list(all_urls)

def run_search(category_key, progress_bar, stop_event, tree):
    category = CATEGORIES[category_key]
    urls = search_forums(category)

    results = []
    progress_bar["value"] = 0
    progress_step = 100 / max(len(urls), 1)

    for url in urls:
        if stop_event.is_set():
            messagebox.showinfo("Dừng", "Tìm kiếm đã bị dừng.")
            break

        is_active, response_time = check_url_status(url)
        status = "Hoạt động" if is_active else "Không hoạt động"
        results.append({"URL": url, "Trạng thái": status, "Thời gian phản hồi (s)": response_time})

        progress_bar["value"] += progress_step
        progress_bar.update()

        # Cập nhật kết quả vào bảng giao diện
        tree.insert("", tk.END, values=(url, status, response_time))

    if results:
        messagebox.showinfo("Hoàn tất", f"Đã tìm được {len(results)} kết quả.")
    return results

def export_to_csv(results, category):
    """Xuất kết quả ra file CSV."""
    output_file_csv = os.path.join(OUTPUT_DIR, f"{category.replace(' ', '_')}.csv")
    df = pd.DataFrame(results)
    df.to_csv(output_file_csv, index=False, encoding='utf-8-sig')
    messagebox.showinfo("Hoàn tất", f"Đã lưu {len(results)} diễn đàn vào {output_file_csv}.")

# Giao diện Tkinter
def create_ui():
    window = tk.Tk()
    window.title("Tìm kiếm diễn đàn")
    window.geometry("800x600")

    category_var = tk.StringVar()
    category_combobox = ttk.Combobox(window, textvariable=category_var, state="readonly")
    category_combobox['values'] = list(CATEGORIES.values())
    category_combobox.pack(pady=10)

    progress_bar = ttk.Progressbar(window, orient='horizontal', length=600, mode='determinate')
    progress_bar.pack(pady=20)

    tree = ttk.Treeview(window, columns=("URL", "Trạng thái", "Thời gian phản hồi (s)"), show="headings")
    tree.heading("URL", text="URL")
    tree.heading("Trạng thái", text="Trạng thái")
    tree.heading("Thời gian phản hồi (s)", text="Thời gian phản hồi (s)")
    tree.pack(pady=20, fill="both", expand=True)

    stop_event = threading.Event()

    def on_search():
        category_name = category_combobox.get()
        if not category_name:
            messagebox.showwarning("Lỗi", "Vui lòng chọn loại diễn đàn.")
            return

        category_key = list(CATEGORIES.keys())[list(CATEGORIES.values()).index(category_name)]
        stop_event.clear()

        global all_results
        all_results = run_search(category_key, progress_bar, stop_event, tree)

    def on_cancel():
        stop_event.set()

    def on_export():
        category_name = category_combobox.get()
        if all_results:
            export_to_csv(all_results, category_name)

    search_button = tk.Button(window, text="Tìm kiếm", command=on_search, font=("Arial", 12), bg="#4CAF50", fg="white")
    search_button.pack(pady=10)

    cancel_button = tk.Button(window, text="Hủy tìm kiếm", command=on_cancel, font=("Arial", 12), bg="#f44336", fg="white")
    cancel_button.pack(pady=5)

    export_button = tk.Button(window, text="Xuất CSV", command=on_export, font=("Arial", 12))
    export_button.pack(pady=5)

    window.mainloop()

if __name__ == "__main__":
    create_ui()
