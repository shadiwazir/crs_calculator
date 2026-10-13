#!/usr/bin/env bash
# Build, tag and push the CRS calculator image to Docker Hub.
#
# Usage: DOCKERHUB_USER=<user> scripts/publish.sh [version]
#   version defaults to the one in pyproject.toml. Pushes <version> and latest.
# Log in first with `docker login`.
set -euo pipefail

cd "$(dirname "$0")/.."

: "${DOCKERHUB_USER:?Set DOCKERHUB_USER to your Docker Hub username}"
IMAGE="${DOCKERHUB_USER}/crs-calculator"
VERSION="${1:-$(sed -n 's/^version = "\(.*\)"/\1/p' pyproject.toml)}"
[ -n "$VERSION" ] || { echo "Could not determine version" >&2; exit 1; }

echo "Building ${IMAGE}:${VERSION}"
docker build -t "${IMAGE}:${VERSION}" -t "${IMAGE}:latest" .

echo "Pushing ${IMAGE}:${VERSION} and ${IMAGE}:latest"
docker push "${IMAGE}:${VERSION}"
docker push "${IMAGE}:latest"
echo "Published ${IMAGE}:${VERSION}"
