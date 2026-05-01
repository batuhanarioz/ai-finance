from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS, PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, DirectoryLoader
import os
from backend.core.config import settings

class RAGManager:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        self.vector_store = None

    def load_documents(self, directory_path: str):
        """Klasördeki tüm dökümanları yükler ve indeksler."""
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
            
        loader = DirectoryLoader(directory_path, glob="**/*.md", loader_cls=TextLoader)
        docs = loader.load()
        chunks = self.text_splitter.split_documents(docs)
        
        try:
            # PGVector kullanarak veritabanına kaydet
            self.vector_store = PGVector.from_documents(
                embedding=self.embeddings,
                documents=chunks,
                collection_name="finagent_docs",
                connection_string=settings.DB_URL,
                pre_delete_collection=True # Her yüklemede temizle
            )
            print(f"✅ PGVector: {len(docs)} döküman veritabanına indekslendi.")
        except Exception as e:
            print(f"⚠️ PGVector bağlantı hatası, FAISS'e geçiliyor: {e}")
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)

    def add_document(self, file_path: str):
        """Yeni bir dökümanı çalışma anında vektör veritabanına ekler."""
        loader = TextLoader(file_path)
        doc = loader.load()
        chunks = self.text_splitter.split_documents(doc)
        
        if self.vector_store:
            self.vector_store.add_documents(chunks)
        else:
            self.load_documents("backend/data")
        print(f"🆕 Yeni döküman eklendi: {file_path}")

    def query(self, text: str, k: int = 3):
        """Anlamsal arama yapar."""
        if not self.vector_store:
            return "Bilgi tabanı boş."
        
        docs = self.vector_store.similarity_search(text, k=k)
        return "\n".join([doc.page_content for doc in docs])

rag_engine = RAGManager()
# Başlangıç verilerini yükle
rag_engine.load_documents("backend/data")
