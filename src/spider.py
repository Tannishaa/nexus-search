import requests
import urllib3
import boto3
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()

# Disable SSL warnings (University WiFi fix)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DistributedSpider:
    def __init__(self, queue_url, max_pages=10):
        # Setup AWS SQS Client
        # This allows us to push/pull URLs from the cloud
        self.sqs = boto3.client('sqs', region_name='ap-south-1')
        self.queue_url = queue_url
        
        # We still keep 'visited' local for now to prevent loops on this machine
        self.visited = set()
        self.max_pages = max_pages

    def add_to_queue(self, url):
        """
        Sends the URL to AWS SQS so any worker can pick it up.
        """
        try:
            self.sqs.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps({'url': url})
            )
            # print(f"   --> Pushed to Queue: {url}") # Optional: Uncomment to see every push
        except Exception as e:
            print(f"❌ AWS Error (Send): {e}")

    def get_next_url(self):
        """
        Asks AWS SQS: "Do you have any URLs for me to crawl?"
        """
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=2 # Long polling (efficient)
            )
            
            if 'Messages' in response:
                message = response['Messages'][0]
                receipt_handle = message['ReceiptHandle']
                body = json.loads(message['Body'])
                
                # Delete it so other workers don't process it again
                self.sqs.delete_message(
                    QueueUrl=self.queue_url,
                    ReceiptHandle=receipt_handle
                )
                return body['url']
            
            return None # Queue is empty
        except Exception as e:
            print(f"❌ AWS Error (Receive): {e}")
            return None

    def start(self, seed_url=None):
        print("🕷️  Distributed Spider Starting...")
        
        # If we have a seed URL, push it to start the chain
        if seed_url:
            print(f"🌱 Seeding queue with: {seed_url}")
            self.add_to_queue(seed_url)

        pages_crawled = 0
        
        while pages_crawled < self.max_pages:
            # 1. Get next URL from Cloud
            current_url = self.get_next_url()
            
            if not current_url:
                print("💤 Queue is empty. Waiting...")
                time.sleep(2)
                continue
                
            if current_url in self.visited:
                continue

            # 2. Process the page
            print(f"🔍 Crawling [{pages_crawled + 1}]: {current_url}")
            self.visited.add(current_url)
            
            links_found = self.crawl_page(current_url)
            pages_crawled += 1
            
            # Politeness delay
            time.sleep(1)

        print(f"✅ Reached limit of {self.max_pages} pages.")

    def crawl_page(self, url):
        """
        Fetches the HTML and pushes new links to SQS.
        """
        try:
            # Fake browser user-agent
            headers = {'User-Agent': 'Nexus-Bot/1.0'}
            response = requests.get(url, headers=headers, timeout=5, verify=False)
            
            if response.status_code != 200:
                return 0

            soup = BeautifulSoup(response.text, "lxml")
            count = 0
            
            for link in soup.find_all("a", href=True):
                full_url = urljoin(url, link['href'])
                
                # Basic validation: Must be HTTP/HTTPS and same domain (optional)
                if full_url.startswith('http') and full_url not in self.visited:
                    self.add_to_queue(full_url)
                    count += 1
            
            print(f"   --> Found {count} new links (pushed to SQS).")
            return count

        except Exception as e:
            print(f"⚠️  Error crawling {url}: {e}")
            return 0

# --- Configuration ---
if __name__ == "__main__":
    # Load from .env instead of hardcoding
    MY_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
    
    if not MY_QUEUE_URL:
        raise ValueError("❌ Error: SQS_QUEUE_URL not found in .env file")

    bot = DistributedSpider(MY_QUEUE_URL, max_pages=5)
    bot.start(seed_url="https://toscrape.com/")