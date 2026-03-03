import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loader.connect import connect_db
from models.site import Site

def migrate_urls():
    connect_db()
    for site in Site.objects():
        if "google.com/search?q=" in site.url:
            query = site.url.split("?q=")[1].split("&")[0]
            new_url = f"https://news.google.com/rss/search?hl=ko&gl=KR&ceid=KR:ko&q={query}"
            site.url = new_url
            site.save()
            print(f"Updated {site.name} to {new_url}")

if __name__ == "__main__":
    migrate_urls()
