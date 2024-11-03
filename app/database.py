import os
import time
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError

load_dotenv()

logging_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=logging_level)
logger = logging.getLogger(__name__)

DB_HOST = os.getenv('DB_HOST', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'patanjameh_db')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_db_engine(max_retries=10, retry_interval=5):
    """Create database engine with retry logic"""
    logger.info(f"Attempting to connect to database at {DB_HOST}:{DB_PORT}")
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    'connect_timeout': 10
                }
            )
            
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                logger.info("Successfully connected to the database!")
                return engine
                
        except OperationalError as e:
            if attempt == max_retries - 1:
                logger.error(f"Failed to connect to database after {max_retries} attempts: {str(e)}")
                raise
            logger.warning(f"Database connection attempt {attempt + 1} failed, retrying in {retry_interval} seconds...")
            logger.warning(f"Connection error: {str(e)}")
            time.sleep(retry_interval)

engine = create_db_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    retries = 5
    for attempt in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Successfully initialized database tables!")
            return
        except Exception as e:
            if attempt == retries - 1:
                logger.error(f"Failed to initialize database: {str(e)}")
                raise
            logger.warning(f"Database initialization attempt {attempt + 1} failed, retrying...")
            time.sleep(5)