import os
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import seaborn as sns

Base = declarative_base()

class PriceHistory(Base):
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    crawl_date = Column(DateTime, default=datetime.utcnow)

class PriceTracker:
    def __init__(self):
        # Database connection
        DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/patanjameh_db')
        self.engine = create_engine(DATABASE_URL)
        self.Session = sessionmaker(bind=self.engine)

    def record_current_prices(self, products):
        """
        Record current prices for all products
        """
        session = self.Session()
        
        for product in products:
            price_history_entry = PriceHistory(
                product_id=product.id,
                price=product.price
            )
            session.add(price_history_entry)
        
        session.commit()
        session.close()

    def generate_price_trends(self):
        """
        Generate price trend visualization
        """
        # Fetch price history data
        query = """
        SELECT product_id, 
               crawl_date, 
               price 
        FROM price_history 
        ORDER BY product_id, crawl_date
        """
        
        df = pd.read_sql(query, self.engine)
        
        # Create visualization
        plt.figure(figsize=(15, 8))
        sns.lineplot(
            x='crawl_date', 
            y='price', 
            hue='product_id', 
            data=df
        )
        
        plt.title('Product Price Trends Over Time')
        plt.xlabel('Crawl Date')
        plt.ylabel('Price')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save plot
        os.makedirs('reports', exist_ok=True)
        plt.savefig('reports/price_trends.png')
        plt.close()

    def price_change_analysis(self):
        """
        Analyze price changes between crawls
        """
        query = """
        WITH ranked_prices AS (
            SELECT 
                product_id, 
                price, 
                crawl_date,
                LAG(price) OVER (PARTITION BY product_id ORDER BY crawl_date) as prev_price
            FROM price_history
        )
        SELECT 
            product_id, 
            AVG((price - prev_price) / prev_price * 100) as avg_price_change_percentage
        FROM ranked_prices
        WHERE prev_price IS NOT NULL
        GROUP BY product_id
        """
        
        df = pd.read_sql(query, self.engine)
        
        # Save analysis to CSV
        os.makedirs('reports', exist_ok=True)
        df.to_csv('reports/price_change_analysis.csv', index=False)

def main():
    # This would be integrated with the main scraping script
    tracker = PriceTracker()
    
    # After scraping and saving products
    # tracker.record_current_prices(scraped_products)
    
    # Generate visualizations
    tracker.generate_price_trends()
    tracker.price_change_analysis()

if __name__ == '__main__':
    main()