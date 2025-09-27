#!/usr/bin/env python3
"""
██╗  ██╗██╗  ██╗ █████╗ ███████╗ █████╗ ██████╗       ██████╗ ██╗   ██╗███╗   ███╗
██║ ██╔╝██║  ██║██╔══██╗╚══███╔╝██╔══██╗██╔══██╗      ██╔══██╗██║   ██║████╗ ████║
█████╔╝ ███████║███████║  ███╔╝ ███████║██║  ██║█████╗██║  ██║██║   ██║██╔████╔██║
██╔═██╗ ██╔══██║██╔══██║ ███╔╝  ██╔══██║██║  ██║╚════╝██║  ██║██║   ██║██║╚██╔╝██║
██║  ██╗██║  ██║██║  ██║███████╗██║  ██║██████╔╝      ██████╔╝╚██████╔╝██║ ╚═╝ ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝       ╚═════╝  ╚═════╝ ╚═╝     ╚═╝

🏔️ ALGORITHMIC TRADING SYSTEM - "They delved too greedily and too deep..."

┌─────────────────────────────────────────────────────────────────────────────────────┐
│ 📋 MODULE: Web Monitoring Dashboard                                                 │
│ 📄 FILE: app.py                                                                    │
│ 📅 CREATED: 2024-12-21                                                             │
│ 👑 AUTHOR: FeanorKingofNoldor                                                      │
│ 🔗 REPOSITORY: https://github.com/FeanorKingofNoldor/khazad_dum                   │
│ 📧 CONTACT: [Your Contact Info]                                                    │
│                                                                                     │
│ 🎯 PURPOSE:                                                                        │
│ Mobile-friendly web interface for remote monitoring of trading system status       │
│                                                                                     │
│ 🔧 DEPENDENCIES:                                                                   │
│ - FastAPI web framework                                                            │
│ - WebSocket real-time communication                                                │
│ - Jinja2 templates                                                                 │
│ - SQLite/PostgreSQL database                                                       │
│                                                                                     │
│ 📈 TRADING PIPELINE STAGE: System Monitoring (All Stages)                        │
│ └── 1. Market Regime Detection                                                     │
│ └── 2. Stock Screening                                                             │
│ └── 3. AI Analysis (TradingAgents)                                                 │
│ └── 4. Pattern Recognition                                                         │
│ └── 5. Portfolio Construction                                                      │
│ └── 6. Performance Observation ← Primary Focus                                    │
│                                                                                     │
│ ⚠️  CRITICAL NOTES:                                                                │
│ - Requires active database connection                                              │
│ - WebSocket connections auto-broadcast updates                                     │
│ - Mobile-optimized responsive design                                               │
│                                                                                     │
│ 📊 PERFORMANCE NOTES:                                                              │
│ - Real-time updates via WebSocket (< 100ms latency)                              │
│ - Supports multiple concurrent connections                                         │
│ - Database queries optimized for dashboard display                                │
│                                                                                     │
│ 🧪 TESTING:                                                                        │
│ - Unit Tests: tests/unit/test_web_dashboard.py                                    │
│ - Integration Tests: tests/integration/test_dashboard_integration.py              │
│                                                                                     │
│ 📚 DOCUMENTATION:                                                                  │
│ - API Docs: Auto-generated from docstrings                                        │
│ - Usage Guide: docs/guides/WEB_DASHBOARD_USAGE.md                                 │
└─────────────────────────────────────────────────────────────────────────────────────┘

Licensed under MIT License - See LICENSE file for details
Copyright (c) 2024 FeanorKingofNoldor

"In the depths of Khazad-dûm, the markets reveal their secrets to those who dare..."
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
from contextlib import asynccontextmanager

# Import our existing monitoring system
from src.monitoring.health_check import health_check_endpoint
from src.data_pipeline.storage.database_manager import DatabaseManager


class WebDashboard:
    """Web-based monitoring dashboard for remote access"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.db = DatabaseManager()
    
    async def connect(self, websocket: WebSocket):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast_update(self, data: dict):
        """Broadcast data to all connected clients"""
        if self.active_connections:
            message = json.dumps(data)
            disconnected = []
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.disconnect(connection)
    
    async def get_trading_summary(self) -> Dict[str, Any]:
        """Get current trading summary"""
        try:
            cursor = self.db.conn.execute("""
                SELECT 
                    COUNT(*) as total_positions,
                    COUNT(CASE WHEN status = 'OPEN' THEN 1 END) as open_positions,
                    SUM(CASE WHEN status = 'OPEN' THEN position_size_dollars ELSE 0 END) as open_value,
                    SUM(CASE WHEN status = 'CLOSED' AND pnl_dollars IS NOT NULL THEN pnl_dollars ELSE 0 END) as total_pnl
                FROM position_tracking
            """)
            row = cursor.fetchone()
            
            # Get recent performance
            cursor = self.db.conn.execute("""
                SELECT 
                    COUNT(*) as recent_trades,
                    AVG(CASE WHEN pnl_pct IS NOT NULL THEN pnl_pct ELSE 0 END) as avg_return,
                    COUNT(CASE WHEN pnl_pct > 0 THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN pnl_pct IS NOT NULL THEN 1 END), 0) as win_rate
                FROM position_tracking 
                WHERE exit_date >= date('now', '-7 days')
                AND status = 'CLOSED'
            """)
            perf_row = cursor.fetchone()
            
            return {
                "total_positions": row[0] if row else 0,
                "open_positions": row[1] if row else 0,
                "open_value": float(row[2]) if row and row[2] else 0.0,
                "total_pnl": float(row[3]) if row and row[3] else 0.0,
                "recent_trades": perf_row[0] if perf_row else 0,
                "avg_return": float(perf_row[1]) if perf_row and perf_row[1] else 0.0,
                "win_rate": float(perf_row[2]) if perf_row and perf_row[2] else 0.0
            }
        except Exception as e:
            return {
                "total_positions": 0,
                "open_positions": 0,
                "open_value": 0.0,
                "total_pnl": 0.0,
                "recent_trades": 0,
                "avg_return": 0.0,
                "win_rate": 0.0,
                "error": str(e)
            }
    
    async def get_active_positions(self) -> List[Dict[str, Any]]:
        """Get list of active positions"""
        try:
            cursor = self.db.conn.execute("""
                SELECT 
                    symbol,
                    entry_date,
                    entry_price,
                    quantity,
                    position_size_dollars,
                    stop_loss,
                    target_price,
                    conviction_score,
                    (julianday('now') - julianday(entry_date)) as days_held
                FROM position_tracking 
                WHERE status = 'OPEN'
                ORDER BY entry_date DESC
            """)
            
            positions = []
            for row in cursor.fetchall():
                positions.append({
                    "symbol": row[0],
                    "entry_date": row[1],
                    "entry_price": float(row[2]) if row[2] else 0.0,
                    "quantity": row[3],
                    "position_size": float(row[4]) if row[4] else 0.0,
                    "stop_loss": float(row[5]) if row[5] else 0.0,
                    "target_price": float(row[6]) if row[6] else 0.0,
                    "conviction": float(row[7]) if row[7] else 0.0,
                    "days_held": int(row[8]) if row[8] else 0
                })
            
            return positions
        except Exception as e:
            return [{"error": str(e)}]
    
    async def get_recent_signals(self) -> List[Dict[str, Any]]:
        """Get recent trading signals"""
        try:
            cursor = self.db.conn.execute("""
                SELECT 
                    symbol,
                    analysis_date,
                    decision,
                    conviction_score,
                    entry_price,
                    regime
                FROM tradingagents_analysis_results 
                WHERE analysis_date >= date('now', '-7 days')
                ORDER BY created_at DESC
                LIMIT 20
            """)
            
            signals = []
            for row in cursor.fetchall():
                signals.append({
                    "symbol": row[0],
                    "date": row[1],
                    "decision": row[2],
                    "conviction": float(row[3]) if row[3] else 0.0,
                    "entry_price": float(row[4]) if row[4] else 0.0,
                    "regime": row[5]
                })
            
            return signals
        except Exception as e:
            return [{"error": str(e)}]


# Create dashboard instance
dashboard = WebDashboard()

# Create FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asyncio.create_task(update_broadcaster())
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Khazad-dûm Trading Dashboard",
    description="Remote monitoring for your algorithmic trading system",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="src/web_dashboard/static"), name="static")
templates = Jinja2Templates(directory="src/web_dashboard/templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/health")
async def api_health():
    """System health endpoint"""
    return await health_check_endpoint()


@app.get("/api/trading-summary")
async def api_trading_summary():
    """Trading summary endpoint"""
    return await dashboard.get_trading_summary()


@app.get("/api/positions")
async def api_positions():
    """Active positions endpoint"""
    return await dashboard.get_active_positions()


@app.get("/api/signals")
async def api_signals():
    """Recent signals endpoint"""
    return await dashboard.get_recent_signals()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await dashboard.connect(websocket)
    try:
        while True:
            # Keep connection alive and wait for messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        dashboard.disconnect(websocket)


async def update_broadcaster():
    """Background task to broadcast updates to connected clients"""
    while True:
        try:
            # Collect all data
            health_data = await health_check_endpoint()
            trading_summary = await dashboard.get_trading_summary()
            positions = await dashboard.get_active_positions()
            signals = await dashboard.get_recent_signals()
            
            # Create update payload
            update_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "type": "dashboard_update",
                "data": {
                    "health": health_data,
                    "trading": trading_summary,
                    "positions": positions[:5],  # Only show top 5
                    "signals": signals[:10]      # Only show recent 10
                }
            }
            
            # Broadcast to all connected clients
            await dashboard.broadcast_update(update_data)
            
        except Exception as e:
            print(f"Update broadcaster error: {e}")
        
        # Update every 30 seconds
        await asyncio.sleep(30)


if __name__ == "__main__":
    uvicorn.run(
        "src.web_dashboard.app:app",
        host="0.0.0.0",  # Listen on all interfaces
        port=8002,       # Different port from main app
        reload=False,    # Disable in production
        log_level="info"
    )