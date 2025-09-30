#!/usr/bin/env python3
"""
Multi-Agent Flask Application for Stuttgart Building Regulations
Integrates CrewAI multi-agent system with existing Flask infrastructure
"""
from dotenv import load_dotenv
load_dotenv()

import os
import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

# Import our multi-agent system
from crew_ai_system import StuttgartBuildingRegulationCrew, RegulationQuery

# Existing imports
from schemas import ChatRequest, ChatResponse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
crew_system: Optional[StuttgartBuildingRegulationCrew] = None

class MultiAgentRequest(BaseModel):
    """Request model for multi-agent analysis"""
    query: str
    project_type: str = "mixed-use"
    location: str = "Stuttgart"
    district: str = "general"
    urgency: str = "normal"
    use_multi_agent: bool = True

class MultiAgentResponse(BaseModel):
    """Response model for multi-agent analysis"""
    analysis: str
    timestamp: str
    query_details: Dict[str, Any]
    processing_time: Optional[float] = None
    agents_used: list = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global crew_system
    
    try:
        print("🚀 Starting Stuttgart Building Regulation Multi-Agent System...")
        
        # Step 1: Validate environment
        print("Step 1: Validating environment variables...")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        print("✅ Environment variables validated")
        
        # Step 2: Initialize multi-agent system
        print("Step 2: Initializing multi-agent crew...")
        crew_system = StuttgartBuildingRegulationCrew(openai_api_key)
        print("✅ Multi-agent crew initialized successfully")
        
        print("✅ APP STARTED SUCCESSFULLY!")
        print("=" * 60)
        print("Available endpoints:")
        print("- GET  /: Main interface")
        print("- POST /chat: Single-agent chat (legacy)")
        print("- POST /multi-agent: Multi-agent analysis (new)")
        print("- GET  /health: System health check")
        print("=" * 60)
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise
    finally:
        print("🔄 Shutting down application...")

# Create FastAPI app
app = FastAPI(
    title="Stuttgart Building Regulations AI",
    description="Multi-Agent AI System for Stuttgart Building Code Analysis",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main application interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Stuttgart Building Regulations AI - Multi-Agent System</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px; 
            }
            .header {
                text-align: center;
                color: white;
                margin-bottom: 30px;
            }
            .header h1 { 
                font-size: 2.5rem; 
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .header p { 
                font-size: 1.2rem; 
                opacity: 0.9; 
            }
            .analysis-section {
                background: white;
                border-radius: 15px;
                padding: 30px;
                margin-bottom: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .query-form {
                display: grid;
                gap: 20px;
                margin-bottom: 30px;
            }
            .form-group {
                display: flex;
                flex-direction: column;
            }
            .form-group label {
                font-weight: 600;
                margin-bottom: 5px;
                color: #555;
            }
            .form-group input, .form-group select, .form-group textarea {
                padding: 12px;
                border: 2px solid #e1e5e9;
                border-radius: 8px;
                font-size: 16px;
                transition: border-color 0.3s;
            }
            .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            .form-group textarea {
                min-height: 120px;
                resize: vertical;
            }
            .analyze-btn {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s;
            }
            .analyze-btn:hover {
                transform: translateY(-2px);
            }
            .analyze-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .results-section {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .results-section h3 {
                color: #667eea;
                margin-bottom: 15px;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #667eea;
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .agent-badge {
                display: inline-block;
                background: #667eea;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                margin: 2px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏗️ Stuttgart Building Regulations AI</h1>
                <p>Multi-Agent System for Professional Building Code Analysis</p>
            </div>
            
            <div class="analysis-section">
                <h2>Professional Building Regulation Analysis</h2>
                <p style="margin-bottom: 20px; color: #666;">
                    Our multi-agent AI system provides comprehensive analysis using specialized agents for 
                    document research, legal interpretation, technical standards, and compliance strategy.
                </p>
                
                <form class="query-form" id="analysisForm">
                    <div class="form-group">
                        <label for="query">Your Building Regulation Question</label>
                        <textarea 
                            id="query" 
                            name="query" 
                            placeholder="e.g., What are the complete requirements for building a mixed-use development with residential and commercial space in Stuttgart?"
                            required
                        ></textarea>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div class="form-group">
                            <label for="project_type">Project Type</label>
                            <select id="project_type" name="project_type">
                                <option value="mixed-use">Mixed-Use Development</option>
                                <option value="residential">Residential Building</option>
                                <option value="commercial">Commercial Building</option>
                                <option value="industrial">Industrial Building</option>
                                <option value="office">Office Building</option>
                                <option value="renovation">Renovation Project</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="district">Stuttgart District</label>
                            <select id="district" name="district">
                                <option value="general">General Stuttgart</option>
                                <option value="Zuffenhausen">Zuffenhausen</option>
                                <option value="Stuttgart-Mitte">Stuttgart-Mitte</option>
                                <option value="Stuttgart-West">Stuttgart-West</option>
                                <option value="Stuttgart-Ost">Stuttgart-Ost</option>
                                <option value="Stuttgart-Nord">Stuttgart-Nord</option>
                                <option value="Stuttgart-Süd">Stuttgart-Süd</option>
                            </select>
                        </div>
                    </div>
                    
                    <button type="submit" class="analyze-btn" id="analyzeBtn">
                        🤖 Start Multi-Agent Analysis
                    </button>
                </form>
                
                <div id="results" class="results-section" style="display: none;">
                    <h3>Analysis Results</h3>
                    <div id="resultsContent"></div>
                </div>
            </div>
        </div>

        <script>
            document.getElementById('analysisForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const form = e.target;
                const formData = new FormData(form);
                const analyzeBtn = document.getElementById('analyzeBtn');
                const results = document.getElementById('results');
                const resultsContent = document.getElementById('resultsContent');
                
                // Disable button and show loading
                analyzeBtn.disabled = true;
                analyzeBtn.innerHTML = '🔄 Analyzing...';
                results.style.display = 'block';
                resultsContent.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>Multi-agent analysis in progress...</p>
                        <p><small>This may take 1-2 minutes as our agents collaborate</small></p>
                    </div>
                `;
                
                try {
                    const response = await fetch('/multi-agent', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            query: formData.get('query'),
                            project_type: formData.get('project_type'),
                            district: formData.get('district'),
                            location: 'Stuttgart',
                            urgency: 'normal',
                            use_multi_agent: true
                        })
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const data = await response.json();
                    
                    resultsContent.innerHTML = `
                        <div style="white-space: pre-wrap; line-height: 1.6;">${data.analysis}</div>
                        <hr style="margin: 20px 0;">
                        <p><strong>Analysis completed at:</strong> ${data.timestamp}</p>
                        ${data.processing_time ? `<p><strong>Processing time:</strong> ${data.processing_time.toFixed(2)} seconds</p>` : ''}
                    `;
                    
                } catch (error) {
                    console.error('Error:', error);
                    resultsContent.innerHTML = `
                        <div style="color: #dc3545;">
                            <h4>Error occurred during analysis</h4>
                            <p>${error.message}</p>
                            <p>Please try again or contact support if the issue persists.</p>
                        </div>
                    `;
                } finally {
                    // Re-enable button
                    analyzeBtn.disabled = false;
                    analyzeBtn.innerHTML = '🤖 Start Multi-Agent Analysis';
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/multi-agent", response_model=MultiAgentResponse)
async def multi_agent_analysis(request: MultiAgentRequest, background_tasks: BackgroundTasks):
    """Execute multi-agent analysis"""
    if not crew_system:
        raise HTTPException(status_code=503, detail="Multi-agent system not initialized")
    
    try:
        start_time = datetime.now()
        
        # Create regulation query
        query = RegulationQuery(
            query=request.query,
            project_type=request.project_type,
            location=request.location,
            district=request.district,
            urgency=request.urgency
        )
        
        # Execute multi-agent analysis
        logger.info(f"Starting multi-agent analysis for: {request.query}")
        crew_result = crew_system.execute_analysis(query)
        analysis_result = str(crew_result)  # Convert CrewOutput to string
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return MultiAgentResponse(
            analysis=analysis_result,
            timestamp=end_time.isoformat(),
            query_details={
                "query": request.query,
                "project_type": request.project_type,
                "location": request.location,
                "district": request.district,
                "urgency": request.urgency
            },
            processing_time=processing_time,
            agents_used=[
                "Document Research Specialist",
                "Regulatory Legal Analyst", 
                "Technical Standards Expert",
                "Compliance Strategy Advisor",
                "Professional Synthesis Manager"
            ]
        )
        
    except Exception as e:
        logger.error(f"Multi-agent analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def legacy_chat_endpoint(request: ChatRequest):
    """Legacy single-agent endpoint for backward compatibility"""
    try:
        # For backward compatibility, redirect to multi-agent if available
        if crew_system:
            multi_agent_request = MultiAgentRequest(
                query=request.message,
                project_type="mixed-use",
                location="Stuttgart",
                district="general"
            )
            
            result = await multi_agent_analysis(multi_agent_request, BackgroundTasks())
            
            return ChatResponse(
                message=result.analysis,
                timestamp=result.timestamp,
                context_used=5,  # Placeholder
                conversation_id=getattr(request, 'conversation_id', None)
            )
        else:
            raise HTTPException(status_code=503, detail="AI system not available")
            
    except Exception as e:
        logger.error(f"Legacy chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

# Add this as a backup simple health check
@app.get("/ping")
async def ping():
    """Simple ping endpoint for basic health checking"""
    return {"status": "ok", "service": "running"}

# Keep your detailed health check as well
@app.get("/health")
async def health_check():
    """Detailed system health check"""
    try:
        status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "multi_agent_ready": crew_system is not None,
            "components": {
                "crew_system": "ready" if crew_system else "not_initialized",
                "openai_api": "configured" if os.getenv("OPENAI_API_KEY") else "missing",
                "document_database": "available"
            },
            "agents": [
                "Document Research Specialist",
                "Regulatory Legal Analyst", 
                "Technical Standards Expert",
                "Compliance Strategy Advisor",
                "Professional Synthesis Manager"
            ] if crew_system else []
        }
        return status
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "multi_agent_ready": False
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))