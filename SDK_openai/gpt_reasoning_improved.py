from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----- Build an improved, search-optimized prompt -----

today = datetime.now().date()
today_str = today.strftime("%Y-%m-%d")
departure_deadline = (datetime.now() + timedelta(hours=36)).strftime("%Y-%m-%d %H:00")

prompt = f"""
You are a senior global shipping planner for a major container line.

**Current Date:** {today_str}
**Departure Deadline:** {departure_deadline} (36 hours from now)

**Shipment Details:**
- Origin: Nhava Sheva (JNPT), Mumbai, India
- Destination: Rotterdam, Netherlands
- Containers: 250 TEU (each valued at $50,000)
- Total Cargo Value: $12.5 million
- Departure Window: MUST depart within 36 hours

**Your Task:**
Assess schedule and disruption risk for THIS SPECIFIC shipment departing in 36 hours and transiting over the next 7-14 days.

**Web Search Guidelines (CRITICAL):**
Only search for TIME-SENSITIVE, CURRENT information:
✓ Search for: Current disruptions, strikes, closures, alerts (last 7 days + next 14 days forecast)
✓ Include temporal context: "2025", "November 2025", "current", "this week"
✓ Focus on: Operational status RIGHT NOW at JNPT, Red Sea/Suez, Rotterdam

✗ Do NOT search for: Nautical distances, standard demurrage rates, vessel speeds, or other static domain knowledge
✗ Avoid: Historical data, annual statistics, or general background information

**Priority Search Topics:**
1. Mumbai/JNPT port operational status (November 2025) - any congestion, strikes, berth closures
2. Red Sea/Suez Canal security situation (November 2025) - current threats, transit delays
3. Rotterdam port disruptions (November 2025) - labor actions, congestion, capacity issues

**Analysis Requirements:**

1. Consider all relevant factors:
   - Seasonal weather patterns (today is November - assess monsoon risk appropriately)
   - Current port congestion and capacity
   - Geopolitical and security risks
   - Route alternatives (Suez vs Cape of Good Hope)
   
2. Clearly separate in your response:
   - **Facts from web search** (cite sources with dates)
   - **General domain knowledge** (from your training)
   - **Assumptions** (explicitly state what you're assuming)
   
3. Propose 2-3 routing/departure strategies:
   - Logic and rationale for each option
   - Delay risk assessment (Low/Medium/High)
   - Cost-delay calculations with transparent assumptions
   - Use your knowledge for: vessel speeds (~20 knots), typical demurrage ($75-300/TEU/day), distances
   
4. Provide final recommendation with clear justification.

**Output Format:**
- Summary Recommendation (2-3 sentences highlighting urgency)
- Detailed Analysis (numbered sections with source citations)
- Assumptions & Limitations (be transparent about what you know vs. don't know)

**Remember:** This is a time-critical decision (36-hour window). Focus on actionable, current information that affects departure and transit in the next 2 weeks.
"""

# ----- Call API with web search -----

response = client.responses.create(
    model="gpt-5-nano",
    reasoning={"effort": "medium"},
    tools=[{"type": "web_search_preview"}],
    input=[{"role": "user", "content": prompt}]
)

# ----- Inspect ALL output items (including web search calls) -----

print("="*70)
print("WEB SEARCH QUERIES MADE BY AI")
print("="*70)

search_count = 0
for idx, item in enumerate(response.output):
    if item.type == "web_search_call":
        search_count += 1
        print(f"\n🔍 Search #{search_count}:")
        print(f"   Query: {item.web_search_call.search_query}")
        print(f"   Status: {item.status}")
        
if search_count == 0:
    print("\n⚠️ No web searches were performed by the AI")

# ----- Print detailed raw output (optional debugging) -----

print("\n" + "="*70)
print("DETAILED RAW OUTPUT (All Items)")
print("="*70)

for idx, item in enumerate(response.output):
    print(f"\n--- Item #{idx} ---")
    print(f"Type: {item.type}")
    
    # Show full structure
    try:
        print(item.model_dump())
    except Exception:
        print(item)

# ----- Print final answer -----

print("\n" + "="*70)
print("SHIPPING ROUTE ANALYSIS - FINAL ANSWER")
print("="*70)
print(f"\nDate: {today_str}\n")
print(response.output_text)