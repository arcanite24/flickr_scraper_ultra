import requests
import json
import argparse
import logging
import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import signal
import sys

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

lock = threading.Lock()


def signal_handler(sig, frame):
    logging.info("Process interrupted. Exiting gracefully...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def save_photo_info(output_folder, photo_info, size, format, failed_downloads):
    image_filepath = os.path.join(output_folder, f"{photo_info['id']}.{format}")

    if os.path.exists(image_filepath):
        logging.info(f"Image {image_filepath} already exists. Skipping download.")
        with lock:
            if photo_info in failed_downloads:
                failed_downloads.remove(photo_info)
        return

    try:
        response = requests.get(photo_info["url"], timeout=10)
        if response.status_code == 200:
            with open(image_filepath, "wb") as file:
                file.write(response.content)
            # Remove the successfully downloaded photo from the failed list
            with lock:
                if photo_info in failed_downloads:
                    failed_downloads.remove(photo_info)
        else:
            raise Exception(f"Failed to download image {photo_info['url']}")
    except Exception as e:
        logging.error(e)


def retry_failed_downloads(failed_file, output_folder, num_cores, size, format):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(failed_file, "r") as file:
        failed_downloads = json.load(file)

    if not failed_downloads:
        logging.info("No failed downloads to retry.")
        return

    new_failed_downloads = failed_downloads.copy()

    with ThreadPoolExecutor(max_workers=num_cores) as executor, tqdm(
        total=len(failed_downloads), desc="Retrying failed downloads"
    ) as pbar:
        futures = [
            executor.submit(
                save_photo_info,
                output_folder,
                photo_info,
                size,
                format,
                new_failed_downloads,
            )
            for photo_info in failed_downloads
        ]
        for future in as_completed(futures):
            future.result()  # Wait for all tasks to complete
            pbar.update(1)

    # Update the failed downloads JSON file
    with open(os.path.join(output_folder, "failed_downloads.json"), "w") as file:
        json.dump(new_failed_downloads, file)

    if new_failed_downloads:
        logging.info(f"{len(new_failed_downloads)} downloads failed again.")
    else:
        logging.info("All failed downloads retried successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Retry failed photo downloads from Flickr."
    )
    parser.add_argument(
        "failed_file", type=str, help="Path to the failed downloads JSON file"
    )
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
        "--size",
        type=str,
        default="b",
        help="Size suffix for the photo (e.g., s, q, t, m, n, z, c, b, h, k, o)",
    )
    parser.add_argument(
        "--format",
        type=str,
        default="png",
        help="Image format (e.g., jpg, png)",
    )

    args = parser.parse_args()

    if args.cores == -1:
        args.cores = os.cpu_count()
        logging.info(f"Using all available cores: {args.cores}")
    else:
        logging.info(f"Using {args.cores} cores")

    retry_failed_downloads(
        args.failed_file,
        args.output,
        args.cores,
        args.size,
        args.format,
    )
