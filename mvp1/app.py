import warnings
from elasticsearch import Elasticsearch, exceptions
import random
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

except exceptions.ConnectionError as e:
    print(f"Connection failed: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

def search_word(word):
    # Define the index name
    index_name = 'definitions'

    # Define the search query
    search_query = {
        "query": {
            "match": {
                "word": word
            }
        }
    }

    # Perform the search
    try:
        response = es.search(index=index_name, body=search_query, size=1)
        if response['hits']['total']['value'] > 0:
            return response['hits']['hits'][0]['_source']['def']
        else:
            return f"The word '{word}' was not found in the database."

    except exceptions.NotFoundError:
        print("Index not found")
    except exceptions.RequestError as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return f"The word '{word}' was not found in the database."

def search(word_for_searching):
    definition = search_word(word_for_searching)
    print('-->searched:', definition)

    # Insert the found word into the found_words table
    if definition != f"The word '{word_for_searching}' was not found in the database.":
        es.index(index='found_words', body={"word": word_for_searching, "definition": definition})

    # Perform Elasticsearch search for sentences containing the word
    es_search(word_for_searching)

def es_search(search_term):
    # Define the index name
    index_name = 'sentences'

    # Define the search query
    search_query = {
        "query": {
            "match": {
                "text": search_term
            }
        }
    }

    # Perform the search
    try:
        response = es.search(index=index_name, body=search_query, size=5)
        if response['hits']['total']['value'] > 0:
            print("Top 5 matching sentences:")
            for hit in response['hits']['hits']:
                print(hit['_source']['text'])
        else:
            print("No matching sentences found.")

    except exceptions.NotFoundError:
        print("Index not found")
    except exceptions.RequestError as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def random_words(n):
    # Query the found_words index
    search_query = {
        "query": {
            "match_all": {}
        }
    }
    response = es.search(index='found_words', body=search_query, size=1000)
    found_words = [(hit['_source']['word'], hit['_source']['definition']) for hit in response['hits']['hits']]

    # Shuffle the list of found words
    random.shuffle(found_words)

    # Print the specified number of random words and their top 2 sentences
    print(f"-->Random {min(n, len(found_words))} words:")
    for word, definition in found_words[:n]:
        print(f"{word}: {definition}")
        print("Top 2 matching sentences:")
        top_sentences = get_top_sentences(word, 2)
        for sentence in top_sentences:
            print(sentence)
        print()

def get_top_sentences(word, size):
    # Define the index name
    index_name = 'sentences'

    # Define the search query
    search_query = {
        "query": {
            "match": {
                "text": word
            }
        }
    }

    # Perform the search
    try:
        response = es.search(index=index_name, body=search_query, size=size)
        if response['hits']['total']['value'] > 0:
            return [hit['_source']['text'] for hit in response['hits']['hits']]
        else:
            return []

    except exceptions.NotFoundError:
        print("Index not found")
    except exceptions.RequestError as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return []

words = ['begin state']
while True:
    if words[0] == 'exit':
        break
    elif words[0] == 'search':
        search(words[1])
    elif words[0] == 'random':
        random_words(int(words[1]))
    print('print one of the next commands:')
    print('exit - to exit')
    print('search <WORD> - to search the <WORD>')
    print('random <NUMBER> - to display <NUMBER> random words you searched')
    input_string = input()
    words = input_string.split()

print('-->exit done')
