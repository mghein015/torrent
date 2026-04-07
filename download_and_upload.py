import subprocess
import os
import sys
import time
from huggingface_hub import HfApi

def download_and_upload(link, repo_id, token):
    save_path = os.path.abspath('./downloads')
    os.makedirs(save_path, exist_ok=True)

    # --- 1. aria2 Download ---
    print(f"Starting aria2c download to: {save_path}")
    
    # aria2c flags:
    # --seed-time=0: Stop immediately after download finishes
    # --summary-interval=10: Print progress every 10 seconds (cleaner logs)
    # --dht-entry-point: Help find peers in cloud networks
    cmd = [
        "aria2c",
        "--dir", save_path,
        "--seed-time", "0",
        "--summary-interval", "10",
        "--bt-enable-lpd", "true",
        "--enable-dht", "true",
        link
    ]

    try:
        # Run aria2c and stream output to the GitHub console
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        if process.returncode != 0:
            print(f"aria2c exited with error code {process.returncode}")
            return

    except Exception as e:
        print(f"Failed to run aria2c: {e}")
        return

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
        print("✅ Upload Finished successfully!")
    except Exception as e:
        print(f"❌ Upload failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python download_and_upload.py <link> <repo_id> <token>")
    else:
        download_and_upload(sys.argv[1], sys.argv[2], sys.argv[3])
