#!/usr/bin/env python3
"""
Test script for streaming analysis wrapper functionality.

This script tests various scenarios to ensure the backend properly:
1. Detects markdown headers as semantic boundaries
2. Identifies content with component potential
3. Creates placeholders for analysis
4. Generates appropriate components
"""

import asyncio
import json
import aiohttp
import time
from typing import Dict, Any, List

# Test cases with different component potentials
TEST_CASES = [
    {
        "name": "Simple Pie Chart Data",
        "message": """# Market Share Analysis

Our market analysis shows the following distribution:
- Instagram: 45%
- TikTok: 30%
- Facebook: 25%

This represents our social media presence across platforms.""",
        "expected_components": ["pie-chart"],
        "expected_placeholders": 1
    },
    
    {
        "name": "Quarterly Sales (Bar Chart)",
        "message": """# Quarterly Sales Report

## Sales Performance
Q1 2024: $150k
Q2 2024: $180k
Q3 2024: $220k
Q4 2024: $195k

The quarterly performance shows strong growth in Q3.""",
        "expected_components": ["bar-chart"],
        "expected_placeholders": 1
    },
    
    {
        "name": "Time Series Data (Line Chart)",
        "message": """# Monthly Revenue Trends

## 2024 Performance
January: $50k
February: $55k
March: $48k
April: $62k
May: $58k
June: $65k

The trend shows steady growth with some seasonal variations.""",
        "expected_components": ["line-chart"],
        "expected_placeholders": 1
    },
    
    {
        "name": "Complex Multi-Section Report",
        "message": """# Annual Business Report

## Executive Summary
This year has been remarkable for our company with significant growth across all sectors.

## Sales Performance
Q1: $100k
Q2: $150k
Q3: $200k
Q4: $180k

## Market Share
- Product A: 40%
- Product B: 35%
- Product C: 25%

## Regional Distribution
North: $220k
South: $180k
East: $150k
West: $200k

## Employee Satisfaction Survey
Very Satisfied: 45%
Satisfied: 35%
Neutral: 15%
Dissatisfied: 5%

## Conclusion
The data shows consistent growth and high employee satisfaction.""",
        "expected_components": ["bar-chart", "pie-chart"],
        "expected_placeholders": 3  # Multiple data sections
    },
    
    {
        "name": "Mixed Content (Some Potential)",
        "message": """# Company Update

## Introduction
Welcome to our monthly company update. We have exciting news to share.

## New Hires
We've welcomed 15 new team members this month across various departments.

## Budget Allocation
Marketing: 40%
Development: 35%
Operations: 25%

## Upcoming Events
- Team building on March 15th
- Product launch on April 2nd
- Quarterly review on April 30th

## Final Notes
Thank you all for your hard work and dedication.""",
        "expected_components": ["pie-chart"],
        "expected_placeholders": 1  # Only budget allocation has potential
    },
    
    {
        "name": "No Component Potential",
        "message": """# General Information

## About Us
We are a technology company focused on innovation and excellence.

## Our Mission
To create solutions that make a difference in people's lives.

## Values
- Integrity
- Innovation
- Collaboration
- Excellence

## Contact Information
Email: info@company.com
Phone: (555) 123-4567

Thank you for your interest in our company.""",
        "expected_components": [],
        "expected_placeholders": 0
    }
]

class StreamingAnalysisTest:
    """Test class for streaming analysis functionality."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_streaming_endpoint(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single streaming endpoint with the given test case."""
        print(f"\n🧪 Testing: {test_case['name']}")
        print(f"📝 Message length: {len(test_case['message'])} characters")
        print(f"🎯 Expected components: {test_case['expected_components']}")
        print(f"📍 Expected placeholders: {test_case['expected_placeholders']}")
        
        url = f"{self.base_url}/api/v1/api/chat/stream"
        payload = {
            "message": test_case['message'],
            "ai_settings": {"temperature": 0.7},
            "user_preferences": {}
        }
        
        results = {
            "test_name": test_case['name'],
            "chunks_received": 0,
            "placeholders_created": 0,
            "components_generated": 0,
            "placeholder_ids": [],
            "component_types": [],
            "content_chunks": [],
            "errors": [],
            "streaming_time": 0
        }
        
        start_time = time.time()
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status != 200:
                    results["errors"].append(f"HTTP {response.status}: {await response.text()}")
                    return results
                
                print("📡 Starting stream analysis...")
                
                async for line in response.content:
                    line_text = line.decode('utf-8').strip()
                    
                    if line_text.startswith('data: '):
                        try:
                            data = json.loads(line_text[6:])  # Remove 'data: ' prefix
                            chunk_type = data.get('type', 'unknown')
                            
                            results["chunks_received"] += 1
                            
                            # Analyze different chunk types
                            if chunk_type == 'content':
                                content = data.get('content', '')
                                results["content_chunks"].append(content)
                                print(f"📄 Content chunk: {content[:50]}...")
                            
                            elif chunk_type == 'placeholder':
                                placeholder_id = data.get('placeholder_id')
                                results["placeholders_created"] += 1
                                results["placeholder_ids"].append(placeholder_id)
                                print(f"🔄 Placeholder created: {placeholder_id}")
                                print(f"   Content: {data.get('content', 'N/A')}")
                            
                            elif chunk_type == 'component_replacement':
                                component = data.get('component', {})
                                component_type = component.get('type', 'unknown')
                                results["components_generated"] += 1
                                results["component_types"].append(component_type)
                                print(f"✅ Component generated: {component_type}")
                                print(f"   Replacing: {data.get('placeholder_id')}")
                                print(f"   Confidence: {component.get('confidence', 'N/A')}")
                            
                            elif chunk_type == 'placeholder_removal':
                                placeholder_id = data.get('placeholder_id')
                                print(f"❌ Placeholder removed: {placeholder_id}")
                                print(f"   Reason: {data.get('reasoning', 'N/A')}")
                            
                            elif chunk_type == 'complete':
                                print("🏁 Stream completed")
                                break
                            
                            elif chunk_type == 'error':
                                error_msg = data.get('content', 'Unknown error')
                                results["errors"].append(error_msg)
                                print(f"❌ Error: {error_msg}")
                                break
                        
                        except json.JSONDecodeError as e:
                            results["errors"].append(f"JSON decode error: {str(e)}")
                            print(f"⚠️ JSON decode error: {str(e)}")
        
        except Exception as e:
            results["errors"].append(f"Request error: {str(e)}")
            print(f"❌ Request error: {str(e)}")
        
        results["streaming_time"] = time.time() - start_time
        
        # Analyze results
        self._analyze_results(test_case, results)
        
        return results
    
    def _analyze_results(self, test_case: Dict[str, Any], results: Dict[str, Any]):
        """Analyze test results and provide feedback."""
        print(f"\n📊 Results Analysis:")
        print(f"   Chunks received: {results['chunks_received']}")
        print(f"   Placeholders created: {results['placeholders_created']}")
        print(f"   Components generated: {results['components_generated']}")
        print(f"   Streaming time: {results['streaming_time']:.2f}s")
        
        # Check expectations
        expected_placeholders = test_case['expected_placeholders']
        expected_components = test_case['expected_components']
        
        # Placeholder validation
        if results['placeholders_created'] == expected_placeholders:
            print(f"✅ Placeholders: Expected {expected_placeholders}, Got {results['placeholders_created']}")
        else:
            print(f"⚠️  Placeholders: Expected {expected_placeholders}, Got {results['placeholders_created']}")
        
        # Component validation
        if len(results['component_types']) == len(expected_components):
            print(f"✅ Components: Expected {len(expected_components)}, Got {len(results['component_types'])}")
        else:
            print(f"⚠️  Components: Expected {len(expected_components)}, Got {len(results['component_types'])}")
        
        # Component type validation
        for expected_type in expected_components:
            if expected_type in results['component_types']:
                print(f"✅ Component type '{expected_type}' detected correctly")
            else:
                print(f"❌ Component type '{expected_type}' not detected")
        
        # Error reporting
        if results['errors']:
            print(f"❌ Errors encountered:")
            for error in results['errors']:
                print(f"   - {error}")
        else:
            print("✅ No errors encountered")
    
    async def run_all_tests(self) -> List[Dict[str, Any]]:
        """Run all test cases and return results."""
        print("🚀 Starting Streaming Analysis Tests")
        print("=" * 60)
        
        all_results = []
        
        for i, test_case in enumerate(TEST_CASES, 1):
            print(f"\n🧪 Test {i}/{len(TEST_CASES)}: {test_case['name']}")
            print("-" * 40)
            
            result = await self.test_streaming_endpoint(test_case)
            all_results.append(result)
            
            # Brief pause between tests
            await asyncio.sleep(2)
        
        # Summary
        self._print_summary(all_results)
        
        return all_results
    
    def _print_summary(self, all_results: List[Dict[str, Any]]):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📋 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(all_results)
        successful_tests = sum(1 for r in all_results if not r['errors'])
        
        print(f"Total tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")
        
        print(f"\n📊 Component Generation Summary:")
        total_placeholders = sum(r['placeholders_created'] for r in all_results)
        total_components = sum(r['components_generated'] for r in all_results)
        
        print(f"Total placeholders created: {total_placeholders}")
        print(f"Total components generated: {total_components}")
        
        # Component types breakdown
        component_types = {}
        for result in all_results:
            for comp_type in result['component_types']:
                component_types[comp_type] = component_types.get(comp_type, 0) + 1
        
        if component_types:
            print(f"\nComponent types generated:")
            for comp_type, count in component_types.items():
                print(f"  - {comp_type}: {count}")
        
        print("\n🎯 Test completed!")


async def main():
    """Main test function."""
    async with StreamingAnalysisTest() as tester:
        results = await tester.run_all_tests()
        
        # Optional: Save results to file
        with open('streaming_analysis_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to streaming_analysis_test_results.json")


if __name__ == "__main__":
    asyncio.run(main())
