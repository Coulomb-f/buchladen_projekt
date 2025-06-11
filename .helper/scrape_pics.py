import os
import json
import requests
import urllib.parse
import time

# Determine paths relative to this script's location
_SCRIPT_LOCATION_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT_DIR = os.path.abspath(os.path.join(_SCRIPT_LOCATION_DIR, os.pardir)) # os.pardir is '..'

BOOKS_JSON_PATH = os.path.join(_PROJECT_ROOT_DIR, 'buecher.json')
COVER_SAVE_DIR = os.path.join(_PROJECT_ROOT_DIR, 'assets')

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in "._- ").rstrip()

def search_and_download_cover(title: str, author: str) -> str | None:
    query = urllib.parse.quote_plus(f"{title} {author}")
    # Google Books API endpoint
    api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}"

    print(f"[*] Searching Google Books for: {title} by {author}")
    # print(f"    API URL: {api_url}") # Uncomment for debugging URL

    try:
        response = requests.get(api_url, headers=HEADERS, timeout=10) # Added timeout
        response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
    except requests.exceptions.RequestException as e:
        print(f"[!] Failed to fetch search results for {title}: {e}")
        return None

    try:
        data = response.json()
    except json.JSONDecodeError:
        print(f"[!] Failed to parse JSON response for {title}")
        print(f"    Response text (first 500 chars): {response.text[:500]}")
        return None

    # print(json.dumps(data, indent=2, ensure_ascii=False)[:1000]) # Uncomment for debugging JSON response

    if "items" in data and len(data["items"]) > 0:
        first_book = data["items"][0]
        volume_info = first_book.get("volumeInfo", {})
        image_links = volume_info.get("imageLinks", {})

        # Try to get various image sizes, preferring larger ones
        img_url = (image_links.get("large") or
                   image_links.get("medium") or
                   image_links.get("thumbnail") or
                   image_links.get("smallThumbnail"))

        if not img_url or not isinstance(img_url, str):
            print(f"[-] No suitable image link found in API response for {title}")
            # print(f"    Available imageLinks: {image_links}") # For debugging
            return None

        # Google Books API URLs are usually http or https.
        # This check might be redundant but harmless.
        if img_url.startswith("//"):
            img_url = "https:" + img_url

        filename = sanitize_filename(f"{title}.jpg")
        filepath = os.path.join(COVER_SAVE_DIR, filename)

        print(f"[*] Downloading cover for {title} from {img_url}")
        try:
            img_response = requests.get(img_url, headers=HEADERS, timeout=10) # Added timeout
            img_response.raise_for_status() # Check for download errors

            with open(filepath, 'wb') as f:
                f.write(img_response.content)
            print(f"[+] Saved cover: {filepath}")
            # Return the relative path for the JSON file
            relative_image_path = f"assets/{filename}" # Uses forward slash as in example
            return relative_image_path

        except requests.exceptions.RequestException as e:
            print(f"[!] Failed to download image for {title} from {img_url}: {e}")
        except IOError as e:
            print(f"[!] Failed to save image for {title} to {filepath}: {e}")
        return None # Return None if download or save fails
    else:
        print(f"[-] No items found in Google Books API response for {title}")
        return None

def main():
    os.makedirs(COVER_SAVE_DIR, exist_ok=True)

    try:
        with open(BOOKS_JSON_PATH, 'r', encoding='utf-8') as f:
            books_data = json.load(f)
    except FileNotFoundError:
        print(f"[!] Error: {BOOKS_JSON_PATH} not found.")
        return
    except json.JSONDecodeError:
        print(f"[!] Error: Could not decode JSON from {BOOKS_JSON_PATH}.")
        return

    books_updated_count = 0
    books_processed_count = 0

    for book_entry in books_data:
        books_processed_count += 1
        title = book_entry.get("titel")
        author = book_entry.get("autor")

        if not title or not author:
            print(f"[*] Skipping entry due to missing title or author: {book_entry}")
            continue

        current_json_image_path = book_entry.get("image_path")
        local_image_found_and_json_updated = False
        needs_api_call = True

        # 1. Check if JSON already has a valid image_path and the file exists
        if current_json_image_path:
            absolute_path_from_json = os.path.join(_PROJECT_ROOT_DIR, current_json_image_path)
            if os.path.exists(absolute_path_from_json):
                print(f"[*] Image for '{title}' found via existing JSON path: {current_json_image_path}. File exists.")
                local_image_found_and_json_updated = True
                needs_api_call = False
            else:
                print(f"[*] Image path '{current_json_image_path}' in JSON for '{title}', but file missing. Will check conventional path or download.")

        # 2. If not found via JSON path, or JSON path was invalid, check conventional local path
        if not local_image_found_and_json_updated:
            # Sanitize the base title once. This removes invalid characters but keeps spaces, hyphens, etc.
            base_sanitized_title = sanitize_filename(title)
            
            # Create a list of possible filenames to check, in order of preference
            # 1. Sanitized title with original spacing + .jpg
            # 2. Sanitized title with spaces replaced by hyphens + .jpg
            # 3. Sanitized title with spaces replaced by underscores + .jpg
            potential_filenames_in_order = [
                f"{base_sanitized_title}.jpg",
                f"{base_sanitized_title.replace(' ', '-')}.jpg",
                f"{base_sanitized_title.replace(' ', '_')}.jpg"
            ]
            
            # Deduplicate the list while preserving order
            unique_check_filenames = []
            for fn in potential_filenames_in_order:
                if fn not in unique_check_filenames:
                    unique_check_filenames.append(fn)

            found_conventional_file_details = None # To store (filepath, relative_json_path)

            for possible_filename in unique_check_filenames:
                expected_local_filepath = os.path.join(COVER_SAVE_DIR, possible_filename)
                if os.path.exists(expected_local_filepath):
                    relative_path_for_json = f"assets/{possible_filename}" # Uses forward slash
                    found_conventional_file_details = (expected_local_filepath, relative_path_for_json)
                    print(f"[*] Local image for '{title}' found by convention: {expected_local_filepath}")
                    break # Found a match, use this one
            
            if found_conventional_file_details:
                _local_filepath, rel_json_path = found_conventional_file_details
                if book_entry.get('image_path') != rel_json_path:
                    book_entry['image_path'] = rel_json_path
                    print(f"    Updated 'image_path' in JSON to: {rel_json_path}")
                    books_updated_count +=1
                else:
                    print(f"    'image_path' in JSON is already correct ({rel_json_path}).")
                local_image_found_and_json_updated = True
                needs_api_call = False

        # 3. If no local image found by either method, attempt download via API
        if needs_api_call:
            print(f"[*] No valid local image found for '{title}'. Attempting download via API...")
            downloaded_api_image_path = search_and_download_cover(title, author) # Returns "assets/filename.jpg" or None
            if downloaded_api_image_path:
                book_entry['image_path'] = downloaded_api_image_path
                print(f"[*] Successfully downloaded and updated 'image_path' for '{title}' to {downloaded_api_image_path}")
                books_updated_count +=1
            else:
                print(f"[-] Could not download image for '{title}'. 'image_path' in JSON will not be updated/added for this entry.")
            time.sleep(2)  # Rate limiting for API calls
        elif local_image_found_and_json_updated and not needs_api_call: # Only if local image was used
            time.sleep(0.1) # Shorter delay if local image was found and used

    # Write the updated books data back to the JSON file
    try:
        with open(BOOKS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(books_data, f, ensure_ascii=False, indent=2)
        print(f"\n[+] Processed {books_processed_count} books. Updated {BOOKS_JSON_PATH} with {books_updated_count} changes to image paths.")
    except IOError as e:
        print(f"[!] Error writing updated data to {BOOKS_JSON_PATH}: {e}")

if __name__ == "__main__":
    main()
