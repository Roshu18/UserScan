import requests
import logging
from utils.config import DEFAULT_HEADERS

# Setup logging for debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def check_site(site_config, username):
    """
    Checks if a username exists on a given site.

    :param site_config: Dictionary with site details
    :param username: Username to check
    :return: Tuple (site_name, status)
    """
    name = site_config.get("name", "Unknown")
    url_template = site_config.get("url")

    if not url_template:
        logging.error(f"❌ No URL template found for {name}")
        return name, "error"

    url = url_template.format(username=username)
    method = site_config.get("method", "GET").upper()
    valid_statuses = site_config.get("valid_status_codes", [200])
    error_text = site_config.get("error_text")
    headers = site_config.get("headers", {})
    timeout = site_config.get("timeout", 10)
    data = site_config.get("data", {})

    merged_headers = {**DEFAULT_HEADERS, **headers}

    try:
        logging.info(f"🔍 Checking {name}: {url} using {method}")

        if method == "GET":
            response = requests.get(url, headers=merged_headers, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, headers=merged_headers, timeout=timeout, data=data)
        else:
            logging.error(f"🚨 Unsupported HTTP method: {method} for {name}")
            return name, "error"

        if response.status_code in valid_statuses:
            if error_text and error_text in response.text:
                return name, "not_found"
            return name, "found"
        else:
            return name, "not_found"

    except requests.exceptions.Timeout:
        logging.error(f"⏳ Timeout for {name}")
        return name, "error"

    except requests.exceptions.ConnectionError:
        logging.error(f"🚫 Connection error for {name}")
        return name, "error"

    except requests.exceptions.RequestException as e:
        logging.error(f"⚠️ Request failed for {name}: {e}")
        return name, "error"