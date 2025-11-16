# =========================================
# RAG Chatbot with Gradio UI
# =========================================
# Beautiful web interface to chat with your documents
# Upload a PDF and ask questions in natural conversation
# =========================================

from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import gradio as gr

load_dotenv()
client = OpenAI()

# Global state to store vector store ID
current_vector_store_id = None


def create_vector_store(name="chatbot_docs"):
    """Step 1: Create a vector store to hold your documents"""
    try:
        vector_store = client.beta.vector_stores.create(name=name)
    except AttributeError:
        vector_store = client.vector_stores.create(name=name)
    
    return vector_store.id


def upload_document(vector_store_id, file_path):
    """Step 2: Upload and index a document into the vector store"""
    with Path(file_path).open("rb") as f:
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


def handle_file_upload(file):
    """Handle document upload and create vector store"""
    global current_vector_store_id
    
    if file is None:
        return "⚠️ Please upload a PDF file first", ""
    
    try:
        # Create vector store
        current_vector_store_id = create_vector_store()
        
        # Upload and index document
        upload_document(current_vector_store_id, file.name)
        
        filename = Path(file.name).name
        success_msg = f"✅ **Document Ready:** {filename}\n\n💬 You can now ask questions about your document!"
        
        return success_msg, ""
    
    except Exception as e:
        return f"❌ **Error:** {str(e)}\n\nPlease check your file and try again.", ""


def chat_with_document(message, history):
    """Handle chat messages and return responses"""
    global current_vector_store_id
    
    if current_vector_store_id is None:
        return "⚠️ Please upload a document first before asking questions."
    
    if not message.strip():
        return ""
    
    try:
        # Get answer from RAG
        answer = ask_question(current_vector_store_id, message)
        return answer
    
    except Exception as e:
        return f"❌ Error: {str(e)}"


def reset_session():
    """Reset the session and clear vector store"""
    global current_vector_store_id
    current_vector_store_id = None
    return "🔄 Session reset. Upload a new document to start.", [], ""


# =========================================
# GRADIO INTERFACE
# =========================================

with gr.Blocks(title="RAG Chatbot", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown(
        """
        # 🤖 Chat with Your Documents
        ### Upload any PDF and have a natural conversation with its content
        
        **How it works:**
        1. Upload a PDF document (resume, report, manual, etc.)
        2. Wait for indexing to complete
        3. Ask questions in natural language
        4. Get accurate answers based on document content
        """
    )
    
    with gr.Row():
        # Left Column: Document Upload
        with gr.Column(scale=1):
            gr.Markdown("### 📁 Document Upload")
            
            file_upload = gr.File(
                label="",
                file_types=[".pdf"],
                type="filepath"
            )
            
            upload_btn = gr.Button(
                "📤 Upload & Index Document",
                variant="primary",
                size="lg"
            )
            
            upload_status = gr.Markdown(
                """
                **Status:** Waiting for document...
                
                📋 Supported format: PDF
                """,
                elem_classes="status-box"
            )
            
            gr.Markdown("---")
            
            reset_btn = gr.Button(
                "🔄 Reset Session",
                variant="secondary",
                size="sm"
            )
        
        # Right Column: Chat Interface
        with gr.Column(scale=2):
            gr.Markdown("### 💬 Chat with Document")
            
            chatbot = gr.Chatbot(
                value=[],
                height=400,
                placeholder="Upload a document to start chatting...",
                show_copy_button=True,
                avatar_images=(None, "🤖")
            )
            
            with gr.Row():
                msg_input = gr.Textbox(
                    placeholder="Ask a question about your document...",
                    show_label=False,
                    scale=9,
                    container=False
                )
                
                send_btn = gr.Button(
                    "Send",
                    variant="primary",
                    scale=1
                )
            
            gr.Markdown(
                """
                **💡 Example questions:**
                - What is this document about?
                - Summarize the key points
                - What are the main conclusions?
                - Find information about [specific topic]
                """
            )
    
    # Event Handlers
    upload_btn.click(
        fn=handle_file_upload,
        inputs=[file_upload],
        outputs=[upload_status, msg_input]
    )
    
    # Chat functionality
    msg_input.submit(
        fn=chat_with_document,
        inputs=[msg_input, chatbot],
        outputs=[msg_input]
    ).then(
        fn=lambda msg, hist: hist + [[msg, chat_with_document(msg, hist)]],
        inputs=[msg_input, chatbot],
        outputs=[chatbot]
    ).then(
        fn=lambda: "",
        outputs=[msg_input]
    )
    
    send_btn.click(
        fn=chat_with_document,
        inputs=[msg_input, chatbot],
        outputs=[msg_input]
    ).then(
        fn=lambda msg, hist: hist + [[msg, chat_with_document(msg, hist)]],
        inputs=[msg_input, chatbot],
        outputs=[chatbot]
    ).then(
        fn=lambda: "",
        outputs=[msg_input]
    )
    
    reset_btn.click(
        fn=reset_session,
        outputs=[upload_status, chatbot, msg_input]
    )
    
    # Footer
    gr.Markdown(
        """
        ---
        ### 🔍 How it works:
        - **Vector Store**: Your document is indexed using OpenAI's vector store
        - **RAG (Retrieval Augmented Generation)**: Finds relevant sections before answering
        - **Accurate Responses**: Answers are grounded in your document's actual content
        
        ### 🎯 Perfect for:
        - Analyzing reports and research papers
        - Extracting information from manuals
        - Understanding contracts and legal documents
        - Reviewing resumes and CVs
        - Exploring technical documentation
        
        ### 🧠 Powered by:
        **OpenAI GPT-5-nano** with **file_search** tool for intelligent document retrieval
        """
    )


# Launch the app
if __name__ == "__main__":
    demo.launch(
        share=False,
        server_name="127.0.0.1",
        server_port=7861  # Different port from ATS app
    )