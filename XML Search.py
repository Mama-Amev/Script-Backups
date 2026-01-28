# Before using the script, do note that this monstrosity is held together
# with bubble gum, shoe laces, and prayer. There is an 80% chance this
# script will completely break on usage, so please be mindful of that.
# Main goal of this script is to scan through several hundred .XML
# files and put specific keywords into a .csv file. It is built
# for a specific usage, so it may not work entirely unless
# used on what it was built for. 


import os
import re
import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict

# === USER INPUT ===
KEYWORDS = ["tag1", "tag2"]   # not case-sensitive, require ALL these be present in the same video block
XML_FOLDER = r"C:\PATH\TO\FOLDER"
OUTPUT_FILE = "keyword_matches.csv"
# ==================

# normalize keywords
keywords = [k.strip().lower() for k in KEYWORDS if k and k.strip()]
if not keywords:
    raise SystemExit("No keywords provided in KEYWORDS list.")

def local_name(tag):
    """Return localname for a possibly namespaced tag."""
    return tag.split('}')[-1].lower()

def extract_number(url):
    if not isinstance(url, str):
        return None
    m = re.search(r'\((\d+)\)', url)
    return int(m.group(1)) if m else None

results = []
errors = []
matched_count = 0
processed_files = 0

for root_dir, _, files in os.walk(XML_FOLDER):
    for file in files:
        if not file.lower().endswith(".xml"):
            continue
        processed_files += 1
        filepath = os.path.join(root_dir, file)
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()

            # Heuristic: treat any element whose local-name is 'url' or 'video' or 'video' container as a single video block.
            # We'll iterate over all elements and treat those elements as candidate "video blocks".
            candidate_blocks = []
            for elem in root.iter():
                ln = local_name(elem.tag)
                if ln in ("url", "video", "video:video", "videoplaylist", "entry"):  # common containers
                    candidate_blocks.append(elem)

            # If none found, fallback to top-level children
            if not candidate_blocks:
                candidate_blocks = list(root)

            # For each candidate, extract:
            # - all child texts (concatenated) for free-text search
            # - tag-like child elements (tag, video:tag, keywords, media:keywords, category)
            for block in candidate_blocks:
                # collect all text in block
                texts = []
                tag_values = []
                for e in block.iter():
                    if e.text and e.text.strip():
                        texts.append(e.text.strip())
                    # also consider attributes as possible tag carriers
                    for attr_val in (e.attrib.values() if e.attrib else []):
                        if attr_val and attr_val.strip():
                            texts.append(attr_val.strip())

                    ln = local_name(e.tag)
                    # collect common tag-like element names explicitly
                    if ln in ("tag", "tags", "video_tag", "video:tag", "keyword", "keywords", "media:keywords", "category"):
                        # some keyword containers may be comma/pipe separated
                        val = (e.text or "").strip()
                        if val:
                            # split common separators into individual tag values
                            for part in re.split(r'[,|/;]\s*', val):
                                if part:
                                    tag_values.append(part.strip().lower())

                combined_text = " ".join(texts).lower()
                tag_set = set(tv.lower() for tv in tag_values)

                # Primary check: all keywords present in tag_set (exact/tag matching)
                all_in_tags = all(any(kw == t or kw in t for t in tag_set) for kw in keywords) if tag_set else False

                # Secondary fallback: all keywords appear somewhere in the block text
                all_in_text = all(kw in combined_text for kw in keywords)

                if all_in_tags or all_in_text:
                    # find a URL for this block if present
                    url = None
                    # prefer a child <loc> or <url> or <link> element
                    for e in block.iter():
                        if local_name(e.tag) in ("loc", "link", "url", "locurl", "video_url"):
                            if e.text and e.text.strip():
                                url = e.text.strip()
                                break

                    # assemble matched tag list to write
                    matched_tags = ", ".join(sorted(tag_set)) if tag_set else ""
                    results.append({
                        "file": file,
                        "url": url,
                        "matched_keywords_required": ", ".join(keywords),
                        "matched_tags_found": matched_tags,
                        "matched_text_snippet": (combined_text[:400] + "...") if len(combined_text) > 400 else combined_text
                    })
                    matched_count += 1

        except Exception as e:
            errors.append((file, str(e)))
            print(f"[ERROR] Parsing {file}: {e}")

# Save CSV
if results:
    df = pd.DataFrame(results)
    df['number'] = df['url'].apply(extract_number)
    df = df.sort_values(by=['number'], na_position='first')
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Done. Processed {processed_files} XML files, found {matched_count} matching video blocks. Results -> {OUTPUT_FILE}")
else:
    print(f"Processed {processed_files} XML files. No matches found for ALL keywords: {keywords}")

if errors:
    print("\nFiles with parse errors (sample):")
    for f, msg in errors[:10]:
        print(f" - {f}: {msg}")
