import os
import re
import sqlite3
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

# Подключение к SQLite и создание таблицы
def init_sqlite_db(db_path='words.db'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS word_weights (
            word TEXT PRIMARY KEY,
            weight INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    return conn

# Обновление веса слова
def update_word_weight(conn, word):
    cursor = conn.cursor()
    cursor.execute('SELECT weight FROM word_weights WHERE word = ?', (word,))
    result = cursor.fetchone()
    if result:
        new_weight = result[0] + 1
        cursor.execute('UPDATE word_weights SET weight = ? WHERE word = ?', (new_weight, word))
    else:
        cursor.execute('INSERT INTO word_weights (word, weight) VALUES (?, ?)', (word, 1))
    conn.commit()

# Поиск слова в Elasticsearch
def search_word(word):
    definition_query = {
        "query": {
            "match": {
                "word": word
            }
        }
    }
    definition_result = es.search(index='definitions', body=definition_query)

    sentences_query = {
        "query": {
            "match": {
                "text": word
            }
        },
        "size": 10
    }
    sentences_result = es.search(index='sentences', body=sentences_query)

    return definition_result, sentences_result
    
# Ранжирование предложений по сумме весов слов
def rank_sentences_by_word_weight(conn, sentences):
    ranked = []
    cursor = conn.cursor()

    for hit in sentences:
        text = hit['_source']['text']
        words = re.findall(r'\b\w+\b', text.lower())
        total_weight = 0
        for word in words:
            cursor.execute('SELECT weight FROM word_weights WHERE word = ?', (word,))
            result = cursor.fetchone()
            if result:
                total_weight += result[0]
        ranked.append((total_weight, hit))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [hit for _, hit in ranked]

# Вывод результатов
def print_results(definition_result, sentences_result, conn):
    if definition_result['hits']['total']['value'] > 0:
        definition = definition_result['hits']['hits'][0]['_source']
        print(f"\nОпределение слова '{definition['word']}':")
        print(f"Часть речи: {definition['pos']}")
        print(f"Значение: {definition['def']}")
    else:
        print(f"\nОпределение не найдено")
    
    # Вывод предложений
    if sentences_result['hits']['total']['value'] > 0:
        print("\nПримеры использования (отсортированы по весу слов):")
        sorted_hits = rank_sentences_by_word_weight(conn, sentences_result['hits']['hits'])
        for hit in sorted_hits:
            sentence = hit['_source']
            print(f"- {sentence['text']} (Уровень: {sentence['label']})")
    else:
        print("\nПримеры использования не найдены")

# Основной цикл
def main():
    print("Поиск определений и примеров использования слов")
    print("Введите 'exit' для выхода")

    conn = init_sqlite_db()

    while True:
        user_input = input("\nВведите слово для поиска: ").strip()
        
        if user_input.lower() == 'exit':
            print("До свидания!")
            break
            
        if not user_input:
            print("Пожалуйста, введите слово")
            continue
            
        try:
            word = user_input.lower()
            update_word_weight(conn, word)
            definition_result, sentences_result = search_word(word)
            print_results(definition_result, sentences_result, conn)
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")

    conn.close()

if __name__ == "__main__":
    main()
