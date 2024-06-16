import requests
import json
import argparse
import logging
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_api_key(filepath):
    try:
        with open(filepath, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        logging.error(f"API key file not found at {filepath}")
        raise


def get_page(tags, api_key, per_page, sort, page=1):
    base_url = "https://www.flickr.com/services/rest/"
    params = {
        "method": "flickr.photos.search",
        "api_key": api_key,
        "tags": tags,
        "format": "json",
        "nojsoncallback": 1,
        "per_page": per_page,
        "sort": sort,
        "content_types": "0",  # Defaults to photos
        "media": "photos",
        "page": page,  # Add page number to the parameters
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Error: {response.status_code}")
        return None


def save_photo_info(output_folder, photo_info, size, format):
    json_filepath = os.path.join(output_folder, f"{photo_info['id']}.json")
    image_filepath = os.path.join(output_folder, f"{photo_info['id']}.{format}")

    # Save the photo information in JSON format
    with open(json_filepath, "w") as file:
        json.dump(photo_info, file)

    # Download and save the image
    response = requests.get(photo_info["url"])
    if response.status_code == 200:
        with open(image_filepath, "wb") as file:
            file.write(response.content)
    else:
        logging.error(f"Failed to download image {photo_info['url']}")


def fetch_all_pages(tags, api_key, per_page, sort, max_pages):
    all_pages = []
    first_page = get_page(tags, api_key, per_page, sort)
    if not first_page:
        logging.error("Failed to fetch the first page.")
        return None

    total_pages = min(first_page["photos"]["pages"], max_pages)
    all_pages.append(first_page)

    with ThreadPoolExecutor() as executor, tqdm(
        total=total_pages, desc="Fetching pages"
    ) as pbar:
        futures = [
            executor.submit(get_page, tags, api_key, per_page, sort, page_number)
            for page_number in range(2, total_pages + 1)
        ]
        for future in as_completed(futures):
            page_data = future.result()
            if page_data:
                all_pages.append(page_data)
            pbar.update(1)

    return all_pages


def main(tags, output_folder, num_cores, per_page, sort, max_pages, size, format):
    api_key = load_api_key("FLICKR_API_KEY")
    if not api_key:
        logging.error("API key is required to proceed.")
        return

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    logging.info("Fetching all pages...")
    all_pages = fetch_all_pages(tags, api_key, per_page, sort, max_pages)

    if all_pages:
        # Save all pages data to session.json
        with open(f"{output_folder}/session.json", "w") as file:
            json.dump(all_pages, file)

        # Extract all photos from all pages
        all_photos = [photo for page in all_pages for photo in page["photos"]["photo"]]
        existing_photos = set(
            os.listdir(output_folder)
        )  # Get already downloaded photo IDs

        with ThreadPoolExecutor(max_workers=num_cores) as executor, tqdm(
            total=len(all_photos), desc="Downloading images"
        ) as pbar:
            futures = []
            for photo in all_photos:
                photo_id = photo["id"]
                photo_filename = f"{photo_id}.json"
                if photo_filename in existing_photos:
                    pbar.update(1)
                    continue
                title = photo["title"]
                farm_id = photo["farm"]
                server_id = photo["server"]
                secret = photo["secret"]
                photo_url = f"https://farm{farm_id}.staticflickr.com/{server_id}/{photo_id}_{secret}_{size}.{format}"
                photo_info = {"title": title, "url": photo_url, "id": photo_id}
                futures.append(
                    executor.submit(
                        save_photo_info, output_folder, photo_info, size, format
                    )
                )
            for future in futures:
                future.result()  # Wait for all tasks to complete
                pbar.update(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch photos from Flickr based on tags."
    )
    parser.add_argument("tags", type=str, help="Tags to search for photos")
    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Output folder for saving photo information",
    )
    parser.add_argument(
        "--cores",
        type=int,
        default=16,
        help="Number of cores to use for parallel processing",
    )
    parser.add_argument(
        "--per_page",
        type=int,
        default=500,
        help="Number of photos per page (min 5, max 500)",
    )
    parser.add_argument(
        "--sort",
        type=str,
        default="relevance",
        help="Sort order of the photos",
    )
    parser.add_argument(
        "--max_pages",
        type=int,
        default=10,
        help="Maximum number of pages to fetch",
    )
    parser.add_argument(
        "--size",
        type=str,
        default="b",
        help="Size suffix for the images (e.g., s, q, t, m, n, w, z, c, b, h, k, 3k, 4k, f, 5k, 6k, o)",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="png",
        help="Format of the images (e.g., jpg, png)",
    )
    args = parser.parse_args()
    main(
        args.tags,
        args.output,
        args.cores,
        args.per_page,
        args.sort,
        args.max_pages,
        args.size,
        args.format,
    )
