from typing import AnyStr
from .basetool import *
from .utils.document_loaders.text_loader import TextLoader
from .utils.vector_store import VectorstoreIndexCreator


class SearchDocArgs(BaseModel):
    doc_path: str = Field(..., description="the path to read the file.")
    query: str = Field(..., description="the query string to retrieve similar search.")


class SearchDoc(BaseTool):
    name = "search_doc"
    args_schema: Optional[Type[BaseModel]] = SearchDocArgs
    description: str = f"A search engine looking for relevant text chunk in the provided path to a file." \
                       f"Input should be a search query."

    def _run(self, doc_path, query) -> AnyStr:
        loader = TextLoader(doc_path)
        vector_store = VectorstoreIndexCreator().from_loaders([loader])
        evidence = vector_store.similarity_search(query, k=1)[0].page_content
        return evidence

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
