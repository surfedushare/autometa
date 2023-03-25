from collections import defaultdict, OrderedDict
from functools import reduce
from bs4 import BeautifulSoup, NavigableString


class TikaWebsiteContentTransformer(object):

    domain_common_tag_frequencies = {}

    def __init__(self, content_threshold=0.2, include_anchor_tag=False, min_link_group_size=2):
        self.content_threshold = content_threshold
        self.domain_common_tag_frequencies = {}
        self.domain_doc_count = defaultdict(int)
        self.min_link_group_size = min_link_group_size
        self.common_tags = [f"h{header_number}" for header_number in range(1, 7)]
        if include_anchor_tag:
            self.common_tags.append("a")

    def _parse_domain(self, domain):
        if domain.startswith("www"):
            domain = domain.replace("www.", "")
        if domain == "youtu.be":
            return "youtube.com"
        elif "infonu.nl" in domain:
            return "infonu.nl"
        return domain

    @staticmethod
    def _get_element_id(el):
        if isinstance(el, NavigableString):
            return None
        return f"{el.name}-{el.sourceline}-{el.sourcepos}"

    @staticmethod
    def _get_element_parent(el):
        parent_elements = {"body", "ul", "table"}
        parent = el.parent
        while True:
            if parent.name in parent_elements:
                return parent
            parent = parent.parent

    def parse_content(self, content):
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

        # Group all links by their parent, skip invalid links and determine link line-range
        links_by_parent = defaultdict(list)
        first_link = None
        last_link = None
        for link in soup.find_all("a"):
            if not first_link:
                first_link = link
            if not last_link or last_link.sourceline < link.sourceline:
                last_link = link
            text = link.get_text(strip=True)
            if not text:
                continue
            parent = self._get_element_parent(link)
            if parent.name == "body" and link.sourceline not in tags:
                continue
            links_by_parent[self._get_element_id(parent)].append(link)
        link_half_way_line = first_link.sourceline + int((last_link.sourceline - first_link.sourceline) / 2) if \
            first_link and last_link else 0

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
                groups[group_index][self._get_element_id(previous)] = previous
                groups[group_index][self._get_element_id(current)] = current
                return current
            reduce(reduce_links, links)

            for group_index, group in groups.items():
                if len(group) < self.min_link_group_size:
                    continue
                for link_id, link in group.items():
                    links_info[link_id] = {
                        "at_start": link.sourceline <= link_half_way_line if link_half_way_line else None,
                        "group": group_index,
                        "parent": parent_id,
                        "text": link.get_text(strip=True),
                        "href": link.get("href", None)
                    }

        return soup, links_info

    def fit(self, data):
        # First we load all common tags into a mapping by domain
        for domain, content in data:
            domain = self._parse_domain(domain)
            self.domain_doc_count[domain] += 1
            if domain not in self.domain_common_tag_frequencies:
                self.domain_common_tag_frequencies[domain] = defaultdict(int)
            soup = BeautifulSoup(content, "html.parser")
            for common_tag in self.common_tags:
                for tag in soup.find_all(common_tag):
                    text = tag.get_text(strip=True)
                    if not text:
                        continue
                    self.domain_common_tag_frequencies[domain][text] += 1
        # Express per domain the common tag frequency as a fraction of the total amount of documents
        for domain, counts in self.domain_common_tag_frequencies.items():
            for tag, count in counts.items():
                counts[tag] = count / self.domain_doc_count[domain]

    def transform(self, data):
        domain, content = data
        domain = self._parse_domain(domain)
        frequencies = self.domain_common_tag_frequencies[domain]
        soup, links = self.parse_content(content)
        is_content = False
        content = []
        for descendant in soup.body.descendants:
            # First we see if we're dealing with content and we skip if it is not
            text = descendant.get_text(strip=True)
            if not text:
                continue
            link_info = links.get(self._get_element_id(descendant), None)
            if not is_content:
                if descendant.name not in self.common_tags:
                    continue
                if descendant.name in self.common_tags and frequencies[text] <= self.content_threshold:
                    if descendant.name != "a":
                        is_content = True
                    has_content = len(content)
                    is_internal_link = link_info and (link_info["href"][0] in ["/", "#"] or domain in link_info["href"])
                    if has_content and is_internal_link and link_info["at_start"]:
                        is_content = True
            if descendant.name in self.common_tags and frequencies[text] > self.content_threshold:
                is_content = False
                continue
            # Here we're dealing with content so we try to add text
            if text and isinstance(descendant, NavigableString):
                content.append(text)
        return content
