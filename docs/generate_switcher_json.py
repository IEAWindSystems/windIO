#!/usr/bin/env python3

import json
import os
from git import Repo

# Set paths
REPO_DIR = "../" 
STATIC_DIR = os.path.join(REPO_DIR, 'docs', '_static')
# relies on soft link of latest tag to "latest"    
latest_branch = "latest"

DEPLOY_URL = os.environ.get("DEPLOY_URL", "https://ieawindsystems.github.io")

SWITCHER_JSON_PATH = os.path.join(STATIC_DIR, 'switcher.json')

# Open repo
repo = Repo(REPO_DIR)
print("REPO", repo.references)
for branch in repo.references:
    print("ref", branch.name, branch.path)
# Collect tags
tags = sorted([tag.name for tag in repo.tags])

# remove this when everything works
branches = sorted([
    ref.name for ref in repo.references
    if ref.path.startswith('refs/heads/') or ref.name.startswith('refs/remotes/')
])
print("branches and tags", branches, tags)
# Compose versions list
versions = []

# Add tags
print("Docs will be built for the following tags:")
for tag in tags:
    versions.append({"name": tag,
                     "version": tag, 
                     "url": f"{DEPLOY_URL}/{tag}/"})
    print(tag)

# Add branches that have test_doc in their name (excluding main/master already added)
print("Docs will be built for the following branches")
for branch in branches:
    if ("test_doc" not in branch) and (branch != "main"):
        continue
    else:
        version = {"name": branch,
                   "version": branch, 
                   "url": f"{DEPLOY_URL}/{branch}/"}
        versions.append(version)
    print(branch)
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

