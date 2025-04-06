import csv
import os
import sys
import time
import warnings
from tqdm import tqdm
from elasticsearch import Elasticsearch, exceptions, helpers
from urllib3.exceptions import InsecureRequestWarning

# --- Отключение предупреждений ---
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

# --- Функция чтения пароля из файла ---
def read_password_from_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

# --- Параметры подключения ---
ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST', 'localhost')
ELASTICSEARCH_PORT = int(os.getenv('ELASTICSEARCH_PORT', '9200'))

# --- Ожидание готовности Elasticsearch ---
def wait_for_elasticsearch():
    max_retries = 30
    retry_count = 0
    while retry_count < max_retries:
        try:
            es = Elasticsearch(
                [{'host': ELASTICSEARCH_HOST, 'port': ELASTICSEARCH_PORT, 'scheme': 'http'}],
                basic_auth=('elastic', read_password_from_file('password.txt')),
                timeout=30
            )
            if es.ping():
                print("[OK] Elasticsearch готов к работе", file=sys.stderr, flush=True)
                return es
        except Exception as e:
            retry_count += 1
            print(f"[INFO] Ожидание готовности Elasticsearch... ({retry_count}/{max_retries})", file=sys.stderr, flush=True)
            print(f"[DEBUG] Ошибка: {str(e)}", file=sys.stderr, flush=True)
            time.sleep(10)
    print("[ERROR] Не удалось подключиться к Elasticsearch после всех попыток", file=sys.stderr, flush=True)
    exit(1)

# --- Подключение к Elasticsearch ---
try:
    es = wait_for_elasticsearch()
    es.indices.put_settings(
        index="*",
        body={
            "index": {
                "refresh_interval": "-1",
                "number_of_replicas": "0"
            }
        }
    )
except Exception as e:
    print(f"[ERROR] Неожиданная ошибка: {e}", file=sys.stderr, flush=True)
    exit(1)

# --- Индексы ---
index_names = ['sentences', 'definitions']

for index_name in index_names:
    if es.indices.exists(index=index_name):
        print(f"[INFO] Удаление существующего индекса {index_name}...", file=sys.stderr, flush=True)
        es.indices.delete(index=index_name)
    es.indices.create(index=index_name)
    print(f"[OK] Создан индекс: {index_name}", file=sys.stderr, flush=True)

# --- Загрузка CSV в память ---
def load_csv_data(csv_file):
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            return list(reader)
    except Exception as e:
        print(f"[ERROR] Ошибка при чтении файла {csv_file}: {e}", file=sys.stderr, flush=True)
        return []

# --- Массовая загрузка в Elasticsearch ---
def bulk_upload(index_name, rows, batch_size=1000):
    total = len(rows)
    print(f"\n[INFO] Загрузка {total} записей в индекс '{index_name}'...", file=sys.stderr, flush=True)

    with tqdm(total=total, desc=f"Загрузка '{index_name}'", unit="док", ascii=True, dynamic_ncols=True, file=sys.stderr) as pbar:
        for i in range(0, total, batch_size):
            batch = rows[i:i + batch_size]
            actions = [{"_index": index_name, "_source": row} for row in batch]
            try:
                helpers.bulk(es, actions, raise_on_error=False)
            except Exception as e:
                print(f"[ERROR] Ошибка при загрузке блока {i // batch_size + 1}: {e}", file=sys.stderr, flush=True)
            pbar.update(len(batch))  # Обновление прогресса

# --- Обработка файлов ---
def process_definitions(file_path):
    rows = load_csv_data(file_path)
    if rows:
        bulk_upload("definitions", rows)

def process_sentences(file_path):
    rows = load_csv_data(file_path)
    if rows:
        bulk_upload("sentences", rows)

# --- Основной запуск ---
if __name__ == "__main__":
    print("\n[INFO] Начало загрузки данных...", file=sys.stderr, flush=True)
    process_definitions('cleaned_words.csv')
    process_sentences('sentences.csv')

    try:
        es.indices.put_settings(
            index="*",
            body={
                "index": {
                    "refresh_interval": "1s",
                    "number_of_replicas": "1"
                }
            }
        )
    except Exception as e:
        print(f"[ERROR] Ошибка при восстановлении настроек индекса: {e}", file=sys.stderr, flush=True)

    print("\n[OK] Загрузка данных успешно завершена!", file=sys.stderr, flush=True)
