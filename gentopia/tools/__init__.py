from .basetool import BaseTool
from .google_search import GoogleSearch
from .wikipedia import Wikipedia
from .wolfram_alpha import WolframAlpha
from .web_page import WebPage
from .arxiv_search import ArxivSearch

def load_tools(name: str) -> BaseTool:
    if name == "google_search":
        return GoogleSearch
    elif name == "wolfram_alpha":
        return WolframAlpha
    elif name == "web_page":
        return WebPage
    elif name == "arxiv_search":
        return ArxivSearch
    elif name == "wikipedia":
        return Wikipedia

    else:
        raise NotImplementedError
