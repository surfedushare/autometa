from typing import Any
import os
from collections import defaultdict, OrderedDict
from functools import reduce
from bs4 import BeautifulSoup, NavigableString


def _get_element_id(el):
    return f"{el.name}-{el.sourceline}-{el.sourcepos}"


def _get_element_parent(el):
    parent_elements = {"body", "ul", "table"}
    parent = el.parent
    while True:
        if parent.name in parent_elements:
            return parent
        parent = parent.parent


def _is_link_group_element(el: Any):
    if el.name != "a" and not isinstance(el, NavigableString) and not el.isspace or \
            not isinstance(el, NavigableString) and el.parent.name != "li" and el.sourcepos > 0:
        return False, not isinstance(el, NavigableString)
    return True, not isinstance(el, NavigableString)


def extract_link_groups(html_file_name, min_group_size=2):
    # Detect which lines are whitespace and which lines contain a tag at the beginning
    whitespace = set()
    tags = set()
    with open(os.path.join("samples", "common_tags", html_file_name)) as html_file:
        for line_number, line in enumerate(html_file.readlines()):
            line = line.strip()
            if len(line) == 0:
                whitespace.add(line_number+1)
            if line.startswith("<"):
                tags.add(line_number+1)
    # Parse the HTML in order to traverse it easily
    with open(os.path.join("samples", "common_tags", html_file_name)) as html_file:
        soup = BeautifulSoup(html_file, "html.parser")
    # Group all links by their parent
    links_by_parent = defaultdict(list)
    for link in soup.find_all("a"):
        text = link.get_text(strip=True)
        if not text:
            continue
        parent = _get_element_parent(link)
        if parent.name == "body" and link.sourceline not in tags:
            continue
        links_by_parent[_get_element_id(parent)].append(link)
    # Extract groups
    groups_by_parent = defaultdict(list)

    for parent, links in links_by_parent.items():
        groups = defaultdict(OrderedDict)
        group_index = 0

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
            groups_by_parent[parent].append(group)

    return groups_by_parent


def extract_root_link_groups(container):
    links = {}
    group_number = 0
    for child in container.children:
        is_group, is_link = _is_link_group_element(child)
        if not is_link or f"{child.sourceline}-{child.sourcepos}" in links:
            continue
        group = []
        for sibling in child.next_siblings:
            is_group, is_link = _is_link_group_element(sibling)
            if is_group and not is_link:
                continue
            elif is_group and is_link:
                group.append(sibling)
            else:
                break
        if len(group) <= 1:
            continue
        for link in group:
            links[f"{link.sourceline}-{link.sourcepos}"] = {
                "group": group_number,
                "text": link.get_text(strip=True),
                "href": link["href"]
            }
        group_number += 1
    return links, group_number


def extract_nested_link_groups(container, group_number):
    links = {}
    for child in container.find_all("a"):
        is_group, is_link = _is_link_group_element(child)
        if not is_link or f"{child.sourceline}-{child.sourcepos}" in links:
            continue
        group = [child]
        for sibling in child.parent.next_siblings:
            if isinstance(sibling, NavigableString):
                continue
            is_group, is_link = _is_link_group_element(sibling.find("a"))
            if is_group and not is_link:
                continue
            elif is_group and is_link:
                group.append(sibling.find("a"))
            else:
                break
        if len(group) <= 1:
            continue
        for link in group:
            links[f"{link.sourceline}-{link.sourcepos}"] = {
                "group": group_number,
                "text": link.get_text(strip=True),
                "href": link.get("href", None)
            }
    return links


def print_link_groups_from_file(html_file_name):
    print("Extracting groups")
    links = {}
    link_groups = extract_link_groups(html_file_name)
    group_index = 0
    for parent_id, groups in link_groups.items():
        for group in groups:
            for link_id, link in group.items():
                links[link_id] = {
                    "group": group_index,
                    "parent": parent_id,
                    "text": link.get_text(strip=True),
                    "href": link.get("href", None)
                }
            group_index += 1
    import json; print(json.dumps(links, indent=4))
