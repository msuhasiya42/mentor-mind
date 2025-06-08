from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Resource:
    """Represents a learning resource with metadata"""
    title: str
    url: str
    description: str = ""
    platform: str = ""
    price: str = ""

    def __post_init__(self):
        """Validate and clean resource data"""
        self.title = self.title.strip() if self.title else ""
        self.url = self.url.strip() if self.url else ""
        self.description = self.description.strip() if self.description else ""
        self.platform = self.platform.strip() if self.platform else ""
        self.price = self.price.strip() if self.price else ""


@dataclass
class SearchResult:
    """Represents a search result from any search engine"""
    title: str
    url: str
    description: str = ""
    
    def to_resource(self, platform: str = "", price: str = "") -> Resource:
        """Convert search result to a Resource object"""
        return Resource(
            title=self.title,
            url=self.url,
            description=self.description,
            platform=platform,
            price=price
        ) 