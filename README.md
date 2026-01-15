# Nexus Search 🕷️
> A distributed, cloud-native search engine built with Python, AWS, and Next.js.

## Overview
Nexus Search is a scalable search engine architecture designed to crawl, index, and query the web. It decouples the crawling logic from the indexing logic using a message queue, allowing for horizontal scaling.

**Live Demo:** [Insert your Vercel Link Here]

## Architecture
* **Crawler (Producer):** Python script using `requests` & `BeautifulSoup` to traverse web pages (BFS).
* **Queue (Broker):** **AWS SQS** buffers URLs to decouple crawling from processing.
* **Worker (Consumer):** Python script that pulls tasks, processes HTML, and extracts keywords.
* **Index (Database):** **AWS DynamoDB** (Inverted Index) for O(1) keyword lookups.
* **API:** **AWS Lambda** (Serverless) exposes the data via a REST API.
* **Frontend:** **Next.js 14** (TypeScript) providing a clean, Google-like search interface.

## Tech Stack
* **Backend:** Python 3.12, Boto3
* **Cloud:** AWS (Lambda, SQS, DynamoDB)
* **Frontend:** Next.js, Tailwind CSS, Lucide React
* **Tools:** Git, VS Code

## How to Run Locally

### 1. The Spider (Crawler)
```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows
# Start the spider to fill the SQS Queue
python src/spider.py
```
2. The Worker (Indexer)
```Bash

# Start the worker to process the Queue
python src/worker.py
```
3. The Frontend
```Bash

cd web-ui
npm run dev
# Open localhost:3000
```
## Future Improvements
[ ] Implement PageRank algorithm for better sorting.

[ ] Add "Did you mean?" fuzzy search capability.

[ ] Containerize workers using Docker.