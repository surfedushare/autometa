from typing import Any
import os
from bs4 import BeautifulSoup, NavigableString


def _is_link_group_element(el: Any):
    if el.name != "a" and not isinstance(el, NavigableString) and not el.isspace or \
            not isinstance(el, NavigableString) and el.parent.name != "li" and el.sourcepos > 0:
        return False, not isinstance(el, NavigableString)
    return True, not isinstance(el, NavigableString)


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
    with open(os.path.join("samples", "common_tags", html_file_name)) as html_file:
        soup = BeautifulSoup(html_file, "html.parser")
    print("Extracting body")
    links, group_count = extract_root_link_groups(soup.find("body"))
    print("Extracting unsorted lists")
    for group_number, unsorted_list in enumerate(soup.find_all("ul")):
        # print("ul", unsorted_list.sourceline, unsorted_list.sourcepos)
        links.update(extract_nested_link_groups(unsorted_list, group_number+group_count))
    import json; print(json.dumps(links, indent=4))
