import requests
from bs4 import BeautifulSoup


def fetch_page(url):
    """
    Fetch page HTML and extract title, headings, text, and links.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"Failed to fetch {url} - Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # حذف تگ‌های غیر ضروری
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()

        title = soup.title.get_text(strip=True) if soup.title else ""

        h1_tags = [h.get_text(strip=True) for h in soup.find_all("h1")]
        h2_tags = [h.get_text(strip=True) for h in soup.find_all("h2")]

        text = soup.get_text(separator=" ", strip=True)

        links = []
        for a in soup.find_all("a", href=True):
            links.append(a["href"])

        return {
            "url": url,
            "title": title,
            "h1": " | ".join(h1_tags),
            "h2": " | ".join(h2_tags),
            "content": text,
            "links": links
        }

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def load_urls_from_file(file_path):
    """
    Load URLs from urls.txt
    """

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            urls = file.readlines()

        urls = [url.strip() for url in urls if url.strip()]

        return urls

    except Exception as e:
        print(f"Error reading URL file: {e}")
        return []
