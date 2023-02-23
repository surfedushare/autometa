from collections import defaultdict
from bs4 import BeautifulSoup, NavigableString


class TikaWebsiteContentTransformer(object):

    domain_common_tag_frequencies = {}

    def __init__(self, content_threshold=0.2, include_anchor_tag=False):
        self.content_threshold = content_threshold
        self.domain_common_tag_frequencies = {}
        self.domain_doc_count = defaultdict(int)
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
        soup = BeautifulSoup(content, "html.parser")
        is_content = False
        content = []
        for descendant in soup.body.descendants:
            # First we see if we're dealing with content and we skip if it is not
            text = descendant.get_text(strip=True)
            if not text:
                continue
            if not is_content:
                if descendant.name not in self.common_tags:
                    continue
                if descendant.name in self.common_tags and frequencies[text] <= self.content_threshold:
                    is_content = True
            if descendant.name in self.common_tags and frequencies[text] > self.content_threshold:
                is_content = False
                continue
            # Here we're dealing with content so we try to add text
            if text and isinstance(descendant, NavigableString):
                content.append(text)
        return content
