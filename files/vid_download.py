import requests
import m3u8
from Crypto.Cipher import AES
from tqdm import tqdm
import os
from concurrent.futures import ThreadPoolExecutor

# Headers to bypass protection
headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,te;q=0.8,hi;q=0.7",
    "cache-control": "no-cache",
    "origin": "https://www.miruro.tv",
    "pragma": "no-cache",
    "referer": "https://www.miruro.tv/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
}

def download_decrypt_merge(title, m3u8_file='video.m3u8'):
    """
    Downloads and decrypts .ts video segments from an M3U8 playlist and merges them into a single MP4 file.

    Args:
        title (str or int): The filename (without extension) for the final .mp4 file.
        m3u8_file (str): Path to the downloaded M3U8 file.
    """
    print(f"📥 Processing M3U8: {m3u8_file}")

    # Step 1: Load the m3u8 file
    playlist = m3u8.load(m3u8_file)

    # Step 2: Get AES-128 Key
    key_uri = playlist.keys[0].uri
    key_response = requests.get(key_uri, headers=headers)
    key = key_response.content

    # Step 3: Download and Decrypt Segments in Parallel
    def download_and_decrypt(segment):
        segment_url = segment.uri
        segment_data = requests.get(segment_url, headers=headers).content
        cipher = AES.new(key, AES.MODE_CBC, iv=key)
        decrypted_data = cipher.decrypt(segment_data)
        return decrypted_data

    print("⏳ Downloading and decrypting segments...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        decrypted_segments = list(tqdm(executor.map(download_and_decrypt, playlist.segments), total=len(playlist.segments)))

    # Step 4: Merge all decrypted segments into one file
    ts_file = f"{title}.ts"
    with open(ts_file, 'wb') as final_file:
        for segment in decrypted_segments:
            final_file.write(segment)

    # Step 5: Rename the final file to .mp4
    mp4_file = f"{title}.mp4"
    os.rename(ts_file, mp4_file)

    print(f"✅ Done! Video saved as '{mp4_file}'.")


def download_m3u8(url, filename="video.m3u8"):
    """
    Downloads an .m3u8 playlist file from the provided URL and saves it locally.

    Args:
        url (str): The m3u8 URL.
        filename (str): The output filename (default is 'video.m3u8').
    """
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,te;q=0.8,hi;q=0.7",
        "cache-control": "no-cache",
        "origin": "https://www.miruro.tv",
        "pragma": "no-cache",
        "referer": "https://www.miruro.tv/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    }

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise an error for bad status codes

        with open(filename, 'w', encoding='utf-8') as file:
            file.write(response.text)

        print(f"✅ '{filename}' downloaded successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to download m3u8 file: {e}")





# # Example usage:
# video_flag  =  download_m3u8("https://prxy.miruro.to/m3u8/?url=https%3A%2F%2Fvault-09.padorupado.ru%2Fstream%2F09%2F01%2Fd8d2416bb98373498ca9392aaa9a2b2f7c52263536496ddd918df8a2a41d4848%2Fuwu.m3u8")

# if video_flag:    

#     download_decrypt_merge(title=12)
