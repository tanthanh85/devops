#!/usr/bin/env sh
set -eu

version="${TERRAFORM_VERSION:-1.16.3}"
target="${TERRAFORM_BIN:-$PWD/.tools/terraform}"

if [ -x "$target" ] && "$target" version | head -n 1 | grep -Fq "v${version}"; then
  exit 0
fi

case "$(uname -m)" in
  x86_64) terraform_arch="amd64" ;;
  aarch64|arm64) terraform_arch="arm64" ;;
  *) echo "Unsupported Terraform architecture: $(uname -m)" >&2; exit 1 ;;
esac

tool_dir=$(dirname "$target")
archive_name="terraform_${version}_linux_${terraform_arch}.zip"
archive="$tool_dir/$archive_name"
checksums="$tool_dir/terraform_${version}_SHA256SUMS"
checksum_entry="$tool_dir/terraform_${version}_${terraform_arch}.sha256"
base_url="https://releases.hashicorp.com/terraform/${version}"

mkdir -p "$tool_dir"
curl --fail --silent --show-error --location "$base_url/$archive_name" --output "$archive"
curl --fail --silent --show-error --location "$base_url/terraform_${version}_SHA256SUMS" --output "$checksums"
grep "  ${archive_name}$" "$checksums" > "$checksum_entry"
test -s "$checksum_entry"
(cd "$tool_dir" && sha256sum --check --status "$(basename "$checksum_entry")")
python3 -c 'import sys,zipfile; zipfile.ZipFile(sys.argv[1]).extract("terraform", sys.argv[2])' "$archive" "$tool_dir"
chmod 0755 "$target"
"$target" version
