from typing import AnyStr

import requests
from bs4 import BeautifulSoup

from .basetool import *


class WebPage(BaseTool):
    """Tool that adds the capability to query the Google search API."""

    name = "web_page"
    description = "A tool to retrieve web pages through url. Useful when you have a url and need to find detailed information inside." \
                  "You must make sure that the url is real and correct." \
                  "Input should be a url."

    args_schema: Optional[Type[BaseModel]] = create_model("WebPageArgs", url=(str, ...))

    def _run(self, url: AnyStr) -> str:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            text = ' '.join(line for line in lines if line)[:4096] + '...'
            return text
        except:
            return "Error: Invalid URL."

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
