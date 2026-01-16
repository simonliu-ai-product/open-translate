from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

# Robust import for database Base
try:
    from .database import Base
except (ImportError, ValueError):
    from database import Base

class TranslationLog(Base):
    __tablename__ = "translation_logs"

    id = Column(Integer, primary_key=True, index=True)
    source_text = Column(Text, nullable=True) # For text translation
    image_name = Column(String, nullable=True) # For image translation
    translated_text = Column(Text)
    source_lang = Column(String(10))
    target_lang = Column(String(10))
    translation_type = Column(String(20)) # 'text' or 'image'
    created_at = Column(DateTime, default=datetime.utcnow)
