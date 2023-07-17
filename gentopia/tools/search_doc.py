from typing import AnyStr
from .basetool import *
from .utils.document_loaders.text_loader import TextLoader
from .utils.vector_store import VectorstoreIndexCreator


class SearchDoc(BaseTool):
    name = "SearchDoc"
    args_schema: Optional[Type[BaseModel]] = create_model("SearchDocArgs", query=(str, ...))
    doc_path: Optional[str] = None
    doc_name: Optional[str] = ""
    description: str = f"A search engine looking for relevant text chunk in a document: {doc_name}. " \
                       f"Input should be a search query."

    def _run(self, query: AnyStr) -> AnyStr:
        loader = TextLoader(self.doc_path)
        vector_store = VectorstoreIndexCreator().from_loaders([loader])
        evidence = vector_store.similarity_search(query, k=1)[0].page_content
        return evidence

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
