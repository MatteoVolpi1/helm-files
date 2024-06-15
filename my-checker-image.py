import os
import requests
import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO)

image_mappings = json.loads(os.getenv("IMAGE_MAPPINGS"))

def get_dockerhub_image_digest(image_url):
    try:
        repo, tag = image_url.split(':')
        url = f"https://registry.hub.docker.com/v2/repositories/{repo}/tags/{tag}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['images'][0]['digest']
    except Exception as e:
        logging.error(f"Failed to get digest for {image_url}: {e}")
        return None

def main():
    for mapping in image_mappings:
        image_url = mapping['url']
        deployment_name = mapping['deployment']
        digest_file = f"/app/digests/{image_url.replace('/', '_').replace(':', '_')}.digest"
        new_digest = get_dockerhub_image_digest(image_url)
        
        if new_digest:
            try:
                if os.path.exists(digest_file):
                    with open(digest_file, 'r') as file:
                        old_digest = file.read().strip()
                    if old_digest != new_digest:
                        with open(digest_file, 'w') as file:
                            file.write(new_digest)
                        subprocess.run(["kubectl", "rollout", "restart", f"deployment/{deployment_name}"], check=True)
                        logging.info(f"Deployment {deployment_name} restarted due to image update.")
                else:
                    with open(digest_file, 'w') as file:
                        file.write(new_digest)
            except Exception as e:
                logging.error(f"Failed to process digest for {image_url}: {e}")
        else:
            logging.warning(f"Skipping update check for {image_url} due to failed digest retrieval.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
