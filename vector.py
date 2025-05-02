from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma
import os 
import pandas as pd
import sys
from langchain_ollama.llms import OllamaLLM
import re

def load_best_practices_from_txt(filepath):
    with open(filepath, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

best_practices_list = []

def get_data_filename(subject, content):
    subject_part = re.sub(r'\W+', '', subject.replace(' ', '_'))
    content_first_word = re.sub(r'\W+', '', content.split()[0]) if content.split() else 'content'
    folder = os.path.join('games_input', subject_part)
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"{subject_part}_{content_first_word}.lua")

subject = None
content = None
filename = None

def ensure_data_file():
    global subject, content, filename
    try:
        has_data = input("Do you have a data file to provide? (y/n): ").strip().lower()
        if has_data == 'y':
            filename = input("Enter the data file name (with .txt extension): ").strip()
            try:
                with open(filename, 'r') as f:
                    lines = [line.strip() for line in f if line.strip()]
                if lines:
                    df = pd.DataFrame({'text': lines})
                    data_source = 'txt'
                else:
                    df = pd.DataFrame()
                    data_source = None
            except FileNotFoundError:
                print(f"File '{filename}' not found. Proceeding to create a new file.")
                has_data = 'n'
        if has_data != 'y':
            subject = input("Enter the educational subject you want to focus on (e.g., mathematics, science, history, language arts): ").strip()
            content = input("Enter the specific educational content or concept to teach (e.g., multiplication tables, solar system, ancient Egypt, grammar rules): ").strip()
            filename = get_data_filename(subject, content)
            try:
                with open(filename, 'r') as f:
                    lines = [line.strip() for line in f if line.strip()]
                if lines:
                    df = pd.DataFrame({'text': lines})
                    data_source = 'txt'
                else:
                    df = pd.DataFrame()
                    data_source = None
            except FileNotFoundError:
                print(f"Warning: '{filename}' not found.")
                user_choice = input(f"No data file found. Would you like to bootstrap '{filename}' with your subject and content? (y/n): ").strip().lower()
                if user_choice == 'y':
                    with open(filename, "w") as f:
                        f.write(f"Best practices for teaching {subject} - {content} in Roblox.\n")
                    print(f"'{filename}' created with subject: {subject} and content: {content}")
                    df = pd.DataFrame({'text': [f"Best practices for teaching {subject} - {content} in Roblox."]})
                    data_source = 'txt'
                else:
                    print("No data source available. Best practices will not be used.")
                    df = pd.DataFrame()
                    data_source = None
                # Save the LLM-generated Lua script to the new filename after main.py produces it
                # (This will be called from main.py after the script is generated)
                global save_lua_script_filename
                save_lua_script_filename = filename
        return df, data_source, filename
    except Exception as e:
        print(f"Error during data file setup: {e}")
        return pd.DataFrame(), None, None

# Main data file setup
if __name__ == '__main__' or True:
    df, data_source, filename = ensure_data_file()
else:
    df = pd.DataFrame()
    data_source = None
    filename = None

embeddings = OllamaEmbeddings(model="mxbai-embed-large")

db_location = "./chrome_langchain_db"
add_documents = not os.path.exists(db_location)

ids = []
documents = []

if data_source == 'txt' and not df.empty:
    if add_documents:
        for i, row in df.iterrows():
            text = str(row["text"]).strip()
            if text:  # Only add non-empty lines
                document = Document(
                    page_content=text,
                    metadata={"source": filename},
                    id=str(i)
                )
                ids.append(str(i))
                documents.append(document)

    if not documents:
        print(f"No valid data found in {filename}. Cannot create vector store.")
        retriever = None
    else:
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=db_location,
            ids=ids
        )

        if add_documents:
            vector_store.add_documents(documents=documents, ids=ids)
        
        retriever = vector_store.as_retriever(
            search_kwargs={"k": 5}
        )
else:
    retriever = None

def retrieve_best_practices(subject: str, content: str) -> str:
    """
    Retrieve best practices and teaching strategies for the given subject and content.
    Returns a summary or list of tips to guide script generation.
    """
    if retriever is not None:
        query = f"Best practices for teaching {subject} - {content} in an interactive Roblox experience."
        docs = retriever.invoke(query)
        if not docs:
            return "No best practices found for this subject and content."
        return "\n\n".join(doc.page_content for doc in docs)
    elif best_practices_list:
        return "\n\n".join(best_practices_list)
    else:
        return "No data available for best practices. Please ensure a data file is present."

def save_lua_script(filename, lua_script):
    with open(filename, 'w') as f:
        f.write(lua_script)