import libtorrent as lt
import time
import sys
import os
from huggingface_hub import HfApi

def download_and_upload(link, repo_id, token):
    # --- 1. Torrent Download Logic ---
    ses = lt.session({'listen_interfaces': '0.0.0.0:6881'})
    
    save_path = os.path.abspath('./downloads')
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    if link.startswith("magnet:?"):
        params = lt.parse_magnet_uri(link)
        params.save_path = save_path  # Use dot notation for objects
    else:
        info = lt.torrent_info(link)
        params = {
            'ti': info,
            'save_path': save_path
        }

    handle = ses.add_torrent(params)
    
    print(f"Starting download to: {save_path}")
    
    # Wait for metadata
    while not handle.has_metadata():
        time.sleep(1)
    
    print(f"Metadata acquired for: {handle.status().name}")
    
    # Download loop
    while handle.status().state != lt.torrent_status.seeding:
        s = handle.status()
        print(f'Progress: {s.progress * 100:.2f}% | '
              f'DL: {s.download_rate / 1000:.1f} kB/s | '
              f'Peers: {s.num_peers}', end='\r')
        
        if s.state == lt.torrent_status.finished:
            break
        time.sleep(5)

    print("\nDownload Complete!")

    # --- 2. Hugging Face Upload Logic ---
    print(f"Uploading to Hugging Face: {repo_id}...")
    api = HfApi()
    
    try:
        api.upload_folder(
            folder_path=save_path,
            repo_id=repo_id,
            repo_type="dataset", 
            token=token
        )
        print("Upload Finished successfully!")
    except Exception as e:
        print(f"Upload failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python script.py <link> <repo_id> <token>")
    else:
        download_and_upload(sys.argv[1], sys.argv[2], sys.argv[3])
