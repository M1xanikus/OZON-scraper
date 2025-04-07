import os
from categoryPageDownloader import CategoryPageDownloader

def main():
    # Example category name to search on OZON
    category_name = "электроника"
    
    # Create a directory for category HTML files
    download_path = os.path.join("htmldata", "categories")
    
    # Use the CategoryPageDownloader with context manager
    with CategoryPageDownloader(category_name, download_path) as downloader:
        # Download the category page
        file_path = downloader.save_html_to_file()
        
        if file_path:
            print(f"Category page successfully downloaded to: {file_path}")
        else:
            print("Failed to download category page.")

if __name__ == "__main__":
    main() 