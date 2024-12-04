from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class ClothingItem(Base):
    """
    Model to store clothing item details
    """
    __tablename__ = "clothing_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    brand = Column(String)
    category = Column(String)
    url = Column(String, unique=True)
    price = Column(Float)  # Added price field
    image_urls = Column(ARRAY(String))  # Added image_urls field
    
    # Relationship to price history
    price_histories = relationship("PriceHistory", back_populates="clothing_item")

class PriceHistory(Base):
    """
    Model to track price history of clothing items
    """
    __tablename__ = "price_histories"

    id = Column(Integer, primary_key=True, index=True)
    clothing_item_id = Column(Integer, ForeignKey('clothing_items.id'))
    price = Column(Float, nullable=False)
    scrape_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship back to clothing item
    clothing_item = relationship("ClothingItem", back_populates="price_histories")