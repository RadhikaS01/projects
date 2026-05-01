"""Deploy the MLWithUI Gradio app to a Hugging Face Space.

Usage:
  - Set environment variable `HF_TOKEN` to a valid Hugging Face token.
  - Run: `python deploy_to_hf.py --repo_id RadhikaS01/MLSpace`

The script will create the space (if missing), copy the app files and model,
and push them to the Space repository.
"""
import argparse
import os
import shutil
import tempfile
from huggingface_hub import HfApi


def prepare_files(src_base, tmpdir):
    """Copy necessary files into a temporary directory for push."""
    files_to_copy = [
        os.path.join(src_base, "app.py"),
        os.path.join(src_base, "requirements.txt"),
        os.path.join(src_base, "README.md"),
    ]

    # create models folder
    models_src = os.path.join(src_base, "models")
    models_dst = os.path.join(tmpdir, "models")
    os.makedirs(models_dst, exist_ok=True)

    for f in files_to_copy:
        shutil.copy(f, tmpdir)

    # copy model file if present
    model_file = os.path.join(models_src, "pipeline.joblib")
    if os.path.exists(model_file):
        shutil.copy(model_file, models_dst)
    else:
        print("Warning: model file not found; Space will deploy but predictions will fail until model uploaded.")
    # copy resources folder if present (so dataset is available in the Space)
    resources_src = os.path.join(src_base, "resources")
    resources_dst = os.path.join(tmpdir, "resources")
    if os.path.exists(resources_src):
        try:
            shutil.copytree(resources_src, resources_dst)
        except Exception as e:
            print(f"Warning: failed to copy resources folder: {e}")


def deploy(repo_id, src_base, hf_token):
    api = HfApi()
    # create space repo if it doesn't exist
    try:
        api.create_repo(repo_id=repo_id, repo_type="space", exist_ok=True)
    except Exception as e:
        print(f"create_repo warning: {e}")

    with tempfile.TemporaryDirectory() as tmpdir:
        prepare_files(src_base, tmpdir)

        # upload the prepared temporary folder contents to the Space repo
        # upload_folder will recursively upload files to the repository
        api.upload_folder(
            folder_path=tmpdir,
            path_in_repo="",
            repo_id=repo_id,
            repo_type="space",
            token=hf_token,
        )

    print(f"Deployed to space: https://huggingface.co/spaces/{repo_id}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo_id", required=True, help="Repo id like username/MLSpace")
    args = parser.parse_args()

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("Error: set HF_TOKEN environment variable to a valid Hugging Face token.")
        return

    src_base = os.path.dirname(__file__)
    deploy(args.repo_id, src_base, hf_token)


if __name__ == "__main__":
    main()
