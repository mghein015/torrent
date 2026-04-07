import libtorrent as lt
import time
import sys
import os
from huggingface_hub import HfApi

def download_and_upload(link, repo_id, token):
    # --- 1. Torrent Download Logic ---
    ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})
    
    if link.startswith("magnet:?"):
        params = lt.parse_magnet_uri(link)
    else:
        info = lt.torrent_info(link)
        params = {'ti': info}

    save_path = './downloads'
    params['save_path'] = save_path
    handle = ses.add_torrent(params)
    
    print(f"Starting download to: {save_path}")
    while not handle.has_metadata():
        time.sleep(1)
    
    print("Metadata acquired. Downloading...")
    while handle.status().state != lt.torrent_status.seeding:
        s = handle.status()
        print(f'Progress: {s.progress * 100:.2f}% | Peers: {s.num_peers}', end='\r')
        time.sleep(5)

    print("\nDownload Complete!")

    # --- 2. Hugging Face Upload Logic ---
    print(f"Uploading to Hugging Face: {repo_id}...")
    api = HfApi()
    
    api.upload_folder(
        folder_path=save_path,
        repo_id=repo_id,
        repo_type="dataset",  # Can be "model", "dataset", or "space"
        token=token
    )
    print("Upload Finished!")

if __name__ == "__main__":
    # Expecting: python script.py <link> <repo_id> <token>
    if len(sys.argv) < 4:
        print("Error: Missing arguments.")
    else:
        download_and_upload(sys.argv[1], sys.argv[2], sys.argv[3])
