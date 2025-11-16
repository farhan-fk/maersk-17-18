# =========================================
# Simple RAG Demo - OpenAI Vector Store
# =========================================
# Learn how to:
# 1. Create a vector store
# 2. Upload and index a document
# 3. Ask questions using file_search
# =========================================

from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
client = OpenAI()

# Update this path to your document
PDF_PATH = Path(r"C:\Users\ffarh\OneDrive\Desktop\Maersk\SDK_openai\farhan_khan.pdf")


def create_vector_store(name="fk_vector_store"):
    """Step 1: Create a vector store to hold your documents"""
    print(f"\n📦 Creating vector store: {name}")
    
    try:
        vector_store = client.beta.vector_stores.create(name=name)
    except AttributeError:
        vector_store = client.vector_stores.create(name=name)
    
    print(f"✅ Vector store created with ID: {vector_store.id}")
    return vector_store.id


def upload_document(vector_store_id, file_path):
    """Step 2: Upload and index a document into the vector store"""
    print(f"\n📄 Uploading document: {file_path.name}")
    print("⏳ Indexing... (this may take a moment)")
    
    with file_path.open("rb") as f:
        try:
            client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store_id,
                files=[f],
            )
        except AttributeError:
            client.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store_id,
                files=[f],
            )
    
    print("✅ Document indexed successfully!")


def ask_question(vector_store_id, question):
    """Step 3: Ask a question about the document using RAG"""
    response = client.responses.create(
        model="gpt-5-nano",
        input=question,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store_id]
        }],
    )
    return response.output_text


# =========================================
# MAIN DEMO
# =========================================

print("\n" + "="*60)
print("🔍 SIMPLE RAG DEMO - OpenAI Vector Store")
print("="*60)

# Step 1: Create vector store
vector_store_id = create_vector_store("demo_docs")

# Step 2: Upload document
upload_document(vector_store_id, PDF_PATH)

# Step 3: Interactive Q&A
print("\n" + "="*60)
print("💬 Ask questions about your document")
print("="*60)
print("Type 'exit' to quit\n")

while True:
    user_question = input("You: ").strip()
    
    if user_question.lower() in ("exit", "quit"):
        print("\n👋 Goodbye!")
        break
    
    if not user_question:
        continue
    
    print("\n🤖 AI: ", end="", flush=True)
    answer = ask_question(vector_store_id, user_question)
    print(answer)
    print()