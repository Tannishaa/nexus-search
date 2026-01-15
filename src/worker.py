import boto3
import json
import requests
import urllib3
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()
# Disable SSL warnings (for college WiFi/network issues)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SearchWorker:
    def __init__(self, queue_url):
        # Setup SQS (The To-Do List)
        self.sqs = boto3.client('sqs', region_name='ap-south-1')
        
        # Setup DynamoDB (The Search Index)
        # Using 'resource' instead of 'client' is more "Pythonic"
        self.db = boto3.resource('dynamodb', region_name='ap-south-1')
        self.table = self.db.Table('nexus-index')
        
        self.queue_url = queue_url

    def process_url(self, url):
        """
        Downloads a page and saves keywords to the database.
        """
        headers = {'User-Agent': 'Nexus-Worker/1.0'}
        response = requests.get(url, headers=headers, timeout=5, verify=False)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            title = soup.title.string if soup.title else "No Title"
            
            # Clean up the HTML
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Lowercase and split into unique words
            text_content = soup.get_text().lower()
            words = set(text_content.split())
            
            print(f"   📑 Indexing words from: {title}")

            count = 0
            # SDE Choice: Index first 50 words to stay within DynamoDB free limits for now
            for word in list(words)[:50]:
                if len(word) > 3: # Skip short words like 'the', 'is'
                    try:
                        self.table.put_item(
                            Item={
                                'keyword': word,
                                'url': url,
                                'title': title
                            }
                        )
                        count += 1
                    except Exception as e:
                        print(f"      ❌ Failed word '{word}': {e}")
            
            print(f"   ✅ Successfully indexed {count} words.")

    def run(self):
        """
        Main loop: Constantly asks SQS for new work.
        """
        print("👷 Worker started. Looking for tasks in SQS...")
        
        while True:
            # 1. Pull 1 URL from the queue
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=5 # Long polling (saves money/battery)
            )

            if 'Messages' not in response:
                print("💤 Queue empty. Retrying...")
                continue

            # 2. Get URL and Receipt (needed for deleting)
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            body = json.loads(message['Body'])
            url = body['url']

            print(f"📥 Processing: {url}")

            try:
                # 3. Scrape and Index
                self.process_url(url)
                
                # 4. Delete from queue so nobody else does this work
                self.sqs.delete_message(
                    QueueUrl=self.queue_url,
                    ReceiptHandle=receipt_handle
                )
                print("   🗑️ Task removed from queue.")

            except Exception as e:
                print(f"   ❌ Error processing {url}: {e}")

if __name__ == "__main__":
    # Load from .env instead of hardcoding
    MY_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
    
    if not MY_QUEUE_URL:
        raise ValueError("❌ Error: SQS_QUEUE_URL not found in .env file")
    
    worker = SearchWorker(MY_QUEUE_URL)
    worker.run()