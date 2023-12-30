import os
import argparse
import patoolib
import concurrent.futures

def extract_and_remove_archive(file_path):
    try:
        if os.path.isfile(file_path):
            patoolib.extract_archive(file_path, outdir=os.path.dirname(file_path))
            os.remove(file_path)
            print(f'Розархівовано та видалено архів: {file_path}')
            print(f'Каталог розархівації: {os.path.dirname(file_path)}')
    except Exception as e:
        pass

def process_directory(directory):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                executor.submit(extract_and_remove_archive, file_path)

def main():
    parser = argparse.ArgumentParser(description='Розархівація файлів у вказаній директорії')
    parser.add_argument('directory', type=str, help='Шлях до директорії для обробки')
    args = parser.parse_args()

    directory = args.directory
    if os.path.exists(directory):
        process_directory(directory)
    else:
        print("Зазначена директорія не існує.")
if __name__ == "__main__":
    main()
