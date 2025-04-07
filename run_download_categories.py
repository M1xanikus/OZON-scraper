import os
import sys
import time
import argparse

# Add the project root to the Python path
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)

from scraper.categoryPageDownloader import CategoryPageDownloader
from htmlParser.htmlMainPageParser import HTMLMainPageLinksParser
from logs.logger import Logger

def download_category_and_extract_links(category_name, download_path, links_file):
    """
    Download a category page and extract product links from it.
    
    Args:
        category_name: Name of the category to search for
        download_path: Path to save the HTML file
        links_file: Path to save the extracted links
        
    Returns:
        Number of links extracted
    """
    logger = Logger("category_downloader.log")
    logger.log(f"Starting download for category: {category_name}")
    
    # Create download directory if it doesn't exist
    os.makedirs(download_path, exist_ok=True)
    
    # Download the category page
    with CategoryPageDownloader(category_name, download_path) as downloader:
        html_file_path = downloader.save_html_to_file()
        
        if not html_file_path:
            logger.log(f"Failed to download category page for: {category_name}")
            return 0
            
        logger.log(f"Successfully downloaded category page to: {html_file_path}")
        
        # Read the HTML file
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # Parse the HTML to extract product links
        parser = HTMLMainPageLinksParser(html_content)
        product_links = parser.get_product_links()
        
        # Save the links to a file
        parser.save_links_to_txt(product_links, links_file)
        
        logger.log(f"Extracted {len(product_links)} product links from {category_name}")
        return len(product_links)
# python run_download_categories.py --categories "электроника" "одежда" "обувь"
def main():
    parser = argparse.ArgumentParser(description='Download OZON category pages and extract product links')
    parser.add_argument('--categories', nargs='+', required=True, help='List of category names to download')
    parser.add_argument('--download-path', default='htmldata/categories', help='Path to save HTML files')
    parser.add_argument('--links-file', default='product_links.txt', help='Path to save product links')
    
    args = parser.parse_args()
    
    total_links = 0
    
    for category in args.categories:
        print(f"Processing category: {category}")
        links_count = download_category_and_extract_links(
            category, 
            args.download_path, 
            args.links_file
        )
        total_links += links_count
        print(f"Extracted {links_count} links from {category}")
        
        # Add a delay between categories to avoid rate limiting
        if category != args.categories[-1]:
            delay = 10
            print(f"Waiting {delay} seconds before processing next category...")
            time.sleep(delay)
    
    print(f"Completed! Total links extracted: {total_links}")
    print(f"Links saved to: {args.links_file}")

if __name__ == "__main__":
    main() 