import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from serpapi import GoogleSearch
import time

SEARCH_LIMIT = 100  # Số lượng diễn đàn tối thiểu cần tìm
OUTPUT_DIR = "output"
PREVIOUS_RESULTS_FILE = os.path.join(OUTPUT_DIR, "previous_results.txt")

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

# Khởi tạo thư mục nếu chưa tồn tại
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_previous_results():
    """Đọc danh sách URL đã lưu trước đó."""
    if not os.path.exists(PREVIOUS_RESULTS_FILE):
        return set()
    
    with open(PREVIOUS_RESULTS_FILE, 'r') as file:
        return set(line.strip() for line in file.readlines())

def save_results(urls):
    """Lưu kết quả vào file, loại bỏ trùng lặp."""
    with open(PREVIOUS_RESULTS_FILE, 'a') as file:
        for url in urls:
            file.write(url + '\n')

def check_url_status(url):
    """Kiểm tra xem URL có còn hoạt động không."""
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def search_forums(category):
    """Tìm kiếm diễn đàn dựa trên lựa chọn của người dùng."""
    params = {
        "engine": "google",
        "q": category,
        "num": 100,
        "api_key": "1581c7ec7ff9408684827966b1c79d632753553ac124e7189888faffbc4f0089"
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    urls = set()
    if "organic_results" in results:
        for result in results["organic_results"]:
            if "link" in result:
                urls.add(result["link"])
    return urls

def main():
    # Đọc danh sách URL đã tìm trước đó
    previous_urls = get_previous_results()

    # Nhận lựa chọn từ người dùng
    print("Chọn loại diễn đàn cần tìm:")
    for key, value in CATEGORIES.items():
        print(f"{key}. {value}")
    
    try:
        choice = int(input("Nhập số lựa chọn: "))
        if choice not in CATEGORIES:
            raise ValueError("Lựa chọn không hợp lệ.")
    except ValueError as e:
        print(e)
        return
    
    category = CATEGORIES[choice]
    print(f"Đang tìm kiếm các diễn đàn cho danh mục: {category}...")

    # Tìm kiếm diễn đàn
    urls = search_forums(category)
    if len(urls) < SEARCH_LIMIT:
        print("Không đủ kết quả tìm kiếm. Vui lòng thử lại sau.")
        return

    # Loại bỏ các URL trùng lặp
    urls = urls - previous_urls

    # Kiểm tra trạng thái URL và lưu kết quả hợp lệ
    valid_urls = []
    print("Kiểm tra trạng thái các diễn đàn...")
    for url in tqdm(urls, desc="Đang kiểm tra"):
        if check_url_status(url):
            valid_urls.append(url)
    
    # Lưu kết quả vào file
    output_file = os.path.join(OUTPUT_DIR, f"{category.replace(' ', '_')}.txt")
    with open(output_file, 'w') as file:
        for url in valid_urls:
            file.write(url + '\n')

    # Lưu các URL vào file tổng để tránh trùng lặp trong tương lai
    save_results(valid_urls)

    print(f"Đã tìm và lưu {len(valid_urls)} diễn đàn vào file {output_file}.")
    print("Quá trình hoàn tất thành công.")

if __name__ == "__main__":
    main()
