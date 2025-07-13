AWS_NODES_URL = "https://diagrams.mingrammer.com/docs/nodes/aws"

def fetch_aws_nodes():
    resp = requests.get(AWS_NODES_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    nodes = []
    current_category = None
    for tag in soup.find_all(["h2", "p"]):
        if tag.name == "h2":
            current_category = tag.get_text(strip=True)
            if current_category.startswith("aws."):
                current_category = current_category
            else:
                current_category = None
        elif tag.name == "p" and current_category:
            text = tag.get_text(strip=True)
            if text.startswith("diagrams.aws."):
                # Parse class and aliases
                parts = text.split(",")
                class_name = parts[0].strip()
                aliases = [p.replace("(alias)", "").strip() for p in parts[1:]] if len(parts) > 1 else []
                nodes.append({
                    "category": current_category,
                    "class": class_name,
                    "aliases": aliases
                })
    return nodes

def save_aws_nodes(nodes, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        for node in nodes:
            f.write(json.dumps(node) + "\n")
import requests
from bs4 import BeautifulSoup
import json
import os


EXAMPLES_URL = "https://diagrams.mingrammer.com/docs/getting-started/examples"
OUTPUT_DIR = "output"



def fetch_aws_examples():
    resp = requests.get(EXAMPLES_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    examples = []
    # Find all h2 sections and their following code blocks and images
    for h2 in soup.find_all("h2"):
        title = h2.get_text(strip=True)
        # Skip installation section
        if "install" in title.lower():
            continue
        # Gather all tags between this h2 and the next h2
        tags_between = []
        next_tag = h2
        while True:
            next_tag = next_tag.find_next_sibling()
            if not next_tag or next_tag.name == "h2":
                break
            tags_between.append(next_tag)

        # Recursively collect all code blocks and documentation text
        code_blocks = []
        doc_text = []
        def collect_code_and_text(tag):
            if tag.name == "pre":
                code_blocks.append(tag.get_text(strip=True))
            elif tag.name and tag.name.startswith("h"):
                return  # skip headers
            elif tag.name is not None:
                for child in tag.children:
                    if hasattr(child, 'name'):
                        collect_code_and_text(child)
            elif tag.string and tag.string.strip():
                doc_text.append(tag.string.strip())

        for tag in tags_between:
            collect_code_and_text(tag)

        # Only include if AWS is mentioned in the title or code
        aws_in_title = "aws" in title.lower()
        aws_in_code = any("aws" in cb.lower() for cb in code_blocks)
        if (aws_in_title or aws_in_code) and (code_blocks or doc_text):
            examples.append({
                "title": title,
                "documentation": "\n".join(doc_text),
                "code_examples": code_blocks
            })
    return examples


    # ...existing code... (function replaced above)



def save_examples(examples, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        for ex in examples:
            f.write(json.dumps(ex) + "\n")



def main():
    print(f"Crawling AWS examples from: {EXAMPLES_URL}")
    examples = fetch_aws_examples()
    print(f"Found {len(examples)} AWS usage/example blocks.")
    save_examples(examples, os.path.join(OUTPUT_DIR, "aws_examples.ndjson"))
    print(f"Saved to {OUTPUT_DIR}/aws_examples.ndjson")

    print(f"Crawling AWS nodes from: {AWS_NODES_URL}")
    nodes = fetch_aws_nodes()
    print(f"Found {len(nodes)} AWS node documentation blocks.")
    save_aws_nodes(nodes, os.path.join(OUTPUT_DIR, "aws_nodes.ndjson"))
    print(f"Saved to {OUTPUT_DIR}/aws_nodes.ndjson")


if __name__ == "__main__":
    main()
