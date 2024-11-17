import csv
from elasticsearch import Elasticsearch, exceptions
import warnings
from urllib3.exceptions import InsecureRequestWarning

def read_password_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Suppress specific warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

# Connect to Elasticsearch
try:
    es = Elasticsearch(
        [{'host': 'localhost', 'port': 9200, 'scheme': 'https'}],  # Use 'localhost' or the correct hostname
        http_auth=('elastic', read_password_from_file('password.txt')),
        verify_certs=False  # Set to True in production to verify SSL certificates
    )

    if es.ping():
        print("Successfully connected to the Elasticsearch cluster")
    else:
        print("Connection unsuccessful")

except exceptions.ConnectionError as e:
    print(f"Connection failed: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

# Define the index names
index_names = ['sentences', 'definitions']

# Create the indices if they don't exist
for index_name in index_names:
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)

# Read the CSV files and index the documents
csv_files = ['sentences.csv', 'cleaned_words.csv']
for index_name, csv_file in zip(index_names, csv_files):
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Index the document
            es.index(index=index_name, body=row)

print("Documents indexed successfully")
