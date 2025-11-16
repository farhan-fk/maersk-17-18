# =========================================
# Maersk Customer Support Agent
# =========================================
# Educational Assignment: Tool Calling Demo
# 
# This agent demonstrates:
# 1. Custom tools (order lookup, tracking)
# 2. Built-in tools (file_search for FAQ)
# 3. LLM's intelligent tool selection
# =========================================

from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
import json
import time
from agent_observability import create_observer

load_dotenv()
client = OpenAI()

# Initialize observability tracker
observer = None  # Will be initialized after setup

# =========================================
# DATA SETUP
# =========================================

# Load order data
ORDERS_CSV = Path("orders_data.csv")
orders_df = pd.read_csv(ORDERS_CSV)

# Setup FAQ knowledge base (RAG)
FAQ_FILE = Path("maersk_faq.txt")
vector_store_id = None  # Will be initialized on first run


def setup_faq_knowledge_base():
    """Create vector store and upload FAQ document"""
    global vector_store_id
    
    print("📚 Setting up FAQ knowledge base...")
    
    # Create vector store
    try:
        vector_store = client.beta.vector_stores.create(
            name="maersk_faq_kb"
        )
    except AttributeError:
        vector_store = client.vector_stores.create(
            name="maersk_faq_kb"
        )
    
    vector_store_id = vector_store.id
    
    # Upload FAQ document
    with FAQ_FILE.open("rb") as f:
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
    
    print(f"✅ Knowledge base ready! Vector store ID: {vector_store_id}\n")
    return vector_store_id


# =========================================
# TOOL DEFINITIONS
# =========================================

tools = [
    {
        "type": "function",
        "name": "check_order_status",
        "description": "Look up detailed information about a customer's order using their order ID. Use this when customer asks about order status, delivery date, or order details. Order IDs follow format: ORD-XXXX",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID provided by the customer (e.g., ORD-1001)",
                },
            },
            "required": ["order_id"],
        },
    },
    {
        "type": "function",
        "name": "get_tracking_info",
        "description": "Track a shipment using the container number. Use this when customer provides a container/tracking number or asks to track their shipment. Container numbers follow format: MAEU + 7 digits (e.g., MAEU7654321)",
        "parameters": {
            "type": "object",
            "properties": {
                "container_number": {
                    "type": "string",
                    "description": "The container number to track (e.g., MAEU7654321)",
                },
            },
            "required": ["container_number"],
        },
    },
]


# =========================================
# TOOL IMPLEMENTATIONS
# =========================================

def check_order_status(order_id: str) -> dict:
    """Look up order information from CSV database"""
    
    # Search for order
    order = orders_df[orders_df['order_id'] == order_id]
    
    if order.empty:
        return {
            "found": False,
            "message": f"Order {order_id} not found in our system. Please verify the order ID."
        }
    
    # Return order details
    order_data = order.iloc[0].to_dict()
    return {
        "found": True,
        "order_id": order_data['order_id'],
        "customer_name": order_data['customer_name'],
        "container_number": order_data['container_number'],
        "status": order_data['status'],
        "origin_port": order_data['origin_port'],
        "destination_port": order_data['destination_port'],
        "shipped_date": order_data['shipped_date'],
        "estimated_delivery": order_data['estimated_delivery']
    }


def get_tracking_info(container_number: str) -> dict:
    """Track shipment by container number"""
    
    # Search by container number
    shipment = orders_df[orders_df['container_number'] == container_number]
    
    if shipment.empty:
        return {
            "found": False,
            "message": f"Container {container_number} not found. Please verify the container number."
        }
    
    # Return tracking details
    tracking_data = shipment.iloc[0].to_dict()
    return {
        "found": True,
        "container_number": tracking_data['container_number'],
        "order_id": tracking_data['order_id'],
        "status": tracking_data['status'],
        "current_location": f"En route from {tracking_data['origin_port']} to {tracking_data['destination_port']}",
        "origin_port": tracking_data['origin_port'],
        "destination_port": tracking_data['destination_port'],
        "shipped_date": tracking_data['shipped_date'],
        "estimated_delivery": tracking_data['estimated_delivery']
    }


# =========================================
# TOOL DISPATCHER
# =========================================

def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute the requested tool and return results"""
    
    if tool_name == "check_order_status":
        return check_order_status(arguments["order_id"])
    elif tool_name == "get_tracking_info":
        return get_tracking_info(arguments["container_number"])
    else:
        return {"error": f"Unknown tool: {tool_name}"}


# =========================================
# AGENT ORCHESTRATION (TWO-CALL PATTERN)
# =========================================

def run_support_agent(user_question: str, show_details: bool = True, expected_tool: str = None):
    """
    Main agent function - handles tool calling with two-call pattern
    
    Call #1: Let LLM decide which tool to use
    Call #2: Generate final natural language response
    
    Args:
        user_question: The user's question
        show_details: Whether to print detailed logs
        expected_tool: Expected tool for accuracy tracking (optional)
    """
    
    # Start timing
    start_time = time.time()
    
    # Initialize conversation
    input_list = [
        {"role": "user", "content": user_question}
    ]
    
    print(f"\n{'='*70}")
    print(f"❓ USER QUESTION: {user_question}")
    print(f"{'='*70}\n")
    
    # Track which tool was actually selected
    tool_selected = None
    tool_args = None
    tool_result = None
    success = True
    error_msg = None
    
    # --- CALL #1: Model decides which tool to use ---
    # Combine custom tools + RAG tool
    all_tools = tools + [{
        "type": "file_search",
        "vector_store_ids": [vector_store_id]
    }]
    
    if show_details:
        print(f"🔧 Available tools: {len(all_tools)}")
        print(f"   - check_order_status (custom)")
        print(f"   - get_tracking_info (custom)")
        print(f"   - file_search (RAG)\n")
    
    resp1 = client.responses.create(
        model="gpt-4o-mini",
        tools=all_tools,
        input=input_list,
        instructions="""You are a helpful Maersk customer support agent.

Tool Selection Rules:
- If user provides ORDER ID (ORD-XXXX), use check_order_status
- If user provides CONTAINER NUMBER (MAEU + digits), use get_tracking_info
- If user asks general questions about policies, shipping, payments, etc., use file_search
- Be precise in tool selection based on the question type
"""
    )
    
    # Check which tool was called
    tool_calls = [item for item in resp1.output if hasattr(item, 'type') and item.type == "function_call"]
    
    if not tool_calls:
        # No custom tool called - likely used file_search or answered directly
        tool_selected = "file_search"  # Assume file_search for FAQ questions
        
        if show_details:
            print("🔍 TOOL SELECTED: file_search (RAG)")
            print("📚 Searched FAQ knowledge base\n")
        
        response_time = time.time() - start_time
        
        # Log to observer
        if observer:
            observer.log_interaction(
                user_question=user_question,
                tool_selected=tool_selected,
                expected_tool=expected_tool,
                response_time=response_time,
                success=True,
                response_text=resp1.output_text
            )
        
        print(f"\n💬 AGENT RESPONSE:\n{resp1.output_text}\n")
        return resp1.output_text
    
    # --- Execute custom tool calls ---
    for call in tool_calls:
        tool_name = call.name
        args = json.loads(call.arguments)
        
        # Track tool selection
        tool_selected = tool_name
        tool_args = args
        
        if show_details:
            print(f"🔧 TOOL SELECTED: {tool_name}")
            print(f"📋 ARGUMENTS: {json.dumps(args, indent=2)}")
        
        # Append function call to conversation
        input_list.append({
            "type": "function_call",
            "call_id": call.call_id,
            "name": tool_name,
            "arguments": call.arguments
        })
        
        # Execute the tool
        try:
            result = execute_tool(tool_name, args)
            tool_result = result
            
            # Check if tool execution was successful
            if isinstance(result, dict) and result.get("found") == False:
                success = False
                error_msg = result.get("message", "Tool returned no results")
            
        except Exception as e:
            success = False
            error_msg = str(e)
            result = {"error": str(e)}
            tool_result = result
        
        if show_details:
            print(f"✅ TOOL RESULT: {json.dumps(result, indent=2)}\n")
        
        # Append tool result to conversation
        input_list.append({
            "type": "function_call_output",
            "call_id": call.call_id,
            "output": json.dumps(result)
        })
    
    # --- CALL #2: Generate final natural language response ---
    resp2 = client.responses.create(
        model="gpt-4o-mini",
        tool_choice="none",  # No more tool calls
        input=input_list,
        instructions="Provide a helpful, natural response based on the tool results. Be friendly and professional."
    )
    
    # Calculate total response time
    response_time = time.time() - start_time
    
    # Log to observer
    if observer:
        observer.log_interaction(
            user_question=user_question,
            tool_selected=tool_selected,
            expected_tool=expected_tool,
            response_time=response_time,
            success=success,
            response_text=resp2.output_text,
            tool_args=tool_args,
            tool_result=tool_result,
            error=error_msg
        )
    
    print(f"💬 AGENT RESPONSE:\n{resp2.output_text}\n")
    return resp2.output_text


# =========================================
# TEST SCENARIOS
# =========================================

def run_test_scenarios():
    """Run predefined test cases to demonstrate tool routing"""
    
    print("\n" + "="*70)
    print("🧪 RUNNING TEST SCENARIOS - Tool Selection Intelligence Test")
    print("="*70)
    
    test_cases = [
        # Should use check_order_status
        ("What's the status of my order ORD-1005?", "check_order_status"),
        
        # Should use get_tracking_info
        ("Can you track container MAEU7654321?", "get_tracking_info"),
        
        # Should use file_search
        ("What is your return policy?", "file_search"),
        
        # Should use file_search
        ("Do you ship dangerous goods?", "file_search"),
        
        # Should use check_order_status
        ("When will order ORD-1010 be delivered?", "check_order_status"),
        
        # Should use file_search
        ("What documents do I need for international shipping?", "file_search"),
    ]
    
    print("\n📊 TOOL ROUTING TEST RESULTS:\n")
    
    for i, (question, expected_tool) in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Question: {question}")
        print(f"Expected Tool: {expected_tool}")
        
        # Run the agent with expected tool for accuracy tracking
        run_support_agent(question, show_details=False, expected_tool=expected_tool)
        
        input("Press Enter for next test case...")
    
    print("\n" + "="*70)
    print("✅ All test scenarios completed!")
    print("="*70)
    
    # Show performance metrics
    if observer:
        observer.print_session_summary()
        observer.print_tool_accuracy_report()
        observer.print_confusion_matrix()


# =========================================
# INTERACTIVE MODE
# =========================================

def interactive_mode():
    """Interactive chat mode for manual testing"""
    
    print("\n" + "="*70)
    print("💬 INTERACTIVE CUSTOMER SUPPORT MODE")
    print("="*70)
    print("\nCommands:")
    print("  - Type your question to chat with the agent")
    print("  - Type 'test' to run all test scenarios")
    print("  - Type 'stats' to see performance statistics")
    print("  - Type 'export' to export logs to CSV")
    print("  - Type 'exit' to quit\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['exit', 'quit']:
            print("\n👋 Thank you for using Maersk Customer Support!\n")
            break
        
        if user_input.lower() == 'test':
            run_test_scenarios()
            continue
        
        if user_input.lower() == 'stats':
            if observer:
                observer.print_session_summary()
                observer.print_tool_accuracy_report()
                observer.print_failed_interactions()
            else:
                print("⚠️ Observer not initialized\n")
            continue
        
        if user_input.lower() == 'export':
            if observer:
                observer.export_to_csv("agent_performance.csv")
            else:
                print("⚠️ Observer not initialized\n")
            continue
        
        # Process question
        run_support_agent(user_input, show_details=True)


# =========================================
# MAIN
# =========================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚢 MAERSK CUSTOMER SUPPORT AGENT")
    print("="*70)
    print("\nThis demo shows intelligent tool calling:")
    print("  📦 Custom Tools: Order lookup, Container tracking")
    print("  🔍 Built-in Tool: FAQ search (RAG with file_search)")
    print("  📊 Observability: Performance tracking & metrics")
    print("="*70)
    
    # Setup knowledge base
    vector_store_id = setup_faq_knowledge_base()
    
    # Initialize observer
    observer = create_observer(log_file="agent_logs.jsonl")
    print("📊 Observability initialized - tracking all interactions\n")
    
    # Start interactive mode
    interactive_mode()
