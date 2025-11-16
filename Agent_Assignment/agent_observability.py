# =========================================
# Agent Observability & Performance Tracker
# =========================================
# Track tool selection accuracy, response times,
# and agent performance metrics
# =========================================

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

class AgentObservability:
    """
    Track and analyze agent performance metrics
    
    Metrics tracked:
    - Tool selection accuracy
    - Response times
    - Tool usage distribution
    - Success/failure rates
    - User satisfaction (optional feedback)
    """
    
    def __init__(self, log_file: str = "agent_logs.jsonl"):
        self.log_file = Path(log_file)
        self.current_session = {
            "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "start_time": time.time(),
            "interactions": []
        }
    
    def log_interaction(
        self,
        user_question: str,
        tool_selected: Optional[str],
        expected_tool: Optional[str],
        response_time: float,
        success: bool,
        response_text: str,
        tool_args: Optional[Dict] = None,
        tool_result: Optional[Dict] = None,
        error: Optional[str] = None
    ):
        """Log a single interaction with the agent"""
        
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.current_session["session_id"],
            "user_question": user_question,
            "tool_selected": tool_selected,
            "expected_tool": expected_tool,
            "tool_match": tool_selected == expected_tool if expected_tool else None,
            "tool_args": tool_args,
            "tool_result": tool_result,
            "response_time_seconds": round(response_time, 3),
            "success": success,
            "response_length": len(response_text),
            "error": error
        }
        
        self.current_session["interactions"].append(interaction)
        
        # Append to log file (JSONL format)
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(interaction) + "\n")
        
        return interaction
    
    def get_session_summary(self) -> Dict:
        """Get summary statistics for current session"""
        
        interactions = self.current_session["interactions"]
        
        if not interactions:
            return {"message": "No interactions logged yet"}
        
        # Tool selection accuracy
        tool_matches = [i for i in interactions if i["tool_match"] is not None]
        accuracy = sum(1 for i in tool_matches if i["tool_match"]) / len(tool_matches) if tool_matches else 0
        
        # Tool usage distribution
        tools_used = [i["tool_selected"] for i in interactions if i["tool_selected"]]
        tool_distribution = {}
        for tool in tools_used:
            tool_distribution[tool] = tool_distribution.get(tool, 0) + 1
        
        # Response time stats
        response_times = [i["response_time_seconds"] for i in interactions]
        
        # Success rate
        success_rate = sum(1 for i in interactions if i["success"]) / len(interactions)
        
        return {
            "session_id": self.current_session["session_id"],
            "total_interactions": len(interactions),
            "tool_selection_accuracy": round(accuracy * 100, 2),
            "tool_distribution": tool_distribution,
            "avg_response_time": round(sum(response_times) / len(response_times), 3),
            "min_response_time": round(min(response_times), 3),
            "max_response_time": round(max(response_times), 3),
            "success_rate": round(success_rate * 100, 2),
            "failed_interactions": sum(1 for i in interactions if not i["success"])
        }
    
    def print_session_summary(self):
        """Print formatted session summary"""
        
        summary = self.get_session_summary()
        
        if "message" in summary:
            print(f"\n⚠️ {summary['message']}\n")
            return
        
        print("\n" + "="*70)
        print("📊 AGENT PERFORMANCE SUMMARY")
        print("="*70)
        print(f"\n🆔 Session ID: {summary['session_id']}")
        print(f"📈 Total Interactions: {summary['total_interactions']}")
        print(f"\n🎯 Tool Selection Accuracy: {summary['tool_selection_accuracy']}%")
        print(f"✅ Success Rate: {summary['success_rate']}%")
        print(f"❌ Failed Interactions: {summary['failed_interactions']}")
        
        print(f"\n⏱️ Response Time Statistics:")
        print(f"   Average: {summary['avg_response_time']}s")
        print(f"   Fastest: {summary['min_response_time']}s")
        print(f"   Slowest: {summary['max_response_time']}s")
        
        print(f"\n🔧 Tool Usage Distribution:")
        for tool, count in summary['tool_distribution'].items():
            percentage = (count / summary['total_interactions']) * 100
            print(f"   {tool}: {count} ({percentage:.1f}%)")
        
        print("="*70 + "\n")
    
    def get_tool_accuracy_report(self) -> pd.DataFrame:
        """Generate detailed tool accuracy report"""
        
        interactions = self.current_session["interactions"]
        
        # Filter interactions with expected tool
        tool_tests = [i for i in interactions if i["expected_tool"] is not None]
        
        if not tool_tests:
            print("⚠️ No tool accuracy tests logged (expected_tool was None)")
            return pd.DataFrame()
        
        # Group by expected tool
        accuracy_data = []
        for expected in set(i["expected_tool"] for i in tool_tests):
            tests = [i for i in tool_tests if i["expected_tool"] == expected]
            correct = sum(1 for i in tests if i["tool_match"])
            
            accuracy_data.append({
                "Expected Tool": expected,
                "Total Tests": len(tests),
                "Correct Selections": correct,
                "Accuracy (%)": round((correct / len(tests)) * 100, 2)
            })
        
        df = pd.DataFrame(accuracy_data)
        return df.sort_values("Accuracy (%)", ascending=False)
    
    def print_tool_accuracy_report(self):
        """Print formatted tool accuracy report"""
        
        df = self.get_tool_accuracy_report()
        
        if df.empty:
            return
        
        print("\n" + "="*70)
        print("🎯 TOOL SELECTION ACCURACY BY TOOL")
        print("="*70)
        print(df.to_string(index=False))
        print("="*70 + "\n")
    
    def get_failed_interactions(self) -> List[Dict]:
        """Get list of failed interactions for debugging"""
        
        interactions = self.current_session["interactions"]
        return [i for i in interactions if not i["success"]]
    
    def print_failed_interactions(self):
        """Print details of failed interactions"""
        
        failed = self.get_failed_interactions()
        
        if not failed:
            print("\n✅ No failed interactions in this session!\n")
            return
        
        print("\n" + "="*70)
        print(f"❌ FAILED INTERACTIONS ({len(failed)} total)")
        print("="*70)
        
        for i, interaction in enumerate(failed, 1):
            print(f"\n--- Failure #{i} ---")
            print(f"Question: {interaction['user_question']}")
            print(f"Tool Selected: {interaction['tool_selected']}")
            print(f"Error: {interaction['error']}")
            print(f"Timestamp: {interaction['timestamp']}")
        
        print("="*70 + "\n")
    
    def get_tool_confusion_matrix(self) -> pd.DataFrame:
        """Generate confusion matrix for tool selection"""
        
        interactions = self.current_session["interactions"]
        tool_tests = [i for i in interactions if i["expected_tool"] is not None]
        
        if not tool_tests:
            print("⚠️ No tool tests logged for confusion matrix")
            return pd.DataFrame()
        
        # Get all unique tools
        all_tools = set()
        for i in tool_tests:
            all_tools.add(i["expected_tool"])
            if i["tool_selected"]:
                all_tools.add(i["tool_selected"])
        
        all_tools = sorted(all_tools)
        
        # Build confusion matrix
        matrix = {tool: {t: 0 for t in all_tools} for tool in all_tools}
        
        for interaction in tool_tests:
            expected = interaction["expected_tool"]
            actual = interaction["tool_selected"] or "none"
            if actual in matrix.get(expected, {}):
                matrix[expected][actual] += 1
        
        df = pd.DataFrame(matrix).T
        return df
    
    def print_confusion_matrix(self):
        """Print tool selection confusion matrix"""
        
        df = self.get_tool_confusion_matrix()
        
        if df.empty:
            return
        
        print("\n" + "="*70)
        print("🔀 TOOL SELECTION CONFUSION MATRIX")
        print("="*70)
        print("Rows = Expected Tool | Columns = Actual Tool Selected\n")
        print(df.to_string())
        print("="*70 + "\n")
    
    def export_to_csv(self, filename: str = "agent_performance.csv"):
        """Export all interactions to CSV for analysis"""
        
        interactions = self.current_session["interactions"]
        
        if not interactions:
            print("⚠️ No interactions to export")
            return
        
        # Flatten interactions for CSV
        csv_data = []
        for i in interactions:
            csv_data.append({
                "timestamp": i["timestamp"],
                "session_id": i["session_id"],
                "user_question": i["user_question"],
                "tool_selected": i["tool_selected"],
                "expected_tool": i["expected_tool"],
                "tool_match": i["tool_match"],
                "response_time_seconds": i["response_time_seconds"],
                "success": i["success"],
                "response_length": i["response_length"],
                "error": i["error"]
            })
        
        df = pd.DataFrame(csv_data)
        df.to_csv(filename, index=False)
        print(f"\n✅ Exported {len(interactions)} interactions to {filename}\n")
    
    def load_historical_logs(self) -> pd.DataFrame:
        """Load all historical logs from JSONL file"""
        
        if not self.log_file.exists():
            print(f"⚠️ Log file {self.log_file} does not exist yet")
            return pd.DataFrame()
        
        logs = []
        with self.log_file.open("r", encoding="utf-8") as f:
            for line in f:
                logs.append(json.loads(line))
        
        return pd.DataFrame(logs)
    
    def print_historical_summary(self):
        """Print summary of all historical logs"""
        
        df = self.load_historical_logs()
        
        if df.empty:
            print("⚠️ No historical logs available\n")
            return
        
        print("\n" + "="*70)
        print("📚 HISTORICAL PERFORMANCE (ALL SESSIONS)")
        print("="*70)
        
        # Overall stats
        total_interactions = len(df)
        unique_sessions = df['session_id'].nunique()
        
        # Tool accuracy
        tool_tests = df[df['tool_match'].notna()]
        overall_accuracy = (tool_tests['tool_match'].sum() / len(tool_tests) * 100) if len(tool_tests) > 0 else 0
        
        # Success rate
        success_rate = df['success'].sum() / len(df) * 100
        
        # Avg response time
        avg_response_time = df['response_time_seconds'].mean()
        
        print(f"\n📊 Total Interactions: {total_interactions}")
        print(f"🔄 Total Sessions: {unique_sessions}")
        print(f"🎯 Overall Tool Accuracy: {overall_accuracy:.2f}%")
        print(f"✅ Overall Success Rate: {success_rate:.2f}%")
        print(f"⏱️ Average Response Time: {avg_response_time:.3f}s")
        
        # Most common questions
        print(f"\n📝 Most Common Questions:")
        top_questions = df['user_question'].value_counts().head(5)
        for question, count in top_questions.items():
            print(f"   • {question[:50]}... ({count} times)")
        
        print("="*70 + "\n")


# =========================================
# HELPER FUNCTION FOR INTEGRATION
# =========================================

def create_observer(log_file: str = "agent_logs.jsonl") -> AgentObservability:
    """Factory function to create observer instance"""
    return AgentObservability(log_file=log_file)


# =========================================
# STANDALONE USAGE EXAMPLE
# =========================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("📊 AGENT OBSERVABILITY - Standalone Demo")
    print("="*70)
    
    # Create observer
    observer = AgentObservability(log_file="demo_logs.jsonl")
    
    # Simulate some interactions
    print("\n🔄 Simulating agent interactions...\n")
    
    # Successful interactions
    observer.log_interaction(
        user_question="What's the status of order ORD-1005?",
        tool_selected="check_order_status",
        expected_tool="check_order_status",
        response_time=1.234,
        success=True,
        response_text="Your order is in Processing status..."
    )
    
    observer.log_interaction(
        user_question="Track container MAEU7654321",
        tool_selected="get_tracking_info",
        expected_tool="get_tracking_info",
        response_time=0.987,
        success=True,
        response_text="Container is en route from Shanghai to LA..."
    )
    
    observer.log_interaction(
        user_question="What is your return policy?",
        tool_selected="file_search",
        expected_tool="file_search",
        response_time=1.567,
        success=True,
        response_text="Our return policy requires a Return Authorization Number..."
    )
    
    # Wrong tool selection
    observer.log_interaction(
        user_question="Ship my order faster",
        tool_selected="check_order_status",  # Wrong!
        expected_tool="file_search",
        response_time=1.123,
        success=True,
        response_text="To expedite shipping, please contact..."
    )
    
    # Failed interaction
    observer.log_interaction(
        user_question="Order status ORD-9999",
        tool_selected="check_order_status",
        expected_tool="check_order_status",
        response_time=0.856,
        success=False,
        response_text="",
        error="Order not found in database"
    )
    
    # Print all reports
    observer.print_session_summary()
    observer.print_tool_accuracy_report()
    observer.print_confusion_matrix()
    observer.print_failed_interactions()
    
    # Export to CSV
    observer.export_to_csv("demo_performance.csv")
    
    print("✅ Demo complete! Check demo_logs.jsonl and demo_performance.csv\n")
