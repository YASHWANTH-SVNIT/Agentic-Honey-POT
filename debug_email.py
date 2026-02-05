"""
Debug Email Extraction
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import asyncio
from app.services.intelligence.investigator import InvestigatorAgent

async def test_extraction():
    print("Testing Email Extraction...")
    
    text = "Send your resume to hr@jobs-online.in and cc to support@company.com"
    print(f"Input: {text}")
    
    result = await InvestigatorAgent.analyze(text)
    
    print("\nResult:")
    print(result)
    
    if "hr@jobs-online.in" in result.get("intelligence", {}).get("emailIds", []):
         print("✅ Email 1 found")
    else:
         print("❌ Email 1 MISSING")
         
    if "support@company.com" in result.get("intelligence", {}).get("emailIds", []):
         print("✅ Email 2 found")
    else:
         print("❌ Email 2 MISSING")

if __name__ == "__main__":
    asyncio.run(test_extraction())
