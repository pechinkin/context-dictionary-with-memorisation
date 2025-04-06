import os
from elasticsearch import Elasticsearch
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Отключение предупреждений
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

def read_password_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# Параметры подключения
ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'localhost')
ELASTICSEARCH_PORT = int(os.getenv('ELASTICSEARCH_PORT', '9200'))

# Подключение к Elasticsearch
es = Elasticsearch(
    [{'host': ELASTICSEARCH_HOST, 'port': ELASTICSEARCH_PORT, 'scheme': 'http'}],
    basic_auth=('elastic', read_password_from_file('password.txt')),
    timeout=30
)

def search_word(word):
    # Поиск определения
    definition_query = {
        "query": {
            "match": {
                "word": word
            }
        }
    }
    
    definition_result = es.search(index='definitions', body=definition_query)
    
    # Поиск предложений
    sentences_query = {
        "query": {
            "match": {
                "text": word
            }
        },
        "size": 5
    }
    
    sentences_result = es.search(index='sentences', body=sentences_query)
    
    return definition_result, sentences_result

def print_results(definition_result, sentences_result):
    # Вывод определения
    if definition_result['hits']['total']['value'] > 0:
        definition = definition_result['hits']['hits'][0]['_source']
        print(f"\nОпределение слова '{definition['word']}':")
        print(f"Часть речи: {definition['pos']}")
        print(f"Значение: {definition['def']}")
    else:
        print(f"\nОпределение не найдено")
    
    # Вывод предложений
    if sentences_result['hits']['total']['value'] > 0:
        print("\nПримеры использования:")
        for hit in sentences_result['hits']['hits']:
            sentence = hit['_source']
            print(f"- {sentence['text']} (Уровень: {sentence['label']})")
    else:
        print("\nПримеры использования не найдены")

def main():
    print("Поиск определений и примеров использования слов")
    print("Введите 'exit' для выхода")
    
    while True:
        user_input = input("\nВведите слово для поиска: ").strip()
        
        if user_input.lower() == 'exit':
            print("До свидания!")
            break
            
        if not user_input:
            print("Пожалуйста, введите слово")
            continue
            
        try:
            definition_result, sentences_result = search_word(user_input)
            print_results(definition_result, sentences_result)
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    main()