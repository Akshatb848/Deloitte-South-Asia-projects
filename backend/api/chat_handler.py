"""
Chat Handler - Orchestrates LLM and RAG for conversational interface
"""

import re
from typing import Dict, Any, List, Optional


class ChatHandler:
    """Handles chat interactions between user, RAG, and LLM"""

    def __init__(self, rag_system, llm_handler):
        self.rag_system = rag_system
        self.llm_handler = llm_handler
        self.visualization_keywords = {
            'graph': 'trendsChart',
            'chart': 'trendsChart',
            'trend': 'trendsChart',
            'attendance': 'trendsChart',
            'state': 'stateChart',
            'compare states': 'stateChart',
            'infrastructure': 'infrastructureChart',
            'apaar': 'apaarChart'
        }

    async def initialize(self):
        """Initialize chat handler"""
        print("Chat handler ready")

    async def process_query(
        self,
        query: str,
        current_month: Optional[str] = None,
        include_visualization: bool = True
    ) -> Dict[str, Any]:
        """
        Process user query and generate response

        Args:
            query: User query
            current_month: Current month context
            include_visualization: Whether to detect visualization requests

        Returns:
            Dictionary with response, sources, and optional visualization
        """
        # Analyze query intent
        intent = await self.llm_handler.analyze_query_intent(query)

        # Handle different query types
        if intent['type'] == 'comparison' and len(intent['entities']) >= 2:
            return await self._handle_comparison_query(
                query,
                intent['entities'],
                intent.get('metric'),
                current_month
            )

        # Regular query processing
        response_data = await self._process_regular_query(
            query,
            current_month,
            include_visualization
        )

        return response_data

    async def _process_regular_query(
        self,
        query: str,
        current_month: Optional[str],
        include_visualization: bool
    ) -> Dict[str, Any]:
        """Process regular factual or trend queries"""

        # Retrieve relevant context
        search_results = await self.rag_system.search(
            query,
            top_k=3,
            filter_month=current_month
        )

        # Format context
        context = self._format_context(search_results)

        # Generate response
        response_text = await self.llm_handler.generate_response(
            query=query,
            context=context,
            temperature=0.3
        )

        # Prepare response data
        response_data = {
            "response": response_text,
            "sources": [
                {
                    "month": result['metadata']['month_name'],
                    "type": result['type'],
                    "score": result['score']
                }
                for result in search_results[:3]
            ]
        }

        # Detect visualization request
        if include_visualization:
            viz_data = self._detect_visualization_request(query)
            if viz_data:
                response_data['visualization'] = viz_data

        return response_data

    async def _handle_comparison_query(
        self,
        query: str,
        entities: List[str],
        metric: Optional[str],
        current_month: Optional[str]
    ) -> Dict[str, Any]:
        """Handle comparison queries (e.g., compare states, months)"""

        # Detect what's being compared
        comparison_type = self._detect_comparison_type(query, entities)

        if comparison_type == 'states':
            return await self._compare_states(entities, metric, current_month)
        elif comparison_type == 'months':
            return await self._compare_months(entities, metric)
        else:
            # Fallback to regular query
            return await self._process_regular_query(query, current_month, False)

    def _detect_comparison_type(self, query: str, entities: List[str]) -> str:
        """Detect what type of comparison is being requested"""
        query_lower = query.lower()

        # Check for state names
        indian_states = ['kerala', 'gujarat', 'tamil nadu', 'karnataka', 'maharashtra', 'delhi']
        state_count = sum(1 for state in indian_states if any(state in entity.lower() for entity in entities))

        if state_count >= 2:
            return 'states'

        # Check for month references
        months = ['april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december', 'january']
        month_count = sum(1 for month in months if month in query_lower)

        if month_count >= 2 or 'month' in query_lower:
            return 'months'

        return 'general'

    async def _compare_states(
        self,
        states: List[str],
        metric: Optional[str],
        month: Optional[str]
    ) -> Dict[str, Any]:
        """Compare performance metrics across states"""

        if not month:
            # Use latest month
            months = self.rag_system.get_available_months()
            month = months[-1]

        month_data = self.rag_system.get_month_data(month)

        if not month_data:
            return {
                "response": "The requested month data is not available.",
                "sources": []
            }

        # Extract state performance data
        state_performance = month_data.get('state_performance', {})

        # Filter requested states (fuzzy match)
        comparison_data = {}
        for state_key in state_performance.keys():
            for requested_state in states:
                if requested_state.lower() in state_key.lower():
                    comparison_data[state_key] = state_performance[state_key]

        if not comparison_data:
            return {
                "response": f"No data available for the requested states in {month_data['month']}.",
                "sources": []
            }

        # Format comparison response
        response_parts = [f"State Performance Comparison for {month_data['month']}:\n"]

        for state, metrics in comparison_data.items():
            response_parts.append(
                f"\n{state}:"
                f"\n- Attendance Rate: {metrics['attendance']}%"
                f"\n- APAAR Coverage: {metrics['apaar_coverage']}%"
            )

        # Add analysis
        if len(comparison_data) >= 2:
            states_list = list(comparison_data.keys())
            best_attendance = max(comparison_data.items(), key=lambda x: x[1]['attendance'])
            best_apaar = max(comparison_data.items(), key=lambda x: x[1]['apaar_coverage'])

            response_parts.append(
                f"\n\nAnalysis:"
                f"\n- Highest Attendance: {best_attendance[0]} ({best_attendance[1]['attendance']}%)"
                f"\n- Highest APAAR Coverage: {best_apaar[0]} ({best_apaar[1]['apaar_coverage']}%)"
            )

        return {
            "response": "".join(response_parts),
            "sources": [{
                "month": month_data['month'],
                "type": "state_performance",
                "score": 1.0
            }],
            "visualization": {
                "type": "chart",
                "chartId": "stateChart"
            }
        }

    async def _compare_months(
        self,
        months: List[str],
        metric: Optional[str]
    ) -> Dict[str, Any]:
        """Compare metrics across different months"""

        # Extract month data
        all_months = self.rag_system.get_available_months()

        # Build comparison
        response_parts = ["Monthly Comparison:\n"]

        if not metric or 'attendance' in metric.lower():
            response_parts.append("\nAttendance Rate Trend:")
            for month_key in all_months:
                month_data = self.rag_system.get_month_data(month_key)
                response_parts.append(
                    f"- {month_data['month']}: {month_data['stats']['attendance_rate']}%"
                )

        if not metric or 'teacher' in metric.lower():
            response_parts.append("\n\nTeacher Tracking Trend:")
            for month_key in all_months:
                month_data = self.rag_system.get_month_data(month_key)
                response_parts.append(
                    f"- {month_data['month']}: {month_data['stats']['teacher_tracking']}%"
                )

        return {
            "response": "".join(response_parts),
            "sources": [{"month": "All Months", "type": "trend_analysis", "score": 1.0}],
            "visualization": {
                "type": "chart",
                "chartId": "trendsChart"
            }
        }

    async def handle_comparison(
        self,
        entities: List[str],
        metric: str,
        months: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Public method to handle comparison requests from API endpoint

        Args:
            entities: List of entities to compare (states, etc.)
            metric: Metric to compare (attendance, apaar, etc.)
            months: Optional list of months to include

        Returns:
            Comparison data
        """
        month = months[0] if months else None

        result = await self._compare_states(entities, metric, month)

        return {
            "comparison_data": result,
            "entities": entities,
            "metric": metric
        }

    def _format_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Format search results into context for LLM"""
        if not search_results:
            return "No relevant information found."

        context_parts = []
        for idx, result in enumerate(search_results, 1):
            context_parts.append(
                f"[Source {idx} - {result['metadata']['month_name']} - {result['type']}]"
            )
            context_parts.append(result['text'])
            context_parts.append("")  # Empty line

        return "\n".join(context_parts)

    def _detect_visualization_request(self, query: str) -> Optional[Dict[str, str]]:
        """Detect if query is requesting a visualization"""
        query_lower = query.lower()

        for keyword, chart_id in self.visualization_keywords.items():
            if keyword in query_lower:
                return {
                    "type": "chart",
                    "chartId": chart_id
                }

        return None
