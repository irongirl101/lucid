import pandas as pd
from pathlib import Path


def load_documents(export_path):
    path = Path(export_path)

    if not path.exists():
        raise FileNotFoundError(f"Export not found: {path}")

    if path.is_dir():
        files = sorted(path.glob("*.parquet"))
        if not files:
            raise ValueError("No Parquet files found")

        df = pd.concat(
            [pd.read_parquet(file) for file in files],
            ignore_index=True
        )
    else:
        df = pd.read_parquet(path)

    required_columns = {"doc_id", "title", "content", "pagerank"}

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df = df.fillna({
        "title": "",
        "content": "",
        "pagerank": 0.0
    })

    return df.to_dict(orient="records")
