#!/usr/bin/env bash
set -eu -o pipefail

HELM_CHART="charts/myapp/Chart.yaml"

if ! [[ "${1:-}" =~ ^(patch|minor|major)$ ]]; then
    echo "🚨 Usage $0 patch|minor|major: to bump the corresponding version"
    exit 1
fi

# create new version with poetry
echo "📦️ Update poetry version"
VERSION=$(poetry version "$1" -s)
export VERSION

# update charts
if [ -f "$HELM_CHART" ]; then
    echo "📦️ Update helm chart version"
    yq e '.version = strenv(VERSION)'    -i "$HELM_CHART"
    yq e '.appVersion = strenv(VERSION)' -i "$HELM_CHART"
fi

# add updated files to staging
git add pyproject.toml
if [ -f "$HELM_CHART" ]; then
    git add "$HELM_CHART"
fi

git --no-pager diff --staged 

echo ""
echo ""
echo ""

# ask confirmation before commit
read -p "💡 Commit changes and create tag? [y/n] " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit --message "🔖 New release: $VERSION"
    git tag "$VERSION"

    # ask confirmation before push to origin
    read -p "💡 Push to origin? [y/n] " -n 1 -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push 
        git push --tags
    fi
else
    # revert changes
    echo "🤯 Reverting changes ..."
    git reset HEAD pyproject.toml
    git checkout pyproject.toml
    if [ -f "$HELM_CHART" ]; then
        git reset HEAD "$HELM_CHART"
        git checkout   "$HELM_CHART"
    fi
fi
