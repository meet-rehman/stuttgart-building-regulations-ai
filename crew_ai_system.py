#!/usr/bin/env python3
"""
Multi-Agent Stuttgart Building Regulations System using CrewAI
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# CrewAI imports
from crewai import Agent, Task, Crew, Process
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.schema import Document

# Custom imports (your existing system)
from precomputed_rag import EnhancedPrecomputedRAGSystem as PrecomputedRAGSystem

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RegulationQuery:
    """Structure for regulation queries"""
    query: str
    project_type: str = "mixed-use"
    location: str = "Stuttgart"
    district: str = "general"
    urgency: str = "normal"
    
class DocumentSearchTool:
    """Custom tool for searching building regulations"""
    
    def __init__(self):
        self.rag_system = PrecomputedRAGSystem()
    
    def search_documents(self, query: str, top_k: int = 5) -> str:
        """Search documents and return formatted results"""
        try:
            results = self.rag_system.search(query, top_k=top_k)
            
            if not results:
                return f"No relevant documents found for query: {query}"
            
            formatted_results = []
            for i, result in enumerate(results, 1):
                metadata = result.get('metadata', {})
                content = result.get('content', '')[:500]
                
                formatted_result = f"""
Document {i}:
- File: {metadata.get('document_name', 'Unknown')}
- Category: {metadata.get('category', 'Unknown')}
- Page: {metadata.get('page_number', 'Unknown')}
- Content Preview: {content}...
                """
                formatted_results.append(formatted_result)
            
            return "\n".join(formatted_results)
            
        except Exception as e:
            return f"Error searching documents: {str(e)}"

class LegalHierarchyTool:
    """Tool for understanding regulatory hierarchy"""
    
    def analyze_hierarchy(self, regulations: str) -> str:
        """Analyze regulatory hierarchy"""
        hierarchy_rules = {
            "federal": ["BauGB", "EnEV", "GEG", "DIN", "VDI"],
            "state": ["LBO", "Baden-Württemberg", "BW"],
            "local": ["Stuttgart", "Zuffenhausen", "Municipal", "Stadt"]
        }
        
        analysis = []
        for level, keywords in hierarchy_rules.items():
            if any(keyword.lower() in regulations.lower() for keyword in keywords):
                analysis.append(f"{level.upper()} level regulations identified")
        
        if len(analysis) > 1:
            return f"Multiple regulatory levels apply. Hierarchy: {' > '.join(analysis)}. Local regulations may override state where specifically permitted."
        elif analysis:
            return f"Primary regulatory level: {analysis[0]}"
        else:
            return "Regulatory level unclear - recommend consulting multiple sources"

class ComplianceCostTool:
    """Tool for estimating compliance costs"""
    
    def estimate_costs(self, requirements: str) -> str:
        """Estimate compliance costs"""
        cost_factors = {
            "accessibility": {"cost_multiplier": 1.1, "time_weeks": 2},
            "fire_safety": {"cost_multiplier": 1.15, "time_weeks": 3},
            "energy_efficiency": {"cost_multiplier": 1.2, "time_weeks": 4},
            "parking": {"cost_multiplier": 1.05, "time_weeks": 1},
            "setback": {"cost_multiplier": 1.02, "time_weeks": 1}
        }
        
        applicable_factors = []
        total_multiplier = 1.0
        total_time = 0
        
        for factor, values in cost_factors.items():
            if factor in requirements.lower():
                applicable_factors.append(factor)
                total_multiplier *= values["cost_multiplier"]
                total_time += values["time_weeks"]
        
        if applicable_factors:
            return f"Compliance factors: {', '.join(applicable_factors)}. Estimated cost impact: +{(total_multiplier-1)*100:.1f}%. Timeline: {total_time} weeks additional."
        else:
            return "Standard compliance requirements. Estimated timeline: 2-4 weeks."

class StuttgartBuildingRegulationCrew:
    """Main crew orchestrating the multi-agent system"""
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            openai_api_key=openai_api_key
        )
        
        # Initialize tools
        self.document_tool = DocumentSearchTool()
        self.hierarchy_tool = LegalHierarchyTool()
        self.cost_tool = ComplianceCostTool()
        
        # Create agents
        self.agents = self._create_agents()
        
    def _create_agents(self) -> Dict[str, Agent]:
        """Create specialized agents"""
        
        document_specialist = Agent(
            role="Document Research Specialist",
            goal="Find and analyze relevant building regulations from Stuttgart's comprehensive database",
            backstory="""You are an expert at navigating complex German building regulation 
            documents. You can quickly identify the most relevant regulations for any building 
            project and extract precise citations and requirements.""",
            tools=[],  # Start with no tools to avoid validation error
            llm=self.llm,
            verbose=True
        )
        
        legal_analyst = Agent(
            role="Regulatory Legal Analyst", 
            goal="Interpret regulatory hierarchy and resolve conflicts between different levels of regulation",
            backstory="""You are a legal expert specializing in German building law. You understand 
            the complex interplay between federal (BauGB), state (LBO BW), and municipal regulations. 
            You can determine which regulations take precedence and identify potential conflicts.""",
            tools=[],
            llm=self.llm,
            verbose=True
        )
        
        technical_standards_expert = Agent(
            role="Technical Standards Expert",
            goal="Analyze technical requirements including DIN standards, accessibility, and safety regulations", 
            backstory="""You are a technical expert who understands DIN standards, accessibility 
            requirements (DIN 18040), fire safety regulations, and energy efficiency standards. 
            You translate technical requirements into practical implementation guidance.""",
            tools=[],
            llm=self.llm,
            verbose=True
        )
        
        compliance_strategist = Agent(
            role="Compliance Strategy Advisor",
            goal="Develop cost-effective compliance strategies and assess risks",
            backstory="""You are a seasoned building industry professional who helps developers 
            and architects navigate compliance requirements efficiently. You understand the practical 
            and financial implications of different regulatory approaches.""",
            tools=[],
            llm=self.llm,
            verbose=True
        )
        
        synthesis_manager = Agent(
            role="Professional Synthesis Manager",
            goal="Integrate all analyses into comprehensive, actionable recommendations",
            backstory="""You are a senior building regulation consultant who synthesizes complex 
            regulatory analysis into clear, professional recommendations. You provide decision-makers 
            with the information they need to move forward confidently.""",
            tools=[],
            llm=self.llm,
            verbose=True
        )
        
        return {
            "document_specialist": document_specialist,
            "legal_analyst": legal_analyst, 
            "technical_expert": technical_standards_expert,
            "compliance_strategist": compliance_strategist,
            "synthesis_manager": synthesis_manager
        }
    
    def create_tasks(self, query: RegulationQuery) -> List[Task]:
        """Create tasks for the crew based on the query"""
        
        document_research_task = Task(
            description=f"""Research all relevant building regulations for: {query.query}
            Project details:
            - Type: {query.project_type}
            - Location: {query.location}
            - District: {query.district}
            
            Use the document search system to find regulations from:
            1. Federal level (BauGB, DIN standards)
            2. State level (LBO Baden-Württemberg)
            3. Local level (Stuttgart municipal regulations)
            4. District-specific requirements for {query.district}
            
            Search through the 8,826 document database and provide detailed citations with:
            - Document names and file paths
            - Page numbers and sections
            - Content excerpts
            - Legal reference numbers""",
            expected_output="Comprehensive list of relevant regulations with precise citations and content excerpts",
            agent=self.agents["document_specialist"]
        )
        
        legal_hierarchy_task = Task(
            description=f"""Analyze the regulatory hierarchy for the regulations found in the previous task.
            
            Use legal hierarchy analysis to determine:
            1. Which regulations take precedence (federal > state > local)
            2. Any conflicts between different regulatory levels
            3. How local Stuttgart regulations interact with state LBO BW
            4. Special provisions for {query.district} district
            5. Override conditions where local rules supersede state rules
            
            Provide clear guidance on regulatory priority and conflict resolution.""",
            expected_output="Legal hierarchy analysis with precedence rules and conflict resolution guidance",
            agent=self.agents["legal_analyst"]
        )
        
        technical_analysis_task = Task(
            description=f"""Analyze technical requirements for: {query.query}
            
            Focus on technical standards including:
            1. DIN standards (accessibility DIN 18040, sound insulation DIN 4109, etc.)
            2. Fire safety requirements for {query.project_type}
            3. Energy efficiency standards (EnEV/GEG)
            4. Structural and safety requirements
            5. Building physics requirements
            
            Translate technical standards into practical implementation requirements with specific compliance criteria.""",
            expected_output="Technical requirements summary with implementation guidance and compliance criteria",
            agent=self.agents["technical_expert"]
        )
        
        compliance_strategy_task = Task(
            description=f"""Develop comprehensive compliance strategy for: {query.query}
            
            Use compliance cost analysis to assess:
            1. Cost implications of different compliance approaches
            2. Timeline requirements for permits and approvals
            3. Risk assessment for non-compliance scenarios
            4. Alternative compliance methods where permitted
            5. Cost multipliers for accessibility, fire safety, energy efficiency
            6. Estimated additional timeline (weeks) for each requirement
            
            Provide detailed cost-benefit analysis and strategic recommendations.""",
            expected_output="Compliance strategy with cost analysis, timeline, and risk assessment",
            agent=self.agents["compliance_strategist"]
        )
        
        synthesis_task = Task(
            description=f"""Synthesize all previous analyses into a professional consultation report for: {query.query}
            
            Integrate findings from:
            - Document research results
            - Legal hierarchy analysis  
            - Technical requirements assessment
            - Compliance strategy recommendations
            
            Create a comprehensive response including:
            1. Executive Summary with key requirements
            2. Detailed regulatory analysis with precise citations
            3. Step-by-step compliance roadmap
            4. Cost and timeline estimates with breakdowns
            5. Risk factors and mitigation strategies
            6. Required forms and documents list
            7. Next steps and recommended actions
            8. Professional recommendations for implementation
            
            Format as a professional consultation report suitable for architects, developers, or city officials.""",
            expected_output="Professional consultation report with executive summary, detailed analysis, and actionable recommendations",
            agent=self.agents["synthesis_manager"]
        )
        
        # Set task dependencies - this is crucial for information flow
        legal_hierarchy_task.context = [document_research_task]
        technical_analysis_task.context = [document_research_task]
        compliance_strategy_task.context = [document_research_task, legal_hierarchy_task, technical_analysis_task]
        synthesis_task.context = [document_research_task, legal_hierarchy_task, technical_analysis_task, compliance_strategy_task]
        
        return [document_research_task, legal_hierarchy_task, technical_analysis_task, compliance_strategy_task, synthesis_task]
    
    def execute_analysis(self, query: RegulationQuery) -> str:
        """Execute the multi-agent analysis"""
        try:
            logger.info(f"Starting multi-agent analysis for: {query.query}")
            
            # Create tasks
            tasks = self.create_tasks(query)
            
            # Create and execute crew
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=tasks,
                process=Process.sequential,
                verbose=True
            )
            
            # Execute the crew
            result = crew.kickoff()
            
            logger.info("Multi-agent analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error in multi-agent analysis: {e}")
            return f"Error occurred during analysis: {str(e)}"

def main():
    """Test the multi-agent system"""
    
    # Initialize the system
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable required")
    
    crew_system = StuttgartBuildingRegulationCrew(openai_api_key)
    
    # Test query
    test_query = RegulationQuery(
        query="What are the complete requirements for building a mixed-use development with residential and commercial space?",
        project_type="mixed-use",
        location="Stuttgart",
        district="Zuffenhausen"
    )
    
    # Execute analysis
    result = crew_system.execute_analysis(test_query)
    print("="*80)
    print("MULTI-AGENT ANALYSIS RESULT:")
    print("="*80)
    print(result)

if __name__ == "__main__":
    main()