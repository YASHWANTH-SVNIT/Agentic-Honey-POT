"""
Anti-Detection Response Analyzer

This module analyzes conversation history to ensure response diversity
and prevent detectable patterns that could reveal the honeypot nature.
"""

from typing import List, Dict, Set
import re


class AntiDetectionAnalyzer:
    """
    Analyzes conversation history to prevent repetitive patterns
    and ensure natural variation in responses.
    """
    
    def __init__(self):
        self.common_phrases = set()
        self.question_patterns = set()
        self.sentence_structures = []
    
    def analyze_history(self, history: List[Dict[str, str]]) -> Dict[str, any]:
        """
        Analyze conversation history to identify patterns to avoid.
        
        Args:
            history: List of previous messages
            
        Returns:
            Dictionary with patterns to avoid and suggestions
        """
        agent_messages = []
        
        # Extract only agent's previous responses
        for msg in history:
            sender = msg.get("role", msg.get("sender", ""))
            if sender in ["agent", "assistant", "honeypot"]:
                text = msg.get("content", msg.get("text", ""))
                if text:
                    agent_messages.append(text)
        
        if not agent_messages:
            return self._empty_analysis()
        
        # Analyze patterns
        repeated_phrases = self._find_repeated_phrases(agent_messages)
        repeated_questions = self._find_repeated_questions(agent_messages)
        overused_words = self._find_overused_words(agent_messages)
        sentence_starts = self._find_common_sentence_starts(agent_messages)
        
        return {
            "repeated_phrases": repeated_phrases,
            "repeated_questions": repeated_questions,
            "overused_words": overused_words,
            "common_starts": sentence_starts,
            "message_count": len(agent_messages),
            "diversity_score": self._calculate_diversity(agent_messages)
        }
    
    def _find_repeated_phrases(self, messages: List[str]) -> List[str]:
        """Find phrases that appear in multiple messages."""
        phrases = []
        phrase_counts = {}
        
        for msg in messages:
            # Extract 3-5 word phrases
            words = msg.lower().split()
            for i in range(len(words) - 2):
                for length in [3, 4, 5]:
                    if i + length <= len(words):
                        phrase = " ".join(words[i:i+length])
                        phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        
        # Return phrases used more than once
        repeated = [p for p, count in phrase_counts.items() if count > 1]
        return repeated[:10]  # Top 10
    
    def _find_repeated_questions(self, messages: List[str]) -> List[str]:
        """Find questions that were asked multiple times."""
        questions = []
        question_counts = {}
        
        for msg in messages:
            # Extract sentences ending with ?
            sentences = re.split(r'[.!?]+', msg)
            for sent in sentences:
                sent = sent.strip()
                if '?' in sent or sent.endswith('?'):
                    # Normalize question
                    q = sent.lower().strip('?').strip()
                    question_counts[q] = question_counts.get(q, 0) + 1
        
        repeated = [q for q, count in question_counts.items() if count > 1]
        return repeated[:5]  # Top 5
    
    def _find_overused_words(self, messages: List[str]) -> List[str]:
        """Find words used too frequently."""
        # Common filler words to track
        filler_words = ["just", "really", "very", "like", "actually", "basically", 
                       "literally", "honestly", "please", "sorry", "ok", "okay"]
        
        word_counts = {word: 0 for word in filler_words}
        
        for msg in messages:
            words = msg.lower().split()
            for word in words:
                clean_word = re.sub(r'[^\w]', '', word)
                if clean_word in word_counts:
                    word_counts[clean_word] += 1
        
        # Return words used more than 3 times
        overused = [w for w, count in word_counts.items() if count > 3]
        return overused
    
    def _find_common_sentence_starts(self, messages: List[str]) -> List[str]:
        """Find sentence starting patterns used repeatedly."""
        starts = []
        start_counts = {}
        
        for msg in messages:
            sentences = re.split(r'[.!?]+', msg)
            for sent in sentences:
                sent = sent.strip()
                if len(sent) > 5:
                    # Get first 2-3 words
                    words = sent.split()[:3]
                    start = " ".join(words).lower()
                    start_counts[start] = start_counts.get(start, 0) + 1
        
        repeated = [s for s, count in start_counts.items() if count > 1]
        return repeated[:5]
    
    def _calculate_diversity(self, messages: List[str]) -> float:
        """
        Calculate diversity score (0-1, higher is better).
        Based on unique words vs total words.
        """
        if not messages:
            return 1.0
        
        all_words = []
        for msg in messages:
            words = re.findall(r'\w+', msg.lower())
            all_words.extend(words)
        
        if not all_words:
            return 1.0
        
        unique_ratio = len(set(all_words)) / len(all_words)
        return round(unique_ratio, 2)
    
    def _empty_analysis(self) -> Dict[str, any]:
        """Return empty analysis for new conversations."""
        return {
            "repeated_phrases": [],
            "repeated_questions": [],
            "overused_words": [],
            "common_starts": [],
            "message_count": 0,
            "diversity_score": 1.0
        }
    
    def generate_avoidance_instructions(self, analysis: Dict[str, any]) -> str:
        """
        Generate natural language instructions to avoid detected patterns.
        
        Args:
            analysis: Result from analyze_history()
            
        Returns:
            String with avoidance instructions for the LLM
        """
        if analysis["message_count"] == 0:
            return "This is your first response - be natural and authentic."
        
        instructions = []
        
        # Repeated phrases
        if analysis["repeated_phrases"]:
            phrases_str = ", ".join([f'"{p}"' for p in analysis["repeated_phrases"][:3]])
            instructions.append(f"⚠️ AVOID repeating these phrases: {phrases_str}")
        
        # Repeated questions
        if analysis["repeated_questions"]:
            questions_str = ", ".join([f'"{q}?"' for q in analysis["repeated_questions"][:2]])
            instructions.append(f"⚠️ DON'T ask these questions again: {questions_str}")
        
        # Overused words
        if analysis["overused_words"]:
            words_str = ", ".join(analysis["overused_words"])
            instructions.append(f"⚠️ Try not to use: {words_str} (you've used them too much)")
        
        # Common starts
        if analysis["common_starts"]:
            starts_str = ", ".join([f'"{s}"' for s in analysis["common_starts"][:2]])
            instructions.append(f"⚠️ Don't start sentences with: {starts_str}")
        
        # Diversity warning
        if analysis["diversity_score"] < 0.5:
            instructions.append("⚠️ Your responses are becoming repetitive - use completely different words and structures!")
        
        if not instructions:
            return "✓ Keep varying your responses - you're doing well!"
        
        return "\n".join(instructions)


# Global singleton
_analyzer = None

def get_analyzer() -> AntiDetectionAnalyzer:
    """Get or create global analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = AntiDetectionAnalyzer()
    return _analyzer
