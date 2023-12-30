# -*- coding: utf-8 -*-
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
import requests
import os
import zipfile
from generatelog import generate_html_log

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_to_file_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        directory_path = args[1]
        keywords_file = args[2]
        current_time = datetime.now()
        logging.info(
            f"Початок виконання  для директорії: {directory_path}, файл ключових слів: {keywords_file} о {current_time}")
        result = func(*args, **kwargs)
        return result
    return wrapper

class Command(ABC):
    @abstractmethod
    def execute(self):
        pass

class ShowLogCommand(Command):
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
    def execute(self):
        try:
            with open(self.log_file_path, 'r', encoding='windows-1251', errors='ignore') as log_file:
                log_content = log_file.read()
                print("\033[93m" + log_content + "\033[0m")
        except FileNotFoundError:
            print(f"Помилка: Лог-файл '{self.log_file_path}' не знайдено.")
        except UnicodeDecodeError:
            print(f"Помилка: Неможливо декодувати вміст лог-файлу як Windows-1251.")

class SendDirectoryCommand(Command):
    def __init__(self, sender_proxy, directory_path, keywords_file):
        self.sender_proxy = sender_proxy
        self.directory_path = directory_path
        self.keywords_file = keywords_file
    def execute(self):
        self.sender_proxy.send_directory(self.directory_path, self.keywords_file)


class DirectorySenderProxy:
    def __init__(self, url):
        self.url = url

    @log_to_file_decorator
    def send_directory(self, directory_path, keywords_file):
        if not os.path.exists(directory_path):
            logging.error(f"\033[91mПомилка: Зазначена директорія не існує: {directory_path}\033[0m\n")
            print('\n\033[91mПомилка! Перевірте файл логів\033[0m')
            return

        if not os.path.isdir(directory_path):
            logging.error(f"\n\033[91mПомилка: Зазначений шлях не є директорією: {directory_path}\033[0m")
            print('\n\033[91mПомилка! Перевірте файл журналу\033[0m')
            return

        if not os.listdir(directory_path):
            logging.error(f"\n\033[91mПомилка: Директорія порожня {directory_path}\033[0m")
            print('\n\033[91mПомилка! Перевірте файл журналу\033[0m')
            return

        if not os.path.exists(keywords_file):
            logging.error(f"\n\033[91mПомилка: Файл ключових слів не знайдено {directory_path}\033[0m")
            print('\n\033[91mПомилка! Перевірте файл журналу\033[0m')
            return

        print('\033[92mПеревірка пройшла успішно. Відправлення даних на сервер...\033[0m')
        send_directory_to_server(self.url, directory_path, keywords_file)

def read_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read().strip().split(',')

def create_zip_archive(directory_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(directory_path,
                                                                                                            '../../..')))

def send_directory_to_server(url, directory_path, keywords_file):
    zip_path = 'temp_archive.zip'
    create_zip_archive(directory_path, zip_path)

    keywords = ','.join(read_keywords(keywords_file))
    try:
        with open(zip_path, 'rb') as zip_file:
            files = {'archive': zip_file}
            data = {'keywords': keywords}
            response = requests.post(url, files=files, data=data)
            response_data = response.json()
            print_formatted_log(response_data)
    except requests.exceptions.JSONDecodeError:
        print("Помилка: Неможливо отримати JSON-відповідь від сервера.")
    finally:
        os.remove(zip_path)


def print_formatted_log(response_data):
    if 'log' in response_data:
        log_entries = response_data['log'].split('\n')
        for entry in log_entries:
            if entry.strip():
                print("\033[92m" + entry + "\033[0m")

    if 'errors' in response_data and response_data['errors'].strip():
        print("\n\033[91m" + response_data['errors'] + "\033[0m")


    html_log = generate_html_log(response_data)
    with open('log_output.html', 'w', encoding='utf-8') as file:
        file.write(html_log)


def main():
    url = 'http://localhost:8009/process-directory/'
    sender_proxy = DirectorySenderProxy(url)

    while True:
        print("Введіть команду:")
        print("1. Обробити директорію")
        print("2. Показати лог")
        print("3. Вихід")
        choice = input("Виберіть опцію: ")

        if choice == '1':
            directory_path = input("Введіть шлях до директорії з файлами: ")
            keywords_file = input("Введіть шлях до файлу з ключовими словами (наприклад, dict.txt): ")
            command = SendDirectoryCommand(sender_proxy, directory_path, keywords_file)
            command.execute()
        elif choice == '2':
            log_command = ShowLogCommand('app.log')
            log_command.execute()
        elif choice == '3':
            print("Вихід з програми.")
            break
        else:
            print("Невірна команда, спробуйте ще раз.")


if __name__ == "__main__":
    main()
