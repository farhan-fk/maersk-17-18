# 🚢 Maersk Customer Support Agent - Tool Calling Assignment

## 📚 Learning Objectives

This assignment demonstrates **intelligent tool calling** with OpenAI's API, showing how an LLM can:
1. **Choose the right tool** for different types of questions
2. **Execute custom functions** (order lookup, tracking)
3. **Use built-in tools** (RAG/file_search for FAQ)
4. **Combine results** into natural language responses

---

## 🎯 What You'll Learn

### 1. **Custom Tool Calling**
- Define tool schemas using JSON
- Implement Python functions that tools execute
- Handle tool arguments and return structured data

### 2. **Two-Call Pattern**
- **Call #1**: LLM decides which tool to use
- **Execute**: Your code runs the tool function
- **Call #2**: LLM generates natural language response

### 3. **Hybrid Tool Architecture**
- **Custom tools**: `check_order_status()`, `get_tracking_info()`
- **Built-in tools**: `file_search` for RAG-based FAQ

### 4. **Tool Routing Intelligence**
- How tool descriptions guide LLM decisions
- Testing tool selection accuracy
- Handling ambiguous queries

---

## 📁 Project Structure

```
Agent_Assignment/
├── customer_support_agent.py   # Main agent code
├── orders_data.csv             # Order database (15 sample orders)
├── maersk_faq.txt             # Knowledge base (policies, FAQ)
└── README.md                   # This file
```

---

## 🚀 Setup Instructions

### 1. **Install Dependencies**
```bash
pip install openai python-dotenv pandas
```

### 2. **Set OpenAI API Key**
Create `.env` file in `Agent_Assignment/` folder:
```
OPENAI_API_KEY=your_api_key_here
```

### 3. **Run the Agent**
```bash
cd Agent_Assignment
python customer_support_agent.py
```

---

## 🎮 How to Use

### **Interactive Mode**
Ask questions like a customer would:
```
You: What's the status of order ORD-1005?
You: Track container MAEU7654321
You: What is your return policy?
You: Do you accept dangerous goods?
```

### **Test Mode**
Type `test` to run all predefined scenarios and see tool routing in action.

### **Watch for Tool Selection**
The agent shows which tool it selected:
```
🔧 TOOL SELECTED: check_order_status
📋 ARGUMENTS: {"order_id": "ORD-1005"}
✅ TOOL RESULT: {...}
```

---

## 🧪 Test Scenarios Explained

| Question | Expected Tool | Why? |
|----------|---------------|------|
| "Status of order ORD-1005?" | `check_order_status` | Contains order ID format |
| "Track MAEU7654321" | `get_tracking_info` | Contains container number |
| "What's your return policy?" | `file_search` | General policy question |
| "Ship dangerous goods?" | `file_search` | FAQ about regulations |

---

## 🔍 How It Works

### **Step 1: User asks a question**
```python
user_question = "What's the status of order ORD-1005?"
```

### **Step 2: First API Call (Tool Selection)**
```python
resp1 = client.responses.create(
    model="gpt-4o-mini",
    tools=tools,  # All available tools
    input=[{"role": "user", "content": user_question}]
)
```

LLM decides: "This question contains an order ID, I should use `check_order_status`"

### **Step 3: Execute the Tool**
```python
result = check_order_status("ORD-1005")
# Returns: {"found": True, "status": "Processing", ...}
```

### **Step 4: Second API Call (Generate Response)**
```python
resp2 = client.responses.create(
    model="gpt-4o-mini",
    tool_choice="none",  # No more tools
    input=conversation_with_tool_result
)
```

LLM generates: "Your order ORD-1005 is currently Processing and will be delivered by Dec 8th..."

---

## 🛠️ Tool Definitions

### **Tool 1: check_order_status**
```python
{
    "name": "check_order_status",
    "description": "Look up order details by order ID",
    "parameters": {
        "order_id": "string (e.g., ORD-1001)"
    }
}
```

### **Tool 2: get_tracking_info**
```python
{
    "name": "get_tracking_info",
    "description": "Track shipment by container number",
    "parameters": {
        "container_number": "string (e.g., MAEU7654321)"
    }
}
```

### **Tool 3: file_search (Built-in)**
```python
{
    "type": "file_search",
    "vector_store_ids": [vector_store_id]
}
```
Automatically searches `maersk_faq.txt` for relevant information.

---

## 📊 Data Files

### **orders_data.csv** (15 orders)
```csv
order_id,customer_name,container_number,status,origin_port,destination_port,...
ORD-1001,John Smith,MAEU7654321,Delivered,Shanghai,Los Angeles,...
ORD-1002,Sarah Johnson,MAEU8765432,Shipped,Rotterdam,New York,...
```

### **maersk_faq.txt** (Comprehensive FAQ)
Topics covered:
- Shipping times and routes
- Required documents
- Dangerous goods policy
- Customs regulations
- Payment methods
- Return/cancellation policy
- Container types
- Insurance options

---

## 🧩 Key Concepts

### **Why Two API Calls?**
The LLM cannot execute code directly. It can only:
1. **Recognize** when it needs external data
2. **Request** a function call (structured output)
3. **Process** results you provide

You (the developer) execute the actual function between calls.

### **Tool Description Importance**
Clear descriptions are crucial for tool routing:

✅ **Good**: "Look up order details using order ID (format: ORD-XXXX)"
❌ **Bad**: "Get order info"

The LLM uses descriptions to decide which tool fits the question.

### **Hybrid Tool Architecture**
- **Custom tools**: Your Python functions for business logic
- **Built-in tools**: OpenAI's `file_search`, `web_search`, `code_interpreter`
- **Combination**: Best of both worlds!

---

## 🎓 Extension Ideas

Want to learn more? Try adding:

1. **More Custom Tools**
   - `cancel_order(order_id, reason)`
   - `update_delivery_address(order_id, new_address)`
   - `request_invoice(order_id)`

2. **Better Error Handling**
   - Fuzzy matching for order IDs (ORD-1005 vs ord-1005)
   - "Did you mean?" suggestions
   - Validation before tool execution

3. **Multi-Step Workflows**
   - Verify customer identity before showing order details
   - Require confirmation before cancellations
   - Track conversation context

4. **Analytics Dashboard**
   - Log which tools are used most
   - Track tool selection accuracy
   - Monitor response times

---

## 🐛 Troubleshooting

### **"Vector store not found"**
Make sure `maersk_faq.txt` exists in the same folder. The agent creates the vector store on first run.

### **"Order not found"**
Check `orders_data.csv` for valid order IDs. Format must be: `ORD-1001` to `ORD-1015`

### **"Tool not called"**
The LLM might answer directly if it doesn't need external data. Try questions that require database lookup.

### **"Wrong tool selected"**
Improve tool descriptions to be more specific about when to use each tool.

---

## 📖 Additional Resources

- [OpenAI Function Calling Docs](https://platform.openai.com/docs/guides/function-calling)
- [Tool Use Best Practices](https://platform.openai.com/docs/guides/function-calling/best-practices)
- [RAG with file_search](https://platform.openai.com/docs/assistants/tools/file-search)

---

## 💡 Key Takeaways

1. **Tool calling extends LLM capabilities** beyond text generation
2. **Clear tool descriptions** are critical for accurate routing
3. **Two-call pattern** separates tool selection from response generation
4. **Hybrid architecture** (custom + built-in tools) is powerful
5. **Testing tool routing** ensures reliability in production

---

## 🎉 Success Criteria

You've mastered this assignment when you can:
- ✅ Explain why two API calls are needed
- ✅ Write clear tool descriptions that guide LLM selection
- ✅ Implement custom tool functions that return structured data
- ✅ Combine custom tools with built-in tools (file_search)
- ✅ Test and debug tool routing decisions

---

**Happy Learning! 🚀**

*Questions? Review the code comments in `customer_support_agent.py` for detailed explanations.*
