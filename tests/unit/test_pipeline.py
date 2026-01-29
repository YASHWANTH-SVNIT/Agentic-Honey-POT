"""
Unit tests for Detection Pipeline (Phase 2.5)

Tests the full orchestration step and session updates.
"""
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime

from app.models.schemas import Message, MessageRequest
from app.models.session import SessionData
from app.services.detection.pipeline import DetectionPipeline
from app.services.detection.decision_maker import FinalDecision

@pytest.mark.asyncio
class TestDetectionPipeline:
    """Test suite for Detection Pipeline orchestration"""
    
    @pytest.fixture
    def mock_session_manager(self):
        manager = MagicMock()
        session = SessionData(
            sessionId="test_session",
            status="active"
        )
        manager.get_session.return_value = session
        manager.create_session.return_value = session
        return manager

    @pytest.fixture
    def pipeline(self, mock_session_manager):
        with patch('app.services.detection.pipeline.get_session_manager', return_value=mock_session_manager):
            pipeline = DetectionPipeline()
            return pipeline
            
    async def test_pipeline_ignore_flow(self, pipeline):
        """Test pipeline flow when pre-screening rejects"""
        # Mock pre-screen to reject
        with patch('app.services.detection.pipeline.pre_screen_message') as mock_screen:
            mock_screen.return_value = MagicMock(action="ignore", reason="Empty")
            
            request = MessageRequest(
                sessionId="test",
                message=Message(sender="user", text="")
            )
            
            result = await pipeline.process(request)
            
            assert result["action"] == "ignore"
            assert result["reason"] == "Empty"
            
    async def test_pipeline_engage_flow(self, pipeline):
        """Test pipeline flow when scam detected leads to ENGAGE"""
        # Mock all steps
        with patch('app.services.detection.pipeline.pre_screen_message') as mock_screen, \
             patch('app.services.detection.pipeline.detect_and_route') as mock_lang, \
             patch('app.services.detection.pipeline.retrieve_rag_evidence') as mock_rag, \
             patch('app.services.detection.pipeline.detect_scam_normal_mode') as mock_detect, \
             patch('app.services.detection.pipeline.make_final_decision') as mock_decide:
             
            # 1. Pre-screen pass
            mock_screen.return_value = MagicMock(action="continue")
            
            # 2. Language detect
            mock_lang.return_value = MagicMock(language="en", confidence=0.99, mode="normal")
            
            # 3. RAG
            mock_rag.return_value = MagicMock(matches=[])
            
            # 4. LLM Detect
            mock_detect.return_value = MagicMock(is_scam=True, confidence=0.95)
            
            # 5. Decision
            mock_decide.return_value = FinalDecision(
                action="engage",
                scam_detected=True,
                confidence=0.95,
                category="digital_arrest",
                reasoning="Test scam",
                detection_mode="normal",
                threshold_used=0.7,
                red_flags=["Flag1"]
            )
            
            request = MessageRequest(
                sessionId="test",
                message=Message(sender="user", text="Hello scam")
            )
            
            result = await pipeline.process(request)
            
            assert result["action"] == "engage"
            
            # Verify session update
            # The session object in mock_session_manager should have been updated
            session = pipeline.session_manager.get_session("test")
            assert session.scam_detected is True
            assert session.category == "digital_arrest"
            assert session.confidence == 0.95
            assert session.stage == "engagement"
            
            # Verify update_session was called
            pipeline.session_manager.update_session.assert_called_once()
