from .basetool import BaseTool
from .google_search import GoogleSearch
from .wikipedia import Wikipedia
from .wolfram_alpha import WolframAlpha
from .web_page import WebPage
from .arxiv_search import ArxivSearch
from .weather import *
from .shell import RunShell
from .search_doc import SearchDoc
from .code_interpreter import PythonCodeInterpreter


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
    elif name == "get_future_weather":
        return GetFutureWeather
    elif name == "get_today_weather":
        return GetTodayWeather
    elif name == "bash_shell":
        return RunShell
    elif name == "search_doc":
        return SearchDoc
    elif name == "run_python_code":
        return PythonCodeInterpreter



    else:
        raise NotImplementedError
