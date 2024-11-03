# Patanjameh Web Scraper

A Python-based web scraper for [Patanjameh](https://patanjameh.ir) that collects clothing items data and stores it in a PostgreSQL database. The project uses Docker for containerization and includes price tracking analytics.

## Features

- Asynchronous web scraping using `aiohttp`
- PostgreSQL database for data storage
- Price history tracking and analysis
- Docker containerization
- pgAdmin interface for database management
- Environment variable configuration
- Automatic retry mechanisms for both scraping and database operations

## Prerequisites

- Docker Desktop
- Git
- VS Code
- Python 3.9 or higher (for local development)

## Project Structure

```
patanjameh-scraper/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   └── price_analysis.py
├── docker/
├── reports/
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/patanjameh-scraper.git
cd patanjameh-scraper
```

2. Create a `.env` file in the root directory (use `.env.example` as a template):
```bash
cp .env.example .env
```

3. Build and run the Docker containers:
```bash
docker-compose up -d
```

4. Access pgAdmin:
- Open `http://localhost:5050` in your browser
- Login with:
  - Email: admin@admin.com
  - Password: admin

## Database Configuration

The PostgreSQL database runs in a Docker container with the following default settings:
- Host: postgres
- Port: 5432
- Database: patanjameh_db
- Username: postgres
- Password: postgres

## Usage

1. Start the scraper:
```bash
docker-compose up web
```

2. Monitor the logs:
```bash
docker-compose logs -f web
```

3. View the data in pgAdmin at `http://localhost:5050`

## Development

To set up the development environment:

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application locally:
```bash
python app/main.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.