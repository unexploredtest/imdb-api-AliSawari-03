from pathlib import Path
import urllib.request
import gzip
import shutil

from datetime import datetime
import pandas as pd

na_val = '\\N'

def download_data():
    urls = [
        "https://datasets.imdbws.com/name.basics.tsv.gz",
        "https://datasets.imdbws.com/title.crew.tsv.gz",
        "https://datasets.imdbws.com/title.akas.tsv.gz",
    ]

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    for url in urls:
        filename = url.split("/")[-1]
        gz_path = data_dir / filename
        out_path = data_dir / filename[:-3]  # remove .gz

        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, gz_path)
        print(f"Downloaded {filename}")

        print(f"Extracting {filename}...")
        with gzip.open(gz_path, "rb") as f_in, open(out_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        print(f"Extracted to {out_path.name}")

def process_endpoint_1_data():
    print("Reading name.basics.tsv")
    name_basics = pd.read_csv('data/name.basics.tsv', sep='\t', na_values=na_val, low_memory=False)
    print("Done reading name.basics.tsv")

    print("Reading title.crew.tsv")
    title_crew = pd.read_csv('data/title.crew.tsv', sep='\t', na_values=na_val, low_memory=False)
    print("Done reading title.crew.tsv")

    print("Reading title.akas.tsv")
    chunks = pd.read_csv(
        "data/title.akas.tsv",
        sep="\t",
        na_values=na_val,
        chunksize=1_000_000,
        low_memory=False,
    )

    parts = []
    seen = set()

    total_chunks = 59

    for i, chunk in enumerate(chunks, start=1):
        percent = (i / total_chunks) * 100
        print(f"Reading title.akas.tsv ({percent:.1f}% read)")
        chunk = chunk[chunk["types"].eq("original")]
        chunk = chunk[~chunk["titleId"].isin(seen)]
        seen.update(chunk["titleId"])
        parts.append(chunk)

    title_akas = pd.concat(parts, ignore_index=True)
    print("Done reading title.akas.tsv")

    # Media that has the exact same crew and only one (director and writer)
    same_title_crew = title_crew[
        (title_crew["directors"] == title_crew["writers"]) &
        (~title_crew["directors"].str.contains(",", na=False)) &
        (~title_crew["writers"].str.contains(",", na=False))
    ]

    # Delete the ones that are probably dead
    same_title_crew_alive = same_title_crew.rename(columns={"directors": "nconst"}).merge(
        name_basics[["nconst", "primaryName", "birthYear", "deathYear"]],
        on="nconst",
        how="left"
    )

    MAX_AGE = 100
    current_year = datetime.now().year

    same_title_crew_alive = same_title_crew_alive[
        same_title_crew_alive["deathYear"].isna() &
        same_title_crew_alive["birthYear"].notna() &
        ((2026 - same_title_crew_alive["birthYear"]) < current_year)
    ]

    # Merge titles
    same_title_crew_alive["title"] = same_title_crew_alive["tconst"].map(title_akas.groupby("titleId")["title"].first())
    same_title_crew_alive = same_title_crew_alive.dropna(subset=["title"])

    same_title_crew_alive.to_csv("endpoint_1_data.csv", index=False)

if __name__ == "__main__":
    download_data()
    process_endpoint_1_data()
