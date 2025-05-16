#!/usr/bin/env python3

import json
import os
from git import Repo

# Set paths
REPO_DIR = "../" 
STATIC_DIR = os.path.join(REPO_DIR, 'docs', '_static')
# relies on soft link of latest tag to "latest"    
latest_branch = "latest"

DEPLOY_URL = os.environ.get("DEPLOY_URL", "")

SWITCHER_JSON_PATH = os.path.join(STATIC_DIR, 'switcher.json')

# Open repo
repo = Repo(REPO_DIR)

# Collect tags
tags = sorted([tag.name for tag in repo.tags])
print("TAGS", tags)
# Collect branches from origin

# remove this when everything works
branches = sorted([
    ref.name.replace("origin/", "")
    for ref in repo.remote().refs
    if not ref.name.endswith("/HEAD")
])

# Compose versions list
versions = []

# Add 'main' or 'master' if present in branches
if 'main' in branches:
    versions.append({"name": "main", "version": "main", "url": f"{DEPLOY_URL}/main/"})

# Add tags
for tag in tags:
    versions.append({"name": tag,
                     "version": tag, 
                     "url": f"{DEPLOY_URL}/{tag}/"})

# Add other branches (excluding main/master already added)
for branch in branches:
    if "test_doc" not in branch:
        continue
    if branch not in ['main', 'master'] and not any(v["version"] == branch for v in versions):
        version = {"name": branch,
                   "version": branch, 
                   "url": f"{DEPLOY_URL}/{branch}/"}
        versions.append(version)

# Add 'latest' entry pointing to latest_branch
versions.insert(0, {
    "name": "latest",
    "version": "latest",
    "url": f"{DEPLOY_URL}/{latest_branch}/",
    "preferred": "true"
})


# Write JSON file
with open(SWITCHER_JSON_PATH, "w") as f:
    json.dump(versions, f, indent=2)

print(f"✅ switcher.json written to: {SWITCHER_JSON_PATH}")

