from dotenv import load_dotenv
import os
import io 
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings,ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma as embedder_Chroma
from langchain_chroma import Chroma as retiever_Chroma
load_dotenv()



GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
embedding_model= GoogleGenerativeAIEmbeddings(model="models/text-embedding-004",google_api_key=GOOGLE_API_KEY)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",api_key=GOOGLE_API_KEY)


current_dir = os.path.dirname(os.path.abspath(__file__))
db_dir = os.path.join(current_dir, "db")
persistent_directory = os.path.join(db_dir, "chroma_db_with_metadata")






def create_chunks(pdf):
    
    book=PdfReader(io.BytesIO(pdf.read()))
    text_content="\n".join([page.extract_text() for page in book.pages if page.extract_text()])
    
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=50) 
    docs = text_splitter.split_text(text_content)
    return docs




def create_embedding(pdf):
    db_ret=retiever_Chroma(persist_directory=persistent_directory,
            embedding_function=embedding_model)
    db_ret.delete_collection()
    chunks=create_chunks(pdf)
    db=embedder_Chroma.from_texts(chunks,embedding=embedding_model,persist_directory=persistent_directory)





def retieve_embedding(query):
    db_ret=retiever_Chroma(persist_directory=persistent_directory,
            embedding_function=embedding_model)
    retriever = db_ret.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 3, "score_threshold": 0.2},
    )
    relevant_docs = retriever.invoke(query)
    return relevant_docs


def create_final_message_state(message):
    last_human_input=message[-1]
    relevant_docs=retieve_embedding(last_human_input['content'])
    combined_input=(
        "Here are some documents that might help answer the question: "
    + last_human_input['content']
    + "\n\nRelevant Documents:\n"
    + "\n\n".join([doc.page_content for doc in relevant_docs])
    
)
    

    # result= llm.invoke(message[:-1]+[{"role":"human","content":combined_input}])
    # return result.content
    stream = llm.stream(message[:-1] + [{"role": "human", "content": combined_input}])
    for chunk in stream:
        yield chunk
