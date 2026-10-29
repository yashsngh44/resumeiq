import sys
import os
import dulwich.porcelain as porcelain
from pathlib import Path

def main():
    repo_dir = Path(__file__).resolve().parent
    print(f"[*] Repository directory: {repo_dir}")

    # Check for target remote URL or argument
    if len(sys.argv) > 1:
        remote_url = sys.argv[1].strip()
    else:
        token = os.environ.get("GITHUB_TOKEN", "").strip()
        repo_name = os.environ.get("GITHUB_REPO", "resumeiq").strip()
        username = os.environ.get("GITHUB_USER", "yashsngh44").strip()
        if token:
            remote_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
        else:
            remote_url = f"https://github.com/{username}/{repo_name}.git"

    print(f"[*] Target Remote: {remote_url.split('@')[-1] if '@' in remote_url else remote_url}")

    try:
        # Add remote if not already present
        repo = porcelain.open_repo(str(repo_dir))
        try:
            porcelain.remote_add(repo, "origin", remote_url)
            print("[+] Remote 'origin' added successfully.")
        except Exception:
            # Update existing origin
            config = repo.get_config()
            config.set(("remote", "origin"), "url", remote_url.encode())
            config.write_to_path()
            print("[+] Remote 'origin' updated.")

        print("[*] Pushing 'main' branch to GitHub...")
        porcelain.push(repo, remote_location="origin", refspecs="refs/heads/master:refs/heads/main")
        print("[✔] Successfully pushed to GitHub!")
    except Exception as e:
        print(f"[!] Push failed: {str(e)}")
        print("\nIf authentication is required, you can:")
        print("1. Set your GitHub Personal Access Token:")
        print("   $env:GITHUB_TOKEN='ghp_your_token_here'")
        print("   python push_to_github.py")
        print("2. Or push using Git credentials:")
        print("   git push -u origin main")

if __name__ == "__main__":
    main()
