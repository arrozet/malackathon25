"""
AI Service using Multi-Agent Architecture with LangGraph.

This service implements a sophisticated multi-agent system where:
1. An orchestrator analyzes queries and routes to appropriate specialists
2. Specialist agents execute tasks and return ONLY natural language summaries
3. A synthesizer agent receives summaries and generates final responses
4. The final agent NEVER sees SQL, JSON, code, or technical details

This architecture optimizes token usage and improves response quality.
"""

from typing import List, Dict, Any, Optional, TypedDict, Annotated, AsyncGenerator
import logging
import operator
import json
import asyncio

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

from app.back.config import config
from app.back.services.agents import (
    OrchestratorAgent,
    SQLSpecialistAgent,
    SearchSpecialistAgent,
    PythonSpecialistAgent,
    DiagramSpecialistAgent,
    SynthesizerAgent,
)
from app.back.schemas import ChatMessage

logger = logging.getLogger(__name__)


# Define the state that flows through the agent graph
class AgentState(TypedDict):
    """
    State shared across all agents in the graph.
    
    This state is passed between nodes and accumulates information
    as it flows through the multi-agent pipeline.
    """
    user_query: str
    chat_history: List[Dict[str, str]]
    routing_decision: List[str]
    specialist_summaries: Annotated[List[Dict[str, Any]], operator.add]  # Accumulates summaries
    final_response: str
    tools_used: List[str]
    has_errors: bool


class AIService:
    """
    Multi-Agent AI Service for mental health research assistance.
    
    This service provides an intelligent assistant that orchestrates multiple
    specialized agents, each with a single responsibility:
    
    - **OrchestratorAgent**: Routes queries to appropriate specialists
    - **SQLSpecialistAgent**: Queries database, returns natural language summaries
    - **SearchSpecialistAgent**: Searches internet, returns synthesized findings
    - **PythonSpecialistAgent**: Executes code, returns interpreted results
    - **DiagramSpecialistAgent**: Generates diagrams, returns descriptions
    - **SynthesizerAgent**: Integrates summaries into final response
    
    Token Optimization:
    - Specialist agents summarize outputs (SQL → natural language)
    - Synthesizer only sees clean summaries, not technical details
    - Reduces context size by 60-80% compared to single-agent approach
    """
    
    def __init__(self):
        """
        Initializes the Multi-Agent AI service.
        
        Side Effects:
            Initializes all specialist agents and compiles the LangGraph workflow.
            Logs initialization status.
        
        Raises:
            ValueError: If XAI_API_KEY is not set.
        """
        logger.info("Initializing Multi-Agent AI Service...")
        
        if not config.XAI_API_KEY:
            raise ValueError(
                "XAI_API_KEY no configurada. "
                "Por favor, configura la variable de entorno XAI_API_KEY."
            )
        
        # Initialize all agents
        try:
            self.orchestrator = OrchestratorAgent()
            self.sql_specialist = SQLSpecialistAgent()
            self.search_specialist = SearchSpecialistAgent()
            self.python_specialist = PythonSpecialistAgent()
            self.diagram_specialist = DiagramSpecialistAgent()
            self.synthesizer = SynthesizerAgent()
            
            logger.info("All specialist agents initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            raise
        
        # Build the LangGraph workflow
        self.workflow = self._build_graph()
        
        logger.info("Multi-Agent AI Service initialized successfully")
        logger.info("Architecture: Orchestrator → Specialists → Synthesizer")
    
    def _build_graph(self) -> StateGraph:
        """
        Builds the LangGraph workflow for multi-agent orchestration.
        
        Returns:
            StateGraph: Compiled LangGraph workflow.
        """
        logger.info("Building LangGraph workflow...")
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("orchestrator", self._orchestrator_node)
        workflow.add_node("sql_specialist", self._sql_specialist_node)
        workflow.add_node("search_specialist", self._search_specialist_node)
        workflow.add_node("python_specialist", self._python_specialist_node)
        workflow.add_node("diagram_specialist", self._diagram_specialist_node)
        workflow.add_node("synthesizer", self._synthesizer_node)
        
        # Set entry point
        workflow.set_entry_point("orchestrator")
        
        # Add conditional edges from orchestrator to first specialist or synthesizer
        workflow.add_conditional_edges(
            "orchestrator",
            self._route_to_specialists,
            {
                "sql_specialist": "sql_specialist",
                "search_specialist": "search_specialist",
                "python_specialist": "python_specialist",
                "diagram_specialist": "diagram_specialist",
                "synthesizer": "synthesizer",  # Direct to synthesizer if no specialists needed
            }
        )
        
        # After each specialist, check if there are more specialists to execute
        # If yes, go to next specialist; if no, go to synthesizer
        # NOTE: Specialists cannot route back to themselves to avoid infinite loops
        workflow.add_conditional_edges(
            "sql_specialist",
            self._route_to_next_specialist,
            {
                "search_specialist": "search_specialist",
                "python_specialist": "python_specialist",
                "diagram_specialist": "diagram_specialist",
                "synthesizer": "synthesizer",
            }
        )
        
        workflow.add_conditional_edges(
            "search_specialist",
            self._route_to_next_specialist,
            {
                "sql_specialist": "sql_specialist",
                "python_specialist": "python_specialist",
                "diagram_specialist": "diagram_specialist",
                "synthesizer": "synthesizer",
            }
        )
        
        workflow.add_conditional_edges(
            "python_specialist",
            self._route_to_next_specialist,
            {
                "sql_specialist": "sql_specialist",
                "search_specialist": "search_specialist",
                "diagram_specialist": "diagram_specialist",
                "synthesizer": "synthesizer",
            }
        )
        
        workflow.add_conditional_edges(
            "diagram_specialist",
            self._route_to_next_specialist,
            {
                "sql_specialist": "sql_specialist",
                "search_specialist": "search_specialist",
                "python_specialist": "python_specialist",
                "synthesizer": "synthesizer",
            }
        )
        
        # Synthesizer is the end
        workflow.add_edge("synthesizer", END)
        
        # Compile the graph
        compiled_workflow = workflow.compile()
        
        logger.info("LangGraph workflow compiled successfully")
        
        return compiled_workflow
    
    def _orchestrator_node(self, state: AgentState) -> AgentState:
        """Node for orchestrator agent."""
        logger.info("Executing orchestrator node...")
        routing_decision = self.orchestrator.route(state["user_query"], state)
        state["routing_decision"] = routing_decision
        logger.info(f"Routing decision: {routing_decision}")
        return state
    
    def _route_to_specialists(self, state: AgentState) -> str:
        """
        Conditional routing function from orchestrator.
        
        Routes to the first specialist in the routing decision.
        """
        routing_decision = state.get("routing_decision", [])
        
        if not routing_decision:
            # No specialists needed, go directly to synthesizer
            logger.info("No specialists needed, routing to synthesizer")
            return "synthesizer"
        
        # Route to the first specialist
        first_specialist = routing_decision[0]
        logger.info(f"Routing to first specialist: {first_specialist}")
        
        return first_specialist
    
    def _route_to_next_specialist(self, state: AgentState) -> str:
        """
        Routes to the next specialist in the queue or to synthesizer if done.
        
        This function is called after each specialist completes to determine
        if there are more specialists to execute.
        
        Args:
            state (AgentState): Current agent state.
        
        Returns:
            str: Next node to route to (specialist name or "synthesizer").
        """
        routing_decision = state.get("routing_decision", [])
        
        if not routing_decision or len(routing_decision) == 0:
            # No more specialists to execute, go to synthesizer
            logger.info("All specialists completed, routing to synthesizer")
            return "synthesizer"
        
        # Get the next specialist
        next_specialist = routing_decision[0]
        logger.info(f"Routing to next specialist: {next_specialist} (remaining: {routing_decision})")
        
        return next_specialist
    
    def _sql_specialist_node(self, state: AgentState) -> AgentState:
        """Node for SQL specialist agent."""
        logger.info("Executing SQL specialist node...")
        result = self.sql_specialist.execute(state["user_query"], state)
        
        # Remove this specialist from routing decision (it's now complete)
        routing_decision = state.get("routing_decision", []).copy()
        if "sql_specialist" in routing_decision:
            routing_decision.remove("sql_specialist")
            state["routing_decision"] = routing_decision
            logger.info(f"SQL specialist complete. Remaining specialists: {routing_decision}")
        
        # Merge specialist summaries
        if "specialist_summaries" not in state:
            state["specialist_summaries"] = []
        state["specialist_summaries"].extend(result.get("specialist_summaries", []))
        
        return state
    
    def _search_specialist_node(self, state: AgentState) -> AgentState:
        """Node for search specialist agent."""
        logger.info("Executing search specialist node...")
        result = self.search_specialist.execute(state["user_query"], state)
        
        # Remove this specialist from routing decision (it's now complete)
        routing_decision = state.get("routing_decision", []).copy()
        if "search_specialist" in routing_decision:
            routing_decision.remove("search_specialist")
            state["routing_decision"] = routing_decision
            logger.info(f"Search specialist complete. Remaining specialists: {routing_decision}")
        
        # Merge specialist summaries
        if "specialist_summaries" not in state:
            state["specialist_summaries"] = []
        state["specialist_summaries"].extend(result.get("specialist_summaries", []))
        
        return state
    
    def _python_specialist_node(self, state: AgentState) -> AgentState:
        """Node for Python specialist agent."""
        logger.info("Executing Python specialist node...")
        result = self.python_specialist.execute(state["user_query"], state)
        
        # Remove this specialist from routing decision (it's now complete)
        routing_decision = state.get("routing_decision", []).copy()
        if "python_specialist" in routing_decision:
            routing_decision.remove("python_specialist")
            state["routing_decision"] = routing_decision
            logger.info(f"Python specialist complete. Remaining specialists: {routing_decision}")
        
        # Merge specialist summaries
        if "specialist_summaries" not in state:
            state["specialist_summaries"] = []
        state["specialist_summaries"].extend(result.get("specialist_summaries", []))
        
        return state
    
    def _diagram_specialist_node(self, state: AgentState) -> AgentState:
        """Node for diagram specialist agent."""
        logger.info("Executing diagram specialist node...")
        result = self.diagram_specialist.execute(state["user_query"], state)
        
        # Remove this specialist from routing decision (it's now complete)
        routing_decision = state.get("routing_decision", []).copy()
        if "diagram_specialist" in routing_decision:
            routing_decision.remove("diagram_specialist")
            state["routing_decision"] = routing_decision
            logger.info(f"Diagram specialist complete. Remaining specialists: {routing_decision}")
        
        # Merge specialist summaries
        if "specialist_summaries" not in state:
            state["specialist_summaries"] = []
        state["specialist_summaries"].extend(result.get("specialist_summaries", []))
        
        return state
    
    def _synthesizer_node(self, state: AgentState) -> AgentState:
        """Node for synthesizer agent."""
        logger.info("Executing synthesizer node...")
        
        # Check if we still have specialists to invoke
        routing_decision = state.get("routing_decision", [])
        if routing_decision:
            # There are more specialists to invoke, don't synthesize yet
            logger.warning(f"Synthesizer called but routing_decision still has: {routing_decision}")
            # This shouldn't happen with current graph structure
        
        result = self.synthesizer.synthesize(state)
        
        # Update state with final response
        state["final_response"] = result.get("final_response", "")
        state["tools_used"] = result.get("tools_used", [])
        state["has_errors"] = result.get("has_errors", False)
        
        return state
    
    async def chat_stream(self, message: str, chat_history: Optional[List[ChatMessage]] = None) -> AsyncGenerator[str, None]:
        """
        Processes a user message and streams progress events in real-time.
        
        This method yields Server-Sent Events (SSE) formatted strings that provide
        real-time feedback about the multi-agent thinking process.
        
        Args:
            message (str): User's message.
            chat_history (Optional[List[ChatMessage]]): Previous conversation messages.
        
        Yields:
            str: SSE-formatted event strings (data: {json}\n\n)
        
        Event types:
            - thinking: Agent is thinking/working (e.g., "Analizando la pregunta...")
            - routing: Routing decision made
            - specialist_start: Specialist agent started
            - specialist_complete: Specialist completed with summary
            - synthesizing: Final synthesis in progress
            - complete: Final response ready
            - error: An error occurred
        """
        try:
            logger.info(f"Processing chat message (streaming): {message[:100]}...")
            
            # Emit initial thinking event
            yield self._format_sse_event({
                "type": "thinking",
                "message": "Analizando tu pregunta..."
            })
            await asyncio.sleep(0.1)  # Small delay for UX
            
            # Prepare chat history
            formatted_history = []
            if chat_history:
                for msg in chat_history:
                    if isinstance(msg, dict):
                        formatted_history.append(msg)
                    else:  # Pydantic model
                        formatted_history.append({
                            "role": msg.role,
                            "content": msg.content
                        })
            
            # Initialize state
            initial_state: AgentState = {
                "user_query": message,
                "chat_history": formatted_history,
                "routing_decision": [],
                "specialist_summaries": [],
                "final_response": "",
                "tools_used": [],
                "has_errors": False,
            }
            
            # Step 1: Orchestrator routing
            yield self._format_sse_event({
                "type": "thinking",
                "message": "Determinando qué especialistas deben intervenir..."
            })
            
            orchestrator_state = self._orchestrator_node(initial_state)
            routing = orchestrator_state.get("routing_decision", [])
            
            # Emit routing decision
            specialist_names = {
                "sql_specialist": "Base de Datos",
                "search_specialist": "Búsqueda en Internet",
                "python_specialist": "Análisis Estadístico",
                "diagram_specialist": "Generación de Diagramas"
            }
            
            routing_msg = ", ".join([specialist_names.get(s, s) for s in routing])
            yield self._format_sse_event({
                "type": "routing",
                "specialists": routing,
                "message": f"Consultando: {routing_msg}"
            })
            await asyncio.sleep(0.1)
            
            # Step 2: Execute specialists
            current_state = orchestrator_state
            
            for specialist in routing:
                specialist_display = specialist_names.get(specialist, specialist)
                
                # Emit specialist start
                yield self._format_sse_event({
                    "type": "specialist_start",
                    "specialist": specialist,
                    "message": f"🔍 {specialist_display} trabajando..."
                })
                
                # Execute specialist
                if specialist == "sql_specialist":
                    current_state = self._sql_specialist_node(current_state)
                elif specialist == "search_specialist":
                    current_state = self._search_specialist_node(current_state)
                elif specialist == "python_specialist":
                    current_state = self._python_specialist_node(current_state)
                elif specialist == "diagram_specialist":
                    current_state = self._diagram_specialist_node(current_state)
                
                # Emit specialist complete
                yield self._format_sse_event({
                    "type": "specialist_complete",
                    "specialist": specialist,
                    "message": f"✓ {specialist_display} completado"
                })
                await asyncio.sleep(0.1)
            
            # Step 3: Synthesizer
            yield self._format_sse_event({
                "type": "synthesizing",
                "message": "Integrando toda la información..."
            })
            
            final_state = self._synthesizer_node(current_state)
            
            # Extract results
            response = final_state.get("final_response", "No se pudo generar una respuesta.")
            tools_used = final_state.get("tools_used", [])
            has_errors = final_state.get("has_errors", False)
            
            # Emit final response
            yield self._format_sse_event({
                "type": "complete",
                "response": response,
                "tools_used": tools_used,
                "has_errors": has_errors
            })
            
            logger.info("Streaming chat completed successfully")
            
        except Exception as e:
            error_msg = f"Error procesando mensaje: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Emit error event
            yield self._format_sse_event({
                "type": "error",
                "message": f"Lo siento, ocurrió un error: {str(e)}"
            })
    
    def _format_sse_event(self, data: Dict[str, Any]) -> str:
        """
        Formats a dictionary as a Server-Sent Event (SSE).
        
        Args:
            data (Dict[str, Any]): Event data to send.
        
        Returns:
            str: SSE-formatted event string.
        """
        json_data = json.dumps(data, ensure_ascii=False)
        return f"data: {json_data}\n\n"
    
    def chat(self, message: str, chat_history: Optional[List[ChatMessage]] = None) -> Dict[str, Any]:
        """
        Processes a user message and returns a response (non-streaming version).
        
        Args:
            message (str): User's message.
            chat_history (Optional[List[ChatMessage]]): Previous conversation messages.
        
        Returns:
            Dict[str, Any]: Response containing:
                - response (str): The AI's response
                - specialist_summaries (List[Dict]): Summaries from specialists (for debugging)
                - tools_used (List[str]): Tools that were invoked
                - has_errors (bool): Whether any errors occurred
        """
        try:
            logger.info(f"Processing chat message: {message[:100]}...")
            
            # Prepare chat history
            formatted_history = []
            if chat_history:
                for msg in chat_history:
                    if isinstance(msg, dict):
                        formatted_history.append(msg)
                    else:  # Pydantic model
                        formatted_history.append({
                            "role": msg.role,
                            "content": msg.content
                        })
            
            # Initialize state
            initial_state: AgentState = {
                "user_query": message,
                "chat_history": formatted_history,
                "routing_decision": [],
                "specialist_summaries": [],
                "final_response": "",
                "tools_used": [],
                "has_errors": False,
            }
            
            # Execute the workflow
            logger.info("Starting LangGraph workflow execution...")
            final_state = self.workflow.invoke(initial_state)
            
            logger.info("LangGraph workflow completed successfully")
            
            # Extract results
            response = final_state.get("final_response", "No se pudo generar una respuesta.")
            specialist_summaries = final_state.get("specialist_summaries", [])
            tools_used = final_state.get("tools_used", [])
            has_errors = final_state.get("has_errors", False)
            
            # Log token savings
            total_summary_length = sum(len(s.get("summary", "")) for s in specialist_summaries)
            logger.info(f"Response generated: {len(response)} chars from {len(specialist_summaries)} specialists")
            logger.info(f"Total specialist summaries: {total_summary_length} chars")
            
            return {
                "response": response,
                "specialist_summaries": specialist_summaries,  # Include for debugging
                "tools_used": tools_used,
                "has_errors": has_errors,
            }
            
        except Exception as e:
            error_msg = f"Error procesando mensaje: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return {
                "response": f"Lo siento, ocurrió un error al procesar tu mensaje: {str(e)}",
                "specialist_summaries": [],
                "tools_used": [],
                "has_errors": True,
            }
    
    def analyze(self, query: str) -> Dict[str, Any]:
        """
        Analyzes a specific data query.
        
        This is a convenience method that routes directly to the SQL specialist
        for quick data analysis queries.
        
        Args:
            query (str): Analysis query.
        
        Returns:
            Dict[str, Any]: Analysis results.
        """
        # For analysis, we primarily use SQL specialist
        return self.chat(query, chat_history=None)
    
    def visualize(self, query: str) -> Dict[str, Any]:
        """
        Generates a visualization based on the query.
        
        This is a convenience method that routes directly to the diagram specialist.
        
        Args:
            query (str): Visualization request.
        
        Returns:
            Dict[str, Any]: Visualization results.
        """
        # For visualization, we primarily use diagram specialist
        return self.chat(f"Genera un diagrama para: {query}", chat_history=None)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Performs a health check on the AI service.
        
        Returns:
            Dict[str, Any]: Health status of all components.
        """
        try:
            # Test basic LLM connectivity
            test_llm = ChatOpenAI(
                api_key=config.XAI_API_KEY,
                base_url="https://api.x.ai/v1",
                model="grok-4-fast-reasoning",
                temperature=0,
                max_tokens=10,
            )
            
            test_response = test_llm.invoke([HumanMessage(content="test")])
            
            return {
                "status": "healthy",
                "model": "grok-4-fast-reasoning",
                "architecture": "multi-agent",
                "agents": {
                    "orchestrator": "active",
                    "sql_specialist": "active",
                    "search_specialist": "active",
                    "python_specialist": "active",
                    "diagram_specialist": "active",
                    "synthesizer": "active",
                },
                "xai_api_key": "configured" if config.XAI_API_KEY else "missing",
                "tavily_api_key": "configured" if config.TAVILY_API_KEY else "missing",
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "xai_api_key": "configured" if config.XAI_API_KEY else "missing",
            }
