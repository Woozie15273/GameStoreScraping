import csv
import json

import logging
from dataclasses import asdict, fields
import re
import asyncio
import sqlite3

from schemas import GameEntry, SearchParams
from config import Config

class Exporter:
    def __init__(self, data: list[GameEntry]):
        self.data = data
        self._filename_cleaner = re.compile(r'[^a-z0-9_\-]')

    # -----------------------------
    # Shared internal helpers
    # -----------------------------

    def _ensure_data(self, label:str) -> bool:
        if not self.data:
            logging.info(f"No data to export; skipping {label} write")
            return False
        return True

    def _prepare_path(self, filename:str, ext:str):
        return(Config.DEFAULT_PATH / filename).with_suffix(ext)
    
    def _entries_as_dicts(self):
        return [asdict(entry) for entry in self.data]

    @staticmethod
    def _format_val(v):
        if isinstance(v, float):
            return str(int(v))
        if isinstance(v, list):
            return "-".join(map(str, v))
        return str(v)

    def generate_filename(self, params: SearchParams) -> str:
        parts = [
            f"{k}_{self._format_val(v)}"
            for k, v in vars(params).items()
            if v not in (None, [], "")
        ]

        if not parts:
            return "all_entries"

        raw_name = "_".join(parts).lower()
        cleaned = self._filename_cleaner.sub("", raw_name)

        # Limit to 64 characters
        if len(cleaned) > 64:
            cleaned = cleaned[:64]

        return cleaned

    # -----------------------------
    # CSV Export
    # -----------------------------
    def to_csv(self, filename:str):
                
        if not self._ensure_data("CSV"):
            return
        
        path = self._prepare_path(filename, ".csv")        
        headers = [f.name for f in fields(GameEntry)]

        try:
            with open(path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(asdict(entry).values() for entry in self.data)
                logging.info(f"Exported {len(self.data)} entries to CSV successfully")                
        
        except IOError as e:
            logging.error(f'File error: {e}')

    async def to_csv_async(self, filename: str):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.to_csv, filename)

    # -----------------------------
    # JSON Export
    # -----------------------------
    def to_json(self, filename:str):
        if not self._ensure_data("JSON"):
            return
        
        path = self._prepare_path(filename, '.json')
        payload = self._entries_as_dicts()

        try:
            with open(path, mode='w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii='False', indent=2)
            logging.info(f"Exported {len(self.data)} entries to JSON successfully")
        except IOError as e:
            logging.error(f"File error: {e}")

    async def to_json_async(self, filename: str):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.to_json, filename)

    # -----------------------------
    # SQLite Export
    # -----------------------------
    def to_sqlite(self, filename:str):
        if not self._ensure_data("SQLite"):
            return
        
        path = self._prepare_path(filename, ".sqlite")
        entries = self._entries_as_dicts()
        columns = [f.name for f in fields(GameEntry)]

        try: 
            conn = sqlite3.connect(path)
            cur = conn.cursor()

            # Create table
            col_defs = ', '.join(f'{col} TEXT' for col in columns)
            cur.execute(f"CREATE TABLE IF NOT EXISTS games ({col_defs})")

            # Insert rows
            placeholders = ", ".join("?" for _ in columns)
            insert_sql = f"INSERT INTO games ({', '.join(columns)}) VALUES ({placeholders})"

            rows = [
                tuple(entry[col] for col in columns)
                for entry in entries
            ]

            cur.executemany(insert_sql, rows)
            conn.commit()
            conn.close()
        
            logging.info(f"Exported {len(self.data)} entries to SQLite successfully")

        except sqlite3.Error as e:
            logging.error(f"SQLite error: {e}")
        except IOError as e:
            logging.error(f"File error: {e}")
    
    async def to_sqlite_async(self, filename: str):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.to_sqlite, filename)
