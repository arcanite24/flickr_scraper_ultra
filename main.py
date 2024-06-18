import requests
import json
import argparse
import logging
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

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
        "page": page,
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Error: {response.status_code}")
        return None


def save_photo_info(output_folder, photo_info, size, format, failed_downloads):
    json_filepath = os.path.join(output_folder, f"{photo_info['id']}.json")
    image_filepath = os.path.join(output_folder, f"{photo_info['id']}.{format}")

    with open(json_filepath, "w") as file:
        json.dump(photo_info, file)

    try:
        response = requests.get(photo_info["url"], timeout=10)
        if response.status_code == 200:
            with open(image_filepath, "wb") as file:
                file.write(response.content)
        else:
            raise Exception(f"Failed to download image {photo_info['url']}")
    except Exception as e:
        logging.error(e)
        failed_downloads.append(photo_info)
        with open(os.path.join(output_folder, "failed_downloads.json"), "w") as file:
            json.dump(failed_downloads, file)


def fetch_all_pages(tags, api_key, per_page, sort, max_pages):
    all_pages = []
    first_page = get_page(tags, api_key, per_page, sort)
    if not first_page:
        logging.error("Failed to fetch the first page.")
        return None

    total_pages = first_page["photos"]["pages"]
    if max_pages == -1:
        max_pages = total_pages
    else:
        max_pages = min(total_pages, max_pages)

    all_pages.append(first_page)

    with ThreadPoolExecutor() as executor, tqdm(
        total=max_pages, desc="Fetching pages"
    ) as pbar:
        futures = [
            executor.submit(get_page, tags, api_key, per_page, sort, page_number)
            for page_number in range(2, max_pages + 1)
        ]
        for future in as_completed(futures):
            page_data = future.result()
            if page_data:
                all_pages.append(page_data)
            pbar.update(1)

    return all_pages


def main(
    tags,
    output_folder,
    num_cores,
    per_page,
    sort,
    max_pages,
    size,
    format,
    no_download,
    session_file,
):
    failed_downloads = []

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    if session_file:
        logging.info(f"Loading session data from {session_file}")
        with open(session_file, "r") as file:
            all_pages = json.load(file)
    else:
        api_key = load_api_key("FLICKR_API_KEY")
        if not api_key:
            logging.error("API key is required to proceed.")
            return

        if num_cores == -1:
            num_cores = os.cpu_count()
            logging.info(f"Using all available cores: {num_cores}")
        else:
            logging.info(f"Using {num_cores} cores")

        logging.info("Fetching all pages...")
        all_pages = fetch_all_pages(tags, api_key, per_page, sort, max_pages)

        if all_pages:
            # Save all pages data to session.json
            with open(f"{output_folder}/session.json", "w") as file:
                json.dump(all_pages, file)

    if all_pages:
        if no_download:
            logging.info("No download flag is set. Skipping image downloads.")
            return

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
                        save_photo_info,
                        output_folder,
                        photo_info,
                        size,
                        format,
                        failed_downloads,
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
        help="Number of cores to use for parallel processing (-1 to use all available cores)",
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
        help="Sort order (e.g., date-posted-asc, date-taken-asc, interestingness-desc)",
    )
    parser.add_argument(
        "--max_pages",
        type=int,
        default=-1,
        help="Maximum number of pages to fetch (-1 for all pages)",
    )
    parser.add_argument(
        "--size",
        type=str,
        default="b",
        help="Size suffix for the photo (e.g., s, q, t, m, n, z, c, b, h, k, o)",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="jpg",
        help="Image format (e.g., jpg, png)",
    )
    parser.add_argument(
        "--no_download",
        action="store_true",
        help="If set, only fetch metadata without downloading images",
    )
    parser.add_argument(
        "--session_file",
        type=str,
        help="Path to a session file to resume from",
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
        args.no_download,
        args.session_file,
    )

# python main.py portrait --output flickr_portraits --size b --cores 8 --session_file flickr_portraits_full_v1_partial\session.json
