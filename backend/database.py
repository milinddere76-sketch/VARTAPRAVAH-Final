import os
import psycopg2
from datetime import datetime
from . import config
from .utils.logger import logger

def get_db_connection():
    """Returns a connection to the PostgreSQL database."""
    try:
        return psycopg2.connect(
            host=config.DB_HOST,
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASS
        )
    except psycopg2.OperationalError as e:
        logger.error(f"⚠️ [DB] Connection failed: {e}")
        return None

def init_db():
    """Initializes the VartaPravah core tables."""
    logger.info("🐘 [DB] Initializing PostgreSQL Tables...")
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        # 1. News Articles Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            source VARCHAR(255),
            category VARCHAR(50),
            published_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Generated Scripts Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS scripts (
            id SERIAL PRIMARY KEY,
            article_ids INT[],
            content TEXT NOT NULL,
            anchor_type VARCHAR(20),
            bulletin_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 3. Bulletin Queue Table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS bulletin_queue (
            id SERIAL PRIMARY KEY,
            script_id INT REFERENCES scripts(id),
            status VARCHAR(20) DEFAULT 'pending', -- pending, processing, completed, failed
            output_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 4. Analytics Table (Existing)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id SERIAL PRIMARY KEY,
            videos_generated INT,
            errors INT,
            revenue FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        logger.info("✅ [DB] All tables initialized successfully")
    except Exception as e:
        logger.error(f"⚠️ [DB] Initialization error: {e}")

def save_article(title, source, category):
    conn = get_db_connection()
    if not conn: return
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO articles (title, source, category) VALUES (%s, %s, %s)",
            (title, source, category)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to save article: {e}")

def log_analytics(videos, errors, revenue):
    conn = get_db_connection()
    if not conn: return
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO analytics (videos_generated, errors, revenue) VALUES (%s, %s, %s)",
            (videos, errors, revenue)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to log analytics: {e}")
