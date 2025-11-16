# 🎓 Assignment: Add a New Tool to the Agent

## 📚 Learning Objective
Practice extending the customer support agent by implementing a **new custom tool** from scratch. You'll learn how to define tool schemas, implement functions, and integrate them into the agent workflow.

---

## 🎯 Your Mission: Add `cancel_order` Tool

Implement a new tool that allows customers to request order cancellation with the following business rules:

### **Business Rules:**
1. ✅ **Allow cancellation** if order status is "Processing"
2. ❌ **Reject cancellation** if order is already "Shipped" or "Delivered"
3. 📝 Require a **reason** for cancellation (optional but recommended)
4. 🔄 Generate a **cancellation request ID** (format: CR-XXXXXXXX)
5. 📊 Track cancellation requests in a log file

---

## 📝 Step-by-Step Guide

### **Step 1: Define the Tool Schema**

Add this tool definition to the `tools` array (around line 78):

```python
{
    "type": "function",
    "name": "cancel_order",
    "description": "Request cancellation of an order. Use this when customer wants to cancel their order. Only works for orders in 'Processing' status.",
    "parameters": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The order ID to cancel (e.g., ORD-1001)",
            },
            "reason": {
                "type": "string",
                "description": "Reason for cancellation (optional but helpful)",
            },
        },
        "required": ["order_id"],
    },
},
```

**📍 Where to add:** In the `tools = [...]` list after `get_tracking_info` definition.

**💡 Tip:** Make sure to add a comma after the previous tool definition!

---

### **Step 2: Implement the Function**

Add this function in the "TOOL IMPLEMENTATIONS" section (around line 120):

```python
def cancel_order(order_id: str, reason: str = None) -> dict:
    """
    Request order cancellation with business rule validation
    
    Args:
        order_id: The order ID to cancel
        reason: Optional cancellation reason
    
    Returns:
        dict with cancellation result and request ID
    """
    
    # TODO 1: Look up the order in orders_df
    # Hint: Use orders_df[orders_df['order_id'] == order_id]
    order = orders_df[orders_df['order_id'] == order_id]
    
    # TODO 2: Check if order exists
    if order.empty:
        return {
            "success": False,
            "message": f"Order {order_id} not found. Please verify the order ID."
        }
    
    # TODO 3: Get order status
    order_status = order.iloc[0]['status']
    
    # TODO 4: Apply business rules
    if order_status == "Processing":
        # Generate cancellation request ID
        import uuid
        request_id = f"CR-{uuid.uuid4().hex[:8].upper()}"
        
        # Log cancellation request
        cancellation_log = {
            "request_id": request_id,
            "order_id": order_id,
            "reason": reason or "No reason provided",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "original_status": order_status
        }
        
        # Save to log file (append mode)
        log_file = Path("cancellation_requests.jsonl")
        with log_file.open("a") as f:
            f.write(json.dumps(cancellation_log) + "\n")
        
        return {
            "success": True,
            "request_id": request_id,
            "message": f"Cancellation request created successfully. Request ID: {request_id}",
            "order_id": order_id,
            "original_status": order_status
        }
    
    elif order_status in ["Shipped", "Delivered"]:
        return {
            "success": False,
            "message": f"Cannot cancel order - it is already {order_status}. Please contact support for returns.",
            "order_status": order_status
        }
    
    else:  # Cancelled or other status
        return {
            "success": False,
            "message": f"Order is currently {order_status} and cannot be cancelled.",
            "order_status": order_status
        }
```

**📍 Where to add:** After `get_tracking_info()` function, before the "TOOL DISPATCHER" section.

---

### **Step 3: Update the Tool Dispatcher**

Modify the `execute_tool()` function (around line 190):

```python
def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute the requested tool and return results"""
    
    if tool_name == "check_order_status":
        return check_order_status(arguments["order_id"])
    elif tool_name == "get_tracking_info":
        return get_tracking_info(arguments["container_number"])
    elif tool_name == "cancel_order":
        # TODO 5: Add cancel_order handler
        return cancel_order(
            order_id=arguments["order_id"],
            reason=arguments.get("reason")  # reason is optional
        )
    else:
        return {"error": f"Unknown tool: {tool_name}"}
```

**📍 What to change:** Add the `elif` block for `cancel_order` before the `else` statement.

---

### **Step 4: Add Test Cases**

Add test scenarios to the `run_test_scenarios()` function (around line 360):

```python
test_cases = [
    # Existing test cases...
    ("What's the status of my order ORD-1005?", "check_order_status"),
    ("Can you track container MAEU7654321?", "get_tracking_info"),
    ("What is your return policy?", "file_search"),
    ("Do you ship dangerous goods?", "file_search"),
    ("When will order ORD-1010 be delivered?", "check_order_status"),
    ("What documents do I need for international shipping?", "file_search"),
    
    # TODO 6: Add your new test cases here!
    ("I want to cancel order ORD-1003", "cancel_order"),
    ("Cancel my order ORD-1001 because I found a better price", "cancel_order"),
]
```

**📍 What to change:** Add 2 new test cases to the `test_cases` list.

---

### **Step 5: Update the Instructions**

Modify the agent's system instructions (around line 250) to include cancellation guidance:

```python
instructions="""You are a helpful Maersk customer support agent.

Tool Selection Rules:
- If user provides ORDER ID (ORD-XXXX), use check_order_status
- If user provides CONTAINER NUMBER (MAEU + digits), use get_tracking_info
- If user asks general questions about policies, shipping, payments, etc., use file_search
- If user wants to CANCEL an order, use cancel_order
- Be precise in tool selection based on the question type
"""
```

---

## 🧪 Testing Your Implementation

### **Test Scenario 1: Valid Cancellation**
```
You: I want to cancel order ORD-1003
Expected: ✅ Success (status is "Processing")
```

### **Test Scenario 2: Already Shipped**
```
You: Cancel order ORD-1001
Expected: ❌ Rejection (status is "Delivered")
```

### **Test Scenario 3: With Reason**
```
You: Please cancel ORD-1005 because I ordered the wrong item
Expected: ✅ Success with reason logged
```

---

## ✅ Checklist

### **Part 1: Basic Tool Implementation**
- [ ] Tool schema added to `tools` array with correct format
- [ ] `cancel_order()` function implemented with all business rules
- [ ] Tool dispatcher updated to handle `cancel_order`
- [ ] Test cases added to `run_test_scenarios()`
- [ ] Agent instructions updated to mention cancellation
- [ ] Tested with at least 3 different scenarios
- [ ] Cancellation requests logged to `cancellation_requests.jsonl`
- [ ] Observability tracking works (check with `stats` command)

### **Part 2: Conversation Memory (Bonus Challenge 2)**
- [ ] Global `conversation_history` list created
- [ ] `run_support_agent()` appends user messages to history
- [ ] Both API calls use `conversation_history` instead of `input_list`
- [ ] Assistant responses appended to history
- [ ] `reset` command added to clear history
- [ ] Tested follow-up questions work correctly
- [ ] Agent remembers context from previous turns
- [ ] Conversation history visible in debug output

---

## 🎓 Learning Outcomes

By completing this assignment, you'll understand:

### **Core Tool Implementation:**
1. ✅ How to define JSON schemas for tool parameters
2. ✅ Implementing business logic in tool functions
3. ✅ Handling optional parameters in tools
4. ✅ Logging tool actions for audit trails
5. ✅ Integrating new tools into existing agent workflow
6. ✅ Testing tool routing accuracy
7. ✅ Writing clear tool descriptions for LLM guidance

### **Advanced Concepts (with Memory):**
8. ✅ Managing stateful conversations with history
9. ✅ Handling multi-turn interactions
10. ✅ Context preservation across API calls
11. ✅ Implementing session reset functionality
12. ✅ Debugging conversation state

---

## 🚀 Bonus Challenges

### **Challenge 1: Add Validation** ⭐
Prevent duplicate cancellation requests:
- Check if order has already been cancelled
- Search `cancellation_requests.jsonl` for existing requests
- Return helpful message if duplicate found

### **Challenge 2: Add Conversation Memory** ⭐⭐ (RECOMMENDED)
Enable multi-turn conversations with context awareness:

**The Problem:**
```
User: What's the status of order ORD-1005?
Agent: Your order is Processing...

User: Can you cancel it?
Agent: ❌ Which order do you want to cancel? (Lost context!)
```

**Your Task:** Add conversation memory so agent remembers previous interactions.

#### **Step 1: Add Global Conversation History**
At the top of the file (after imports, around line 22):

```python
# Initialize observability tracker
observer = None  # Will be initialized after setup

# ADD THIS: Conversation memory
conversation_history = []

# =========================================
# DATA SETUP
# =========================================
```

#### **Step 2: Modify run_support_agent() Function**
Update the function to use persistent history (around line 210):

```python
def run_support_agent(user_question: str, show_details: bool = True, expected_tool: str = None):
    """
    Main agent function - handles tool calling with two-call pattern
    """
    
    # Start timing
    start_time = time.time()
    
    # ADD THIS: Append user question to conversation history
    conversation_history.append({
        "role": "user",
        "content": user_question
    })
    
    # CHANGE THIS: Use conversation_history instead of input_list
    # OLD: input_list = [{"role": "user", "content": user_question}]
    # NEW: Use existing conversation_history
    
    print(f"\n{'='*70}")
    print(f"❓ USER QUESTION: {user_question}")
    if len(conversation_history) > 1:
        print(f"💬 Conversation turns: {len(conversation_history)}")
    print(f"{'='*70}\n")
```

#### **Step 3: Update API Calls to Use History**
Replace `input_list` with `conversation_history` in both API calls:

```python
# CALL #1
resp1 = client.responses.create(
    model="gpt-4o-mini",
    tools=all_tools,
    input=conversation_history,  # Changed from input_list
    instructions="""..."""
)

# When appending tool calls:
conversation_history.append({
    "type": "function_call",
    "call_id": call.call_id,
    "name": tool_name,
    "arguments": call.arguments
})

# When appending tool results:
conversation_history.append({
    "type": "function_call_output",
    "call_id": call.call_id,
    "output": json.dumps(result)
})

# CALL #2
resp2 = client.responses.create(
    model="gpt-4o-mini",
    tool_choice="none",
    input=conversation_history,  # Changed from input_list
    instructions="..."
)

# ADD THIS: Append assistant response to history
conversation_history.append({
    "role": "assistant",
    "content": resp2.output_text
})
```

#### **Step 4: Add Reset Command**
In `interactive_mode()` function, add a reset option:

```python
print("\nCommands:")
print("  - Type your question to chat with the agent")
print("  - Type 'test' to run all test scenarios")
print("  - Type 'stats' to see performance statistics")
print("  - Type 'export' to export logs to CSV")
print("  - Type 'reset' to clear conversation history")  # NEW
print("  - Type 'exit' to quit\n")

# Inside the while loop, add:
if user_input.lower() == 'reset':
    conversation_history.clear()
    print("\n🔄 Conversation history cleared!\n")
    continue
```

#### **Test Your Memory Implementation:**

```
You: What's the status of order ORD-1005?
Agent: Your order is Processing, arriving Dec 8th...

You: Can you cancel it?
Agent: ✅ I'll cancel order ORD-1005 for you...
         (Agent remembers the order ID from previous question!)

You: What was my first question?
Agent: ✅ You asked about the status of order ORD-1005.
         (Agent has full conversation context!)
```

#### **Expected Behavior:**
- ✅ Agent remembers previous questions and answers
- ✅ Follow-up questions work naturally
- ✅ Context preserved across multiple turns
- ✅ Can reference earlier parts of conversation
- ✅ Type 'reset' to start fresh conversation

#### **Debugging Tips:**
```python
# Add this to see conversation history:
if show_details:
    print(f"📚 Conversation History Length: {len(conversation_history)}")
    print(f"   Messages: {len([m for m in conversation_history if m.get('role') == 'user'])} user, "
          f"{len([m for m in conversation_history if m.get('role') == 'assistant'])} assistant")
```

---

### **Challenge 3: Add Email Notification** ⭐⭐
Simulate sending confirmation email:
- Extract customer email from `orders_df`
- Log simulated email to `email_log.jsonl`
- Include cancellation details in email body

### **Challenge 4: Add Cancellation Policy Check** ⭐⭐⭐
Check if order is within cancellation window:
- Parse `shipped_date` from order data
- Only allow cancellation within 24 hours of order placement
- Return policy-based rejection if too late

### **Challenge 5: Add Partial Cancellation** ⭐⭐⭐⭐
Allow cancelling specific items from multi-item orders:
- Add `item_name` parameter (optional)
- Support cancelling individual items
- Update order total calculation

---

## 🐛 Common Mistakes to Avoid

### **Mistake 1: Missing Comma in tools Array**
```python
# ❌ Wrong - missing comma
},
{
    "type": "function",
```

```python
# ✅ Correct
},  # <- comma here!
{
    "type": "function",
```

### **Mistake 2: Wrong Parameter Handling**
```python
# ❌ Wrong - will crash if reason not provided
def cancel_order(order_id: str, reason: str):
    return f"Reason: {reason}"
```

```python
# ✅ Correct - handle optional parameter
def cancel_order(order_id: str, reason: str = None):
    return f"Reason: {reason or 'No reason provided'}"
```

### **Mistake 3: Forgetting to Update Dispatcher**
```python
# ❌ Won't work - tool not routed
def execute_tool(tool_name, arguments):
    if tool_name == "check_order_status":
        return check_order_status(...)
    # cancel_order not handled!
```

### **Mistake 4: Unclear Tool Description**
```python
# ❌ Too vague
"description": "Cancel an order"

# ✅ Clear and specific
"description": "Request cancellation of an order. Use this when customer wants to cancel their order. Only works for orders in 'Processing' status."
```

---

## 📊 Expected Output

When you run the agent and test cancellation:

```
======================================================================
❓ USER QUESTION: I want to cancel order ORD-1003
======================================================================

🔧 Available tools: 4
   - check_order_status (custom)
   - get_tracking_info (custom)
   - cancel_order (custom)
   - file_search (RAG)

🔧 TOOL SELECTED: cancel_order
📋 ARGUMENTS: {
  "order_id": "ORD-1003",
  "reason": "Customer requested cancellation"
}
✅ TOOL RESULT: {
  "success": true,
  "request_id": "CR-A7B3C8D2",
  "message": "Cancellation request created successfully...",
  "order_id": "ORD-1003",
  "original_status": "Processing"
}

💬 AGENT RESPONSE:
Your cancellation request has been submitted successfully! 

Cancellation Request ID: CR-A7B3C8D2
Order ID: ORD-1003

Your order was in Processing status and has been flagged for cancellation. 
Our operations team will process this within 2-4 hours and you'll receive 
a confirmation email once complete.
```

---

## 🎉 Submission

Once complete, demonstrate your implementation by:

1. Running `python customer_support_agent.py`
2. Type `test` to run all test scenarios
3. Show that cancellation tool is selected correctly
4. Type `stats` to show tool accuracy includes cancel_order
5. Share your `cancellation_requests.jsonl` log file

**Congratulations!** 🎊 You've successfully extended an AI agent with custom business logic!

---

## 📚 Additional Resources

- [OpenAI Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [JSON Schema Specification](https://json-schema.org/)
- Python `uuid` module documentation
- Pandas DataFrame filtering

---

**Need Help?** Review the existing `check_order_status` implementation as a reference. It follows the same pattern! 🚀
