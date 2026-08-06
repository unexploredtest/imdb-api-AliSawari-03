count = 0

with open("data/title.crew.tsv", "r", encoding="utf-8") as f:
    next(f)  # skip header
    for line in f:
        cols = line.rstrip("\n").split("\t")
        if len(cols) < 3:
            continue

        directors = cols[1]
        writers = cols[2]

        if directors != "\\N" and writers != "\\N" and "," not in directors and "," not in writers and directors == writers:
            count += 1

print(count)
