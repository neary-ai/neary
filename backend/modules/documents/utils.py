import os
import tempfile
import uuid
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import UnstructuredURLLoader


def _get_temp_file(file_content):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_content)
        temp_file.flush()

        return temp_file.name


async def pdf_loader(files):
    documents = []

    for file in files:
        file_path = _get_temp_file(await file.read())
        loader = PyPDFLoader(file_path)
        file_docs = loader.load()
        document_key = str(uuid.uuid4())

        for doc in file_docs:
            doc.metadata["document_type"] = "pdf"
            doc.metadata["source"] = file.filename
            doc.metadata["document_key"] = document_key

        documents += file_docs

        os.remove(file_path)

    return documents


async def text_loader(files):
    docs = []
    for file in files:
        file_content = await file.read()
        text = file_content.decode("utf-8")
        document_key = str(uuid.uuid4())

        metadata = {
            "document_type": "text",
            "source": file.filename,
            "document_key": document_key,
        }

        docs.append({"text": text, "metadata": metadata})

    return docs


async def url_loader(urls):
    loader = UnstructuredURLLoader(urls)
    docs = loader.load()
    document_key = str(uuid.uuid4())

    for doc in docs:
        doc.metadata["document_type"] = "webpage"
        doc.metadata["document_key"] = document_key

    return docs


async def email_loader(emails):
    docs = []
    for email in emails:
        text = f"Date: {email.sent_time.strftime('%m-%d-%Y')}\nSender: {email.sender}\nSubject: {email.subject}\nBody: {email.body}"
        metadata = {
            "source": email.id,
            "document_type": "email",
            "timestamp": email.sent_time.isoformat(),
            "author": email.sender,
            "title": email.subject,
        }

        docs.append({"text": text, "metadata": metadata})

    return docs
