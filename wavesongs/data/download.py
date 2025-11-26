# download audio
"""
Download data
"""

import requests
import re

def xc_url(url: str) -> str:
    """_summary_

    Args:
        url (str): _description_

    Returns:
        str|None: _description_
    """
    response = requests.get(url)
    if response.status_code == 200:
        filename = f"{url.split('/')[-2]}.wav"  # Default name
        cd = response.headers.get("Content-Disposition")
        if cd:
            match = re.search('filename="?([^";]+)"?', cd)
            if match:
                filename = match.group(1)
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Downloaded audio to {filename}")
        return filename
    else:
        print(f"Failed to download. Status code: {response.status_code}")
        return ""