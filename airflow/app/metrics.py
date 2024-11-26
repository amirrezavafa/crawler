# crawler/airflow/app/metrics.py
from prometheus_client import Counter, Gauge, Histogram, start_http_server, push_to_gateway
import time
import os

PUSHGATEWAY_HOST = os.getenv('PUSHGATEWAY_HOST', 'pushgateway:9091')

class CrawlerMetrics:
    def __init__(self):
        # Initialize Prometheus metrics
        self.pages_crawled = Counter('crawler_pages_total', 'Total number of pages crawled')
        self.products_scraped = Counter('crawler_products_total', 'Total number of products scraped')
        self.scrape_errors = Counter('crawler_errors_total', 'Total number of scraping errors')
        self.scrape_duration = Histogram('crawler_scrape_duration_seconds', 'Time spent scraping')
        self.last_scrape_timestamp = Gauge('crawler_last_scrape_timestamp', 'Timestamp of the last scrape')
        self.active_scrape = Gauge('crawler_scrape_in_progress', 'Whether a scrape is currently in progress')
        
    def record_page_crawled(self):
        self.pages_crawled.inc()
        
    def record_product_scraped(self):
        self.products_scraped.inc()
        
    def record_error(self):
        self.scrape_errors.inc()
        
    def start_scrape(self):
        self.active_scrape.set(1)
        self.last_scrape_timestamp.set_to_current_time()
        return time.time()
        
    def end_scrape(self, start_time):
        duration = time.time() - start_time
        self.scrape_duration.observe(duration)
        self.active_scrape.set(0)
        
    def push_metrics(self, job_name='crawler'):
        try:
            push_to_gateway(PUSHGATEWAY_HOST, job=job_name, registry=None)
        except Exception as e:
            print(f"Error pushing metrics: {e}")