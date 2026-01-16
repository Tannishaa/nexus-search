import boto3
import json
import requests
import urllib3
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from collections import Counter  # <--- NEW: For Frequency Analysis

# Load variables from .env file
load_dotenv()
# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SearchWorker:
    def __init__(self, queue_url):
        # Setup SQS (The To-Do List)
        self.sqs = boto3.client('sqs', region_name='ap-south-1')
        
        # Setup DynamoDB (The Search Index)
        self.db = boto3.resource('dynamodb', region_name='ap-south-1')
        self.table = self.db.Table('nexus-index')
        
        self.queue_url = queue_url

    def process_url(self, url):
        """
        Downloads a page, calculates Word Frequency (TF), and indexes the top keywords.
        """
        headers = {'User-Agent': 'Nexus-Worker/2.0-Intelligent'} # <--- Updated User Agent
        try:
            response = requests.get(url, headers=headers, timeout=5, verify=False)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "lxml")
                title = soup.title.string if soup.title else "No Title"
                
                # 1. Clean up the HTML (Remove CSS/JS)
                for script in soup(["script", "style", "meta", "noscript"]):
                    script.decompose()
                
                # 2. ALGORITHM: Frequency Analysis
                # We get all text, lowercase it, and split into a list
                text_content = soup.get_text().lower()
                words = text_content.split()
                
                # 3. Calculate "Term Frequency" (TF)
                # Instead of a simple set(), we count occurrences.
                # Example: {'python': 12, 'code': 4, 'the': 50}
                word_counts = Counter(words)
                
                print(f"   📑 Analyzed {len(words)} words in: {title}")

                count = 0
                
                # 4. FILTERING: Get the top 50 most relevant words only
                # We skip generic words (len < 4) and take the ones with highest counts
                most_common = word_counts.most_common(100) # Analyze top 100 candidates
                
                for word, freq in most_common:
                    if len(word) > 3 and word.isalpha(): # Ensure it's a real word
                        try:
                            # 5. STORAGE: Save with Relevance Score
                            self.table.put_item(
                                Item={
                                    'keyword': word,      # Partition Key
                                    'url': url,           # Sort Key
                                    'title': title,
                                    'score': freq         # <--- NEW: The Relevance Score
                                }
                            )
                            count += 1
                            if count >= 50: break # Hard limit to save DB costs
                        except Exception as e:
                            print(f"      ❌ Failed word '{word}': {e}")
                
                print(f"   ✅ Indexed {count} keywords with relevance scores.")

        except Exception as e:
            print(f"   ❌ Network error for {url}: {e}")

    def run(self):
        """
        Main loop: Constantly asks SQS for new work.
        """
        print("👷 Intelligent Worker started. Ready to calculate relevance scores...")
        
        while True:
            # 1. Pull 1 URL from the queue
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=1,
                WaitTimeSeconds=5 # Long polling
            )

            if 'Messages' not in response:
                # No sleep needed here because WaitTimeSeconds does it for us
                print("💤 Queue empty. Waiting...")
                continue

            # 2. Get URL and Receipt
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            try:
                body = json.loads(message['Body'])
                url = body['url']

                print(f"📥 Processing: {url}")

                # 3. Scrape and Index
                self.process_url(url)
                
                # 4. Delete from queue
                self.sqs.delete_message(
                    QueueUrl=self.queue_url,
                    ReceiptHandle=receipt_handle
                )
                print("   🗑️ Task removed from queue.")

            except Exception as e:
                print(f"   ❌ Error parsing message: {e}")

if __name__ == "__main__":
    MY_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
    if not MY_QUEUE_URL:
        raise ValueError("❌ Error: SQS_QUEUE_URL not found in .env file")
    
    worker = SearchWorker(MY_QUEUE_URL)
    worker.run()