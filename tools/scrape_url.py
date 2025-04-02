from pydantic import Field
from typing import Dict
from typing_extensions import Annotated
import time, json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from core.utils.logger import logger
from app.middleware.CheckAccessMiddleware import is_authenticated


def scrape_content(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        time.sleep(3)
        page_source = driver.page_source

        soup = BeautifulSoup(page_source, "html.parser")

        # Extract the page title
        page_title = soup.title.string if soup.title else "No Title Found"

        # Replace hyperlinks in text with formatted [link text]{address}
        for a in soup.find_all("a", href=True):
            link_text = a.get_text(strip=True) or "Untitled"
            link_address = a["href"]
            a.replace_with(f"[{link_text}]({link_address})")

        body_content = soup.get_text(
            separator=" ", strip=True
        )  # Extract formatted text

    finally:
        driver.quit()

    return page_title, body_content


def split_text(text, max_length=2000):
    """Splits text into chunks of max_length without breaking words."""
    words = text.split(" ")
    chunks = []
    current_chunk = []

    for word in words:
        if sum(len(w) + 1 for w in current_chunk) + len(word) + 1 > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []

        current_chunk.append(word)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def scrape_url_tool(
    url: Annotated[
        str,
        Field(description="The URL to scrape content from. Ex: https://example.com"),
    ],
) -> Dict:
    """
    Scrape content from a given URL and return the page title, content chunks, and character count. 
    
    Request Body Parameters:
    - url (str): The URL to scrape content from.

    Example Request Payload:
    {
        "url": "https://example.com"
    }

    Returns:
    - 200 OK: A JSON object containing the scraped data.
    - 400 Bad Request: If the URL is missing or invalid.
    - 500 Internal Server Error: If an error occurs during the scraping process.

    Example Response (200 OK):
    {
        "data": {
            "page_title": "Example Title",
            "content_chunks": ["chunk1", "chunk2"],
            "total_chars": 1024
        }
    }

    Example Response (400 Bad Request):
    {
        "error": "URL not provided"
    }

    Example Response (500 Internal Server Error):
    {
        "error": "Failed to scrape URL: <error_message>"
    }
    """
    logger.info(f"Starting to scrape URL: {url}")

    auth_response = is_authenticated(True)
    if auth_response:
        return auth_response

    if not url:
        logger.error("URL not provided")
        return {"error": "URL not provided"}

    try:
        # Scrape the content of the URL
        page_title, body_content = scrape_content(url)
        char_count = len(body_content)

        # Split the content into chunks
        content_chunks = split_text(body_content, 2000)

        logger.info(f"Successfully scraped URL: {url} ({char_count} characters)")

        # Return the response
        return json.dumps(
            {
                "page_title": page_title,
                "content_chunks": content_chunks,
                "total_chars": char_count,
            }
        )

    except Exception as e:
        logger.error(f"Failed to scrape URL {url}: {str(e)}")
        return {"error": f"Failed to scrape URL: {str(e)}"}
