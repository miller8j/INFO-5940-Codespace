import streamlit as st
import os
from openai import OpenAI
# 
from io import BytesIO
from os import environ
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

client = OpenAI(
    api_key=os.environ["API_KEY"],
    base_url="https://api.ai.it.cornell.edu",
)


st.title("📝 File Q&A with OpenAI")
# allow multiple files (PDF, text, markdown) (https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader)
uploaded_files = st.file_uploader("Upload article(s)", type=("pdf", "txt", "md"), accept_multiple_files=True)

# Disable the chat input if there are no uploaded files
has_files = bool(uploaded_files)
question = st.chat_input(
    "Ask something about the uploaded article(s)",
    disabled=not has_files,
)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask something about the article"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

def get_file_text(uploaded_file):
    """
    Parameters: 
        uploaded_file (pdf, txt, or md): the file object we are reading

    Returns: 
        the text of the file as a string (empty string on failure).
    """
    content_type = uploaded_file.type
    print(content_type)
    # PDF handling
    if content_type == "application/pdf":
        # pypdf is used to read a PDF (https://www.geeksforgeeks.org/python/working-with-pdf-files-in-python/)
        from pypdf import PdfReader

        reader = PdfReader(uploaded_file)
        pdf_as_str = ""

        # get the text from each page
        for page in reader.pages:
            # format it so that each page is separated by two newlines
            pdf_as_str += page.extract_text() + "\n\n"
        
        return pdf_as_str
        
    # txt/md files decode as utf-8
    else:
        return uploaded_file.read().decode("utf-8")


from langchain_core.documents import Document
from typing_extensions import List, TypedDict

from langchain_core.prompts import PromptTemplate

# from the notebook
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str

# from the notebook
def format_docs(docs):
    return "\n\n".join(f"{doc.page_content} source: [[{doc.metadata.get('source', 'unknown source')}]]" for doc in docs)
      
if question and has_files:
    # always format uploaded_files as a list
    if not isinstance(uploaded_files, list):
        files = [uploaded_files]
    else:
        files = uploaded_files


    all_chunks = []
    for f in files:
        text = get_file_text(f)
        # used this post to get the name of the uploaded file (https://docs.streamlit.io/knowledge-base/using-streamlit/retrieve-filename-uploaded)
        filename = f.name
        # split each file into chunks (just using what we do in the notebook)
        splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=0)
        chunks = splitter.split_documents([Document(text)])
        for chunk in chunks:
            chunk.metadata["source" ]= filename
            all_chunks.append(chunk)

    # following notebook to create vectorstore and retriever    
    vectorstore = Chroma.from_documents(documents=all_chunks, embedding=OpenAIEmbeddings(model="openai.text-embedding-3-large"))
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 20})    # Append the user's question to the messages

    # invoking the retriever with the user's question to get the relevant context
    context = format_docs(retriever.invoke(question))

    template = f"""
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
    
    If you don't know the answer, just say that you don't know. 
    
    If the question is not relevant to the given context, just say that you don't know.

    Use four sentences maximum and keep the answer concise.
    
    Question: {question} 
    
    Context: {context} **IMPORTANT: You MUST cite the retrieved context using the file name associated with each source.**
    """

    # append the user's question to the messages
    st.session_state.messages.append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="openai.gpt-4o-mini",  # Change this to a valid model name
            messages=[
                {"role": "system", "content": template}, # system prompt with context
                {"role": "user", "content": question}, # user question
            ],
            stream=True
        )
        response = st.write_stream(stream)

    # Append the assistant's response to the messages
    st.session_state.messages.append({"role": "assistant", "content": response})