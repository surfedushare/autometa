import os
from collections import defaultdict, OrderedDict
from functools import reduce
from bs4 import BeautifulSoup


def _get_element_id(el):
    return f"{el.name}-{el.sourceline}-{el.sourcepos}"


def _get_element_parent(el):
    parent_elements = {"body", "ul", "table"}
    parent = el.parent
    while True:
        if parent.name in parent_elements:
            return parent
        parent = parent.parent


def extract_link_info(content, min_group_size=2):
    # Detect which lines are whitespace and which lines contain a tag at the beginning
    whitespace = set()
    tags = set()
    for line_number, line in enumerate(content.split("\n")):
        line = line.strip()
        if len(line) == 0:
            whitespace.add(line_number+1)
        if line.startswith("<"):
            tags.add(line_number+1)

    # Parse the HTML in order to traverse it easily
    soup = BeautifulSoup(content, "html.parser")

    # Group all links by their parent and skip invalid links
    links_by_parent = defaultdict(list)
    for link in soup.find_all("a"):
        text = link.get_text(strip=True)
        if not text:
            continue
        parent = _get_element_parent(link)
        if parent.name == "body" and link.sourceline not in tags:
            continue
        links_by_parent[_get_element_id(parent)].append(link)

    # Group links together and store some information about them
    links_info = {}
    group_index = 0

    for parent_id, links in links_by_parent.items():
        groups = defaultdict(OrderedDict)
        group_index += 1

        def reduce_links(previous, current):
            nonlocal group_index
            if previous is None:
                return current
            for line_number in range(previous.sourceline+1, current.sourceline):
                if line_number not in whitespace:
                    group_index += 1
                    return current
            groups[group_index][_get_element_id(previous)] = previous
            groups[group_index][_get_element_id(current)] = current
            return current
        reduce(reduce_links, links)

        for group_index, group in groups.items():
            if len(group) < min_group_size:
                continue
            for link_id, link in group.items():
                links_info[link_id] = {
                    "group": group_index,
                    "parent": parent_id,
                    "text": link.get_text(strip=True),
                    "href": link.get("href", None)
                }

    return links_info


def print_link_info_from_file(html_file_name):
    with open(os.path.join("samples", "common_tags", html_file_name)) as html_file:
        content = html_file.read()
    links = extract_link_info(content)
    import json; print(json.dumps(links, indent=4))
