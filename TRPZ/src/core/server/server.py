# -*- coding: utf-8 -*-
from fastapi import FastAPI, UploadFile, File, Form
import aiofiles
import os
import shutil
import zipfile
from core2 import search_keywords_in_emails
from abc import ABC, abstractmethod
from typing import List
from database import DatabaseManager

app = FastAPI()
db_manager = DatabaseManager('requests.db')


class ArchiveProcessor(ABC):
    @abstractmethod
    def extract(self, archive_path: str, destination: str) -> None:
        pass

class ZipArchiveProcessor(ArchiveProcessor):
    def extract(self, archive_path: str, destination: str) -> None:
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(destination)

class DirectoryProcessor(ABC):
    @abstractmethod
    async def process_directory(
        self, directory_path: str, log_file: str, error_file: str, keywords: List[str], output_folder: str, flag: bool
    ) -> None:
        pass

class EmailProcessor(DirectoryProcessor):
    async def process_directory(
        self, directory_path: str, log_file: str, error_file: str, keywords: List[str], output_folder: str, flag: bool
    ) -> None:
        await search_keywords_in_emails(directory_path, log_file, error_file, keywords, output_folder, flag)

class ArchiveProcessorBridge:
    def __init__(self, archive_processor: ArchiveProcessor, directory_processor: DirectoryProcessor):
        self.archive_processor = archive_processor
        self.directory_processor = directory_processor

    async def process_archive(
        self, archive_path: str, log_file: str, error_file: str, keywords: List[str], output_folder: str, flag: bool
    ) -> None:
        temp_directory = "temp_directory"
        self.archive_processor.extract(archive_path, temp_directory)
        await self.directory_processor.process_directory(temp_directory, log_file, error_file, keywords, output_folder, flag)



@app.post("/process-directory/")
async def process_directory(archive: UploadFile = File(...), keywords: str = Form(...)):
    archive_path = f"temp_{archive.filename}"
    log_file = "log.txt"
    error_file = "errors.txt"
    output_folder = "output_folder"
    await db_manager.log_request(archive.filename, keywords.split(','))
    open(log_file, 'w').close()
    open(error_file, 'w').close()

    async with aiofiles.open(archive_path, "wb") as out_file:
        content = await archive.read()
        await out_file.write(content)

    archive_processor = ZipArchiveProcessor()
    directory_processor = EmailProcessor()

    bridge = ArchiveProcessorBridge(archive_processor, directory_processor)
    await bridge.process_archive(archive_path, log_file, error_file, keywords.split(','), output_folder, False)

    log_content = ""
    if os.path.exists(log_file):
        async with aiofiles.open(log_file, "r", encoding="utf-8") as log:
            log_content = await log.read()

    errors_content = ""
    if os.path.exists(error_file):
        async with aiofiles.open(error_file, "r", encoding="utf-8") as errors:
            errors_content = await errors.read()

    os.remove(archive_path)
    shutil.rmtree("temp_directory")

    return {"message": "Directory processed", "log": log_content, "errors": errors_content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
