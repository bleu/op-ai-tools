# 002-governance-forum-202406014

This dataset is comprised of two files, both generated when runniing the script in in [op-9-create-optimism-forum-dataset](scripts/op-9-create-optimism-forum-dataset).

- site_info.json
- dataset.tar.gz

`site_info.json` is the bare result of calling Discourse's `/site.json` API at <https://gov.optimism.io/site.json>, and serves for us as an entrypoint to explore the data that's available through the forum's Discourse API.

`dataset.tar.gz` is a collection of JSONL documents created by `forum-dl`, providing as entrypoint the forum category pages in Optimism's governance forum.

## Reproducing and regenerating this dataset

This dataset cannot be reproduced _exactly_ because our script to generate the dataset completely disregards timestamps. We simply scrape all the data from the forum. Thus you'll get the most up to date version of this dateset when you run the script in [op-9-create-optimism-forum-dataset](scripts/op-9-create-optimism-forum-dataset).
