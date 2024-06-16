## Flickr Scrapper Ultra
Based on https://github.com/ultralytics/flickr_scraper

This script fetches photos from Flickr based on specified tags and saves the photo information and images to a local directory.
Features
Fetch photos from Flickr using specified tags.
Save photo information in JSON format.
Download and save images in the specified format and size.
Parallel processing for faster downloads.
Requirements
Python 3.x
Required Python packages (listed in requirements.txt):
requests
tqdm
Installation
1. Clone the repository:
2. Install the required packages:
3. Obtain a Flickr API key and save it in a file named FLICKR_API_KEY in the root directory of the project.
Usage
Run the script with the following command:
Arguments
tags (required): Tags to search for photos.
--output (optional): Output folder for saving photo information (default: output).
--cores (optional): Number of cores to use for parallel processing (default: 16).
--per_page (optional): Number of photos per page (min 5, max 500, default: 500).
--sort (optional): Sort order of the photos (default: relevance).
--max_pages (optional): Maximum number of pages to fetch (default: 10).
--size (optional): Size suffix for the images (e.g., s, q, t, m, n, w, z, c, b, h, k, 3k, 4k, f, 5k, 6k, o, default: b).
--format (optional): Format of the images (e.g., jpg, png, default: png).
Example
This command will fetch photos tagged with "nature" and "landscape", save the information and images in the my_photos directory, use 8 cores for parallel processing, fetch 100 photos per page, sort by interestingness in descending order, fetch up to 5 pages, and save images in medium size and JPG format.
License
This project is licensed under the MIT License.