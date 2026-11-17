
import os
import shutil
import uuid
from pathlib import Path

from app.data_loader import load_documents


def publish_version(export_path, serving_root="data/serving"):
    source = Path(export_path)
    root = Path(serving_root)
    root.mkdir(parents=True, exist_ok=True)

    # Validate before changing the active version
    documents = load_documents(source)

    if not documents:
        raise ValueError("Export contains no documents")

    versions = [
        int(p.name[1:])
        for p in root.glob("v*")
        if p.is_dir() and p.name[1:].isdigit()
    ]

    next_version = max(versions, default=0) + 1
    version_name = f"v{next_version}"

    staging = root / f".staging-{uuid.uuid4().hex}"
    destination = root / version_name

    try:
        staging.mkdir()

        if source.is_file():
            shutil.copy2(source, staging / source.name)
        else:
            for file in source.glob("*.parquet"):
                shutil.copy2(file, staging / file.name)

        staging.rename(destination)

        # Atomically switch the active version
        temporary_link = root / f".current-{uuid.uuid4().hex}"
        temporary_link.symlink_to(version_name)
        os.replace(temporary_link, root / "current")

        return {
            "version": version_name,
            "documents": len(documents),
            "status": "activated"
        }

    except Exception:
        if staging.exists():
            shutil.rmtree(staging)
        if destination.exists() and not (root / "current").is_symlink():
            shutil.rmtree(destination)
        raise
