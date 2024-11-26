import os
import logging
import asyncio
import aiohttp
from typing import List, Dict
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from database import get_db, init_db, Base, engine
from models import ClothingItem, PriceHistory
from metrics import CrawlerMetrics

load_dotenv()

logging_level = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(level=logging_level)
logger = logging.getLogger(__name__)

class PatanjamehScraper:
    def __init__(self):
        self.base_url = os.getenv('BASE_URL', 'https://patanjameh.ir')
        self.metrics = CrawlerMetrics()
        self.categories = [
            f"{self.base_url}/search/group-men-shirt",
            f"{self.base_url}/search/group-women-manto"
        ]
        self.headers = {
            'User-Agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.session = None

    async def init_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)

    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def fetch_html(self, url: str) -> str:
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                logger.error(f"Error fetching {url}: Status {response.status}")
                return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None

    def extract_product_data(self, product_div) -> Dict:
        try:
            title_elem = product_div.find('div', class_='content').find('h6', class_='title').find('a')
            url = f"{self.base_url}{title_elem['href']}" if title_elem else None
            title = title_elem.text.strip() if title_elem else 'No title'

            price_box = product_div.find('div', class_='content-right')
            price = 0
            if price_box:
                price_elem = price_box.find('div', class_='sep_vit_rightspec sep-price')
                if price_elem:
                    price_text = price_elem.text.strip().replace(',', '').replace('تومان', '').strip()
                    try:
                        price = float(price_text)
                    except ValueError:
                        price = 0

            discount_div = product_div.find('div', class_='sep-OffPrecent')
            discount = 0
            if discount_div:
                discount_text = discount_div.find('span').text.strip().replace('%', '')
                try:
                    discount = float(discount_text)
                except ValueError:
                    discount = 0

            images = []
            main_img = product_div.find('img', class_='main-img')
            overlay_img = product_div.find('img', class_='overlay-img')
            
            if main_img and main_img.get('src'):
                images.append(main_img['src'])
            if overlay_img and overlay_img.get('src'):
                if overlay_img.get('data-src'):  
                    images.append(overlay_img['data-src'])
                elif overlay_img.get('src') and 'data:image/gif' not in overlay_img['src']:
                    images.append(overlay_img['src'])

            product_data = {
                'title': title,
                'price': price,
                'url': url,
                'image_urls': images,
                'discount_percentage': discount
            }
            
            logger.info(f"Extracted product: {title} - Price: {price}")
            return product_data

        except Exception as e:
            logger.error(f"Error extracting product data: {str(e)}")
            return None

    async def fetch_products(self, category_url: str) -> List[Dict]:
        products = []
        page = 1
        
        while True:
            url = f"{category_url}?page={page}"
            logger.info(f"Fetching page {page} from {url}")
            
            html = await self.fetch_html(url)
            if not html:
                self.metrics.record_error()
                break

            self.metrics.record_page_crawled()
            soup = BeautifulSoup(html, 'html.parser')
            product_divs = soup.find_all('div', class_='sep-vit-item')
            
            if not product_divs:
                logger.info(f"No products found on page {page} for {category_url}")
                break
            
            for product_div in product_divs:
                product_data = self.extract_product_data(product_div)
                if product_data:
                    products.append(product_data)
                    self.metrics.record_product_scraped()
                else:
                    self.metrics.record_error()

    

            pagination = soup.find('ul', class_='pagination')
            if not pagination or not pagination.find('a', class_='page-link', string='›'):
                break
            
            page += 1
            
        logger.info(f"Found {len(products)} products in category {category_url}")
        return products
    
    async def run(self):
        await self.init_session()
        try:
            start_time = self.metrics.start_scrape()
            db = next(get_db())
            for category_url in self.categories:
                logger.info(f"Processing category: {category_url}")
                products = await self.fetch_products(category_url)
                if products:
                    self.save_to_database(products, db)
            self.metrics.end_scrape(start_time)
            self.metrics.push_metrics()  # Push metrics after completion
        finally:
            await self.close_session()

    def save_to_database(self, products: List[Dict], db: Session):
        try:
            for product in products:
                existing_item = db.query(ClothingItem).filter(ClothingItem.url == product['url']).first()
                
                if existing_item:
                    existing_item.name = product['title']
                    existing_item.price = product['price']

                    price_history = PriceHistory(
                        clothing_item_id=existing_item.id,
                        price=product['price']
                    )
                    db.add(price_history)
                else:
                    new_item = ClothingItem(
                        name=product['title'],
                        url=product['url'],
                        price=product['price'],
                        image_urls=product['image_urls']
                    )
                    db.add(new_item)
                    db.flush() 
                    
                    price_history = PriceHistory(
                        clothing_item_id=new_item.id,
                        price=product['price']
                    )
                    db.add(price_history)
                
                db.commit()
                logger.info(f"Saved/updated product: {product['title']}")
                
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            db.rollback()

    async def run(self):
        await self.init_session()
        try:
            db = next(get_db())
            for category_url in self.categories:
                logger.info(f"Processing category: {category_url}")
                products = await self.fetch_products(category_url)
                if products:
                    self.save_to_database(products, db)
        finally:
            await self.close_session()

async def reset_db():
    """Reset database tables"""
    logger.info("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database reset complete!")

async def main():
    logger.info("Starting the scraper...")
    await reset_db() 
    init_db()
    scraper = PatanjamehScraper()
    await scraper.run()

if __name__ == "__main__":
    asyncio.run(main())