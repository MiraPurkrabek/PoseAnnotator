#!/bin/bash

set -euo pipefail

# Available datasets:
# 1. BOTTOM: 1UBjXSvejswtVddT6F7kcCVl6p4OnNEg1 (old, deprecated, used for debugging the app)
# 2. ???: give GDrive fileid as an argument to the script

# If fileid is not provided, download the default dataset
if [ -z "${1:-}" ]
then
    fileid="1gkQeZ5MWGGiGzL1l342izky_1ycXYS0I"
else
    fileid="${1}"
fi

# Change to the script's directory
cd "$(dirname "$0")"

# Temporary filename
filename="downloaded_data.zip"
cookie_file="./cookie"
confirm_page="./gdrive_confirm.html"

# Download the confirmation page and extract the actual download form Google Drive serves.
curl -c "${cookie_file}" -s -L "https://drive.google.com/uc?export=download&id=${fileid}" -o "${confirm_page}"

confirm_action="$(grep -o 'action="[^"]*"' "${confirm_page}" | head -n 1 | cut -d'"' -f2 || true)"
confirm_id="$(grep -o 'name="id" value="[^"]*"' "${confirm_page}" | head -n 1 | sed 's/.*value="//; s/"$//' || true)"
confirm_export="$(grep -o 'name="export" value="[^"]*"' "${confirm_page}" | head -n 1 | sed 's/.*value="//; s/"$//' || true)"
confirm_token="$(grep -o 'name="confirm" value="[^"]*"' "${confirm_page}" | head -n 1 | sed 's/.*value="//; s/"$//' || true)"
confirm_uuid="$(grep -o 'name="uuid" value="[^"]*"' "${confirm_page}" | head -n 1 | sed 's/.*value="//; s/"$//' || true)"

if [ -n "${confirm_action}" ] && [ -n "${confirm_token}" ]; then
    curl -Lb "${cookie_file}" -L \
        "${confirm_action}?id=${confirm_id:-${fileid}}&export=${confirm_export:-download}&confirm=${confirm_token}${confirm_uuid:+&uuid=${confirm_uuid}}" \
        -o "${filename}"
else
    # Small public files may download directly without a confirm token.
    curl -Lb "${cookie_file}" -L "https://drive.google.com/uc?export=download&id=${fileid}" -o "${filename}"
fi

rm -f "${cookie_file}" "${confirm_page}"

if ! unzip -tq "${filename}" >/dev/null; then
    echo "Downloaded file is not a valid ZIP archive. Google Drive likely returned an HTML page instead." >&2
    exit 1
fi

# Unzip the file and remove the zip file
unzip "${filename}" -d ./
rm $filename
