import boto3
from botocore.exceptions import ClientError

class NexusSearchEngine:
    def __init__(self):
        # Connect to our DynamoDB Index
        self.db = boto3.resource('dynamodb', region_name='ap-south-1')
        self.table = self.db.Table('nexus-index')

    def find_results(self, keyword):
        """
        Uses the 'Query' operation to find all URLs mapped to a keyword.
        SDE Tip: Query is much faster/cheaper than Scan!
        """
        keyword = keyword.lower().strip()
        print(f"🔎 Searching for: '{keyword}'...")

        try:
            # We query based on the 'keyword' Partition Key
            response = self.table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('keyword').eq(keyword)
            )
            
            items = response.get('Items', [])
            return items

        except ClientError as e:
            print(f"❌ Database error: {e.response['Error']['Message']}")
            return []

if __name__ == "__main__":
    engine = NexusSearchEngine()
    
    while True:
        query = input("\nEnter search term (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
            
        results = engine.find_results(query)
        
        if not results:
            print(" No results found. Try crawling more pages!")
        else:
            print(f"Found {len(results)} results:")
            for i, res in enumerate(results, 1):
                print(f"{i}. {res['title']}")
                print(f"   🔗 {res['url']}\n")