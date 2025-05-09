import sqlite3
from datetime import datetime
import os

class Database:
    def __init__(self):
        self.db_path = 'notes.db'
        self.init_db()
        
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建便签表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                font TEXT,
                bg_color TEXT,
                text_color TEXT,
                position_x INTEGER,
                position_y INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建最近使用字体表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recent_fonts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                font_name TEXT UNIQUE,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_recent_font(self, font_name):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 更新或插入字体记录
            cursor.execute('''
                INSERT OR REPLACE INTO recent_fonts (font_name, last_used)
                VALUES (?, CURRENT_TIMESTAMP)
            ''', (font_name,))
            
            conn.commit()
        except Exception as e:
            print(f"Error adding recent font: {e}")
        finally:
            conn.close()
        
    def get_recent_fonts(self, limit=5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT font_name FROM recent_fonts
                ORDER BY last_used DESC
                LIMIT ?
            ''', (limit,))
            
            fonts = [row[0] for row in cursor.fetchall()]
            return fonts
        except Exception as e:
            print(f"Error getting recent fonts: {e}")
            return []
        finally:
            conn.close()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT,
                position_x INTEGER,
                position_y INTEGER,
                size_width INTEGER,
                size_height INTEGER,
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                is_top_most BOOLEAN,
                is_bottom_most BOOLEAN,
                background_color TEXT,
                font_family TEXT,
                font_size INTEGER,
                font_color TEXT
            )
        ''')
        self.conn.commit()
        
    def save_note(self, note_data):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO notes (
                content, position_x, position_y, size_width, size_height,
                created_at, updated_at, is_top_most, is_bottom_most,
                background_color, font_family, font_size, font_color
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            note_data['content'],
            note_data['position_x'],
            note_data['position_y'],
            note_data['size_width'],
            note_data['size_height'],
            datetime.now(),
            datetime.now(),
            note_data.get('is_top_most', False),
            note_data.get('is_bottom_most', False),
            note_data.get('background_color', '#FFFF99'),
            note_data.get('font_family', 'Arial'),
            note_data.get('font_size', 12),
            note_data.get('font_color', '#000000')
        ))
        self.conn.commit()
        return cursor.lastrowid
        
    def update_note(self, note_id, note_data):
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE notes SET
                content = ?,
                position_x = ?,
                position_y = ?,
                size_width = ?,
                size_height = ?,
                updated_at = ?,
                is_top_most = ?,
                is_bottom_most = ?,
                background_color = ?,
                font_family = ?,
                font_size = ?,
                font_color = ?
            WHERE id = ?
        ''', (
            note_data['content'],
            note_data['position_x'],
            note_data['position_y'],
            note_data['size_width'],
            note_data['size_height'],
            datetime.now(),
            note_data.get('is_top_most', False),
            note_data.get('is_bottom_most', False),
            note_data.get('background_color', '#FFFF99'),
            note_data.get('font_family', 'Arial'),
            note_data.get('font_size', 12),
            note_data.get('font_color', '#000000'),
            note_id
        ))
        self.conn.commit()
        
    def get_all_notes(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM notes')
        return cursor.fetchall()
        
    def delete_note(self, note_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        self.conn.commit()
        
    def __del__(self):
        self.conn.close() 