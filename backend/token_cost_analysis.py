#!/usr/bin/env python3
"""
Token Cost Analysis for Anthropic Claude 4 Sonnet

This script tests different query complexities to understand:
1. Token consumption (input/output)
2. Cost per request
3. Performance differences between our backend vs direct API

Query Types:
- Small: Simple questions (10-50 tokens)
- Medium: Moderate complexity (100-500 tokens)
- Complex: Large context/reasoning tasks (1000+ tokens)
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

import httpx
import structlog
from app.services.ai_providers.anthropic_provider import AnthropicProvider
from app.core.config import get_settings

logger = structlog.get_logger(__name__)

@dataclass
class TestResult:
    """Container for test results."""
    query_type: str
    query: str
    method: str  # 'backend' or 'direct_api'
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    response_time_ms: float
    response_content: str
    success: bool
    error: Optional[str] = None

class TokenCostAnalyzer:
    """Analyzes token costs for different query types."""
    
    def __init__(self):
        self.settings = get_settings()
        self.anthropic_provider = AnthropicProvider()
        
        # Claude 4 Sonnet pricing (as of 2024)
        # Input: $3.00 per 1M tokens
        # Output: $15.00 per 1M tokens
        self.input_cost_per_token = 3.00 / 1_000_000
        self.output_cost_per_token = 15.00 / 1_000_000
        
        # Test queries of different complexities
        self.test_queries = {
            "small": [
                "What is 2+2?",
                "Hello, how are you?",
                "What day is today?",
                "Define AI in one sentence.",
                "What color is the sky?"
            ],
            "medium": [
                """Explain the concept of machine learning in simple terms. 
                Include the main types of ML and give one example of each type. 
                Keep the explanation under 200 words.""",
                
                """Write a Python function that takes a list of numbers and returns 
                the second largest number. Include error handling and docstring.""",
                
                """Compare and contrast REST APIs vs GraphQL APIs. List 3 advantages 
                and 2 disadvantages of each approach.""",
                
                """Analyze this business scenario: A startup wants to build a food 
                delivery app. What are the key technical components they need and 
                what challenges might they face?""",
                
                """Create a simple project plan for developing a todo list web app 
                using React and Node.js. Include timeline and key milestones."""
            ],
            "complex": [
                f"""You are a senior software architect. Design a comprehensive system 
                architecture for a large-scale e-commerce platform that needs to handle:
                
                - 1 million concurrent users
                - 10,000 transactions per second
                - Global distribution across 5 regions
                - Real-time inventory management
                - Advanced recommendation engine
                - Multi-tenant architecture for vendors
                
                Include:
                1. High-level architecture diagram description
                2. Database design strategy (include specific technologies)
                3. Caching strategy
                4. API design patterns
                5. Security considerations
                6. Monitoring and observability
                7. Deployment strategy
                8. Cost optimization approaches
                
                Provide detailed explanations for each component and justify your choices.
                Consider scalability, reliability, and maintainability.""",
                
                f"""Analyze this complex debugging scenario:
                
                A React application is experiencing random crashes in production but works 
                fine in development. The crashes happen about 2-3 times per day, affecting 
                different users. Stack traces show:
                
                1. Memory leaks in useEffect hooks
                2. Uncaught promise rejections in API calls
                3. State updates on unmounted components
                4. Bundle size issues causing timeouts
                
                Environment details:
                - React 18.2, Next.js 13.4
                - Node.js 18, deployed on Vercel
                - Using Redux Toolkit, React Query
                - Third-party integrations: Stripe, Auth0, SendGrid
                
                Provide:
                1. Step-by-step debugging methodology
                2. Specific code patterns to look for
                3. Tools and techniques for monitoring
                4. Prevention strategies for each issue type
                5. Testing approaches to catch these issues
                6. Performance optimization recommendations
                
                Include code examples where relevant.""",
                
                f"""Design a complete DevOps pipeline for a microservices architecture with:
                
                Services:
                - User service (Node.js)
                - Payment service (Python/FastAPI)  
                - Inventory service (Go)
                - Notification service (Java/Spring)
                - Analytics service (Python/ML)
                
                Requirements:
                - Kubernetes deployment
                - Multi-environment (dev/staging/prod)
                - Automated testing at all levels
                - Security scanning
                - Database migrations
                - Monitoring and alerting
                - Rollback capabilities
                - Blue-green deployments
                
                Provide:
                1. Complete CI/CD pipeline design
                2. Kubernetes manifests structure
                3. Testing strategy for each service type
                4. Security implementation details
                5. Monitoring and logging setup
                6. Disaster recovery plan
                7. Performance benchmarking approach
                
                Include specific tools, configurations, and best practices."""
            ]
        }
    
    async def initialize(self):
        """Initialize the Anthropic provider."""
        try:
            await self.anthropic_provider.initialize()
            logger.info("Anthropic provider initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic provider: {e}")
            raise
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD for given token usage."""
        input_cost = input_tokens * self.input_cost_per_token
        output_cost = output_tokens * self.output_cost_per_token
        return input_cost + output_cost
    
    async def test_backend_method(self, query: str, model: str = "claude-sonnet-4-20250514") -> TestResult:
        """Test using our backend AnthropicProvider."""
        start_time = time.time()
        
        try:
            messages = [
                {"role": "user", "content": query}
            ]
            
            response = await self.anthropic_provider.generate_completion(
                messages=messages,
                model=model,
                max_tokens=4096,
                temperature=0.7
            )
            
            response_time = (time.time() - start_time) * 1000
            
            # Extract token usage from response
            input_tokens = 0
            output_tokens = 0
            response_content = ""
            
            if isinstance(response, dict):
                # Handle Anthropic API response format
                if 'usage' in response:
                    input_tokens = response['usage'].get('input_tokens', 0)
                    output_tokens = response['usage'].get('output_tokens', 0)
                
                if 'content' in response and response['content']:
                    if isinstance(response['content'], list) and len(response['content']) > 0:
                        response_content = response['content'][0].get('text', '') if isinstance(response['content'][0], dict) else str(response['content'][0])
                    else:
                        response_content = str(response['content'])
            
            total_tokens = input_tokens + output_tokens
            cost = self.calculate_cost(input_tokens, output_tokens)
            
            return TestResult(
                query_type="",  # Will be set by caller
                query=query,
                method="backend",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                cost_usd=cost,
                response_time_ms=response_time,
                response_content=response_content[:200] + "..." if len(response_content) > 200 else response_content,
                success=True
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Backend method failed: {e}")
            
            return TestResult(
                query_type="",
                query=query,
                method="backend",
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                cost_usd=0.0,
                response_time_ms=response_time,
                response_content="",
                success=False,
                error=str(e)
            )
    
    async def test_direct_api(self, query: str, model: str = "claude-sonnet-4-20250514") -> TestResult:
        """Test using direct Anthropic API call."""
        start_time = time.time()
        
        try:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.settings.ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": model,
                "max_tokens": 4096,
                "temperature": 0.7,
                "messages": [
                    {"role": "user", "content": query}
                ]
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
            
            response_time = (time.time() - start_time) * 1000
            
            # Extract token usage and content
            input_tokens = data.get('usage', {}).get('input_tokens', 0)
            output_tokens = data.get('usage', {}).get('output_tokens', 0)
            total_tokens = input_tokens + output_tokens
            cost = self.calculate_cost(input_tokens, output_tokens)
            
            response_content = ""
            if 'content' in data and data['content']:
                if isinstance(data['content'], list) and len(data['content']) > 0:
                    response_content = data['content'][0].get('text', '')
            
            return TestResult(
                query_type="",  # Will be set by caller
                query=query,
                method="direct_api",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                cost_usd=cost,
                response_time_ms=response_time,
                response_content=response_content[:200] + "..." if len(response_content) > 200 else response_content,
                success=True
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Direct API method failed: {e}")
            
            return TestResult(
                query_type="",
                query=query,
                method="direct_api",
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                cost_usd=0.0,
                response_time_ms=response_time,
                response_content="",
                success=False,
                error=str(e)
            )
    
    async def run_comprehensive_test(self) -> Dict[str, List[TestResult]]:
        """Run comprehensive tests across all query types and methods."""
        results = {
            "small": [],
            "medium": [],
            "complex": []
        }
        
        for query_type, queries in self.test_queries.items():
            print(f"\n{'='*60}")
            print(f"Testing {query_type.upper()} queries...")
            print(f"{'='*60}")
            
            for i, query in enumerate(queries, 1):
                print(f"\n--- Query {i}/{len(queries)} ({query_type}) ---")
                print(f"Query: {query[:100]}{'...' if len(query) > 100 else ''}")
                
                # Test backend method
                print("Testing backend method...")
                backend_result = await self.test_backend_method(query)
                backend_result.query_type = query_type
                results[query_type].append(backend_result)
                
                if backend_result.success:
                    print(f"✅ Backend: {backend_result.input_tokens}→{backend_result.output_tokens} tokens, ${backend_result.cost_usd:.6f}, {backend_result.response_time_ms:.0f}ms")
                else:
                    print(f"❌ Backend failed: {backend_result.error}")
                
                # Small delay between requests
                await asyncio.sleep(1)
                
                # Test direct API method
                print("Testing direct API...")
                direct_result = await self.test_direct_api(query)
                direct_result.query_type = query_type
                results[query_type].append(direct_result)
                
                if direct_result.success:
                    print(f"✅ Direct API: {direct_result.input_tokens}→{direct_result.output_tokens} tokens, ${direct_result.cost_usd:.6f}, {direct_result.response_time_ms:.0f}ms")
                else:
                    print(f"❌ Direct API failed: {direct_result.error}")
                
                # Compare results if both succeeded
                if backend_result.success and direct_result.success:
                    token_diff = abs(backend_result.total_tokens - direct_result.total_tokens)
                    cost_diff = abs(backend_result.cost_usd - direct_result.cost_usd)
                    time_diff = backend_result.response_time_ms - direct_result.response_time_ms
                    
                    print(f"📊 Difference: {token_diff} tokens, ${cost_diff:.6f} cost, {time_diff:+.0f}ms time")
                
                # Longer delay between different queries
                await asyncio.sleep(2)
        
        return results
    
    def generate_report(self, results: Dict[str, List[TestResult]]) -> str:
        """Generate a comprehensive analysis report."""
        report = []
        report.append("# Token Cost Analysis Report - Anthropic Claude 4 Sonnet")
        report.append("=" * 70)
        report.append("")
        
        # Summary statistics
        total_tests = sum(len(queries) * 2 for queries in results.values())  # *2 for backend + direct
        successful_tests = sum(sum(1 for r in queries if r.success) for queries in results.values())
        
        report.append(f"**Total Tests:** {total_tests}")
        report.append(f"**Successful Tests:** {successful_tests}")
        report.append(f"**Success Rate:** {successful_tests/total_tests*100:.1f}%")
        report.append("")
        
        # Analysis by query type
        for query_type, test_results in results.items():
            report.append(f"## {query_type.upper()} Queries Analysis")
            report.append("-" * 40)
            
            backend_results = [r for r in test_results if r.method == "backend" and r.success]
            direct_results = [r for r in test_results if r.method == "direct_api" and r.success]
            
            if backend_results:
                avg_backend_input = sum(r.input_tokens for r in backend_results) / len(backend_results)
                avg_backend_output = sum(r.output_tokens for r in backend_results) / len(backend_results)
                avg_backend_cost = sum(r.cost_usd for r in backend_results) / len(backend_results)
                avg_backend_time = sum(r.response_time_ms for r in backend_results) / len(backend_results)
                
                report.append(f"### Backend Method ({len(backend_results)} successful)")
                report.append(f"- Average Input Tokens: {avg_backend_input:.1f}")
                report.append(f"- Average Output Tokens: {avg_backend_output:.1f}")
                report.append(f"- Average Cost: ${avg_backend_cost:.6f}")
                report.append(f"- Average Response Time: {avg_backend_time:.0f}ms")
                report.append("")
            
            if direct_results:
                avg_direct_input = sum(r.input_tokens for r in direct_results) / len(direct_results)
                avg_direct_output = sum(r.output_tokens for r in direct_results) / len(direct_results)
                avg_direct_cost = sum(r.cost_usd for r in direct_results) / len(direct_results)
                avg_direct_time = sum(r.response_time_ms for r in direct_results) / len(direct_results)
                
                report.append(f"### Direct API Method ({len(direct_results)} successful)")
                report.append(f"- Average Input Tokens: {avg_direct_input:.1f}")
                report.append(f"- Average Output Tokens: {avg_direct_output:.1f}")
                report.append(f"- Average Cost: ${avg_direct_cost:.6f}")
                report.append(f"- Average Response Time: {avg_direct_time:.0f}ms")
                report.append("")
            
            # Comparison if both methods have results
            if backend_results and direct_results:
                token_diff = avg_backend_input + avg_backend_output - (avg_direct_input + avg_direct_output)
                cost_diff = avg_backend_cost - avg_direct_cost
                time_diff = avg_backend_time - avg_direct_time
                
                report.append(f"### Comparison (Backend vs Direct API)")
                report.append(f"- Token Difference: {token_diff:+.1f}")
                report.append(f"- Cost Difference: ${cost_diff:+.6f}")
                report.append(f"- Time Difference: {time_diff:+.0f}ms")
                report.append("")
        
        # Detailed results table
        report.append("## Detailed Results")
        report.append("-" * 40)
        report.append("")
        
        for query_type, test_results in results.items():
            report.append(f"### {query_type.upper()} Query Details")
            report.append("")
            report.append("| Method | Input | Output | Total | Cost ($) | Time (ms) | Success |")
            report.append("|--------|--------|--------|--------|----------|-----------|---------|")
            
            for result in test_results:
                status = "✅" if result.success else "❌"
                report.append(f"| {result.method} | {result.input_tokens} | {result.output_tokens} | {result.total_tokens} | {result.cost_usd:.6f} | {result.response_time_ms:.0f} | {status} |")
            
            report.append("")
        
        # Cost projections
        report.append("## Cost Projections")
        report.append("-" * 40)
        report.append("")
        
        all_successful = [r for results_list in results.values() for r in results_list if r.success]
        if all_successful:
            avg_cost = sum(r.cost_usd for r in all_successful) / len(all_successful)
            
            report.append(f"**Average cost per request:** ${avg_cost:.6f}")
            report.append(f"**Cost for 1,000 requests:** ${avg_cost * 1000:.2f}")
            report.append(f"**Cost for 10,000 requests:** ${avg_cost * 10000:.2f}")
            report.append(f"**Cost for 100,000 requests:** ${avg_cost * 100000:.2f}")
            report.append("")
        
        return "\n".join(report)

async def test_direct_api_simple():
    """Simple test of direct API to debug the 404 issue."""
    print("🔍 Testing Direct Anthropic API...")
    settings = get_settings()
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": settings.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    }
    
    # Test with the simplest possible request
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Hi"}]
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print(f"Making request to: https://api.anthropic.com/v1/messages")
            print(f"Headers: {headers}")
            print(f"Payload: {payload}")
            
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Response: {data}")
                return True
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"Response text: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main function to run the analysis."""
    print("🚀 Starting Token Cost Analysis for Anthropic Claude 4 Sonnet")
    print("=" * 70)
    
    # Check if API key is available
    settings = get_settings()
    if not settings.ANTHROPIC_API_KEY or settings.ANTHROPIC_API_KEY == "your-anthropic-api-key-here":
        print("❌ ANTHROPIC_API_KEY not found or not set properly.")
        print("Please set your Anthropic API key in the environment or .env file.")
        return
    
    # First test direct API to debug the issue
    print("\n--- Direct API Test ---")
    api_works = await test_direct_api_simple()
    if not api_works:
        print("❌ Direct API test failed. Cannot proceed with full analysis.")
        return
    
    print("✅ Direct API test successful! Proceeding with full analysis...")
    
    analyzer = TokenCostAnalyzer()
    
    try:
        # Initialize
        await analyzer.initialize()
        
        # Run tests
        results = await analyzer.run_comprehensive_test()
        
        # Generate and save report
        report = analyzer.generate_report(results)
        
        # Save to file
        report_file = "token_cost_analysis_report.md"
        with open(report_file, "w") as f:
            f.write(report)
        
        # Also save raw data as JSON
        json_file = "token_cost_analysis_data.json"
        json_data = {}
        for query_type, test_results in results.items():
            json_data[query_type] = [
                {
                    "query": r.query,
                    "method": r.method,
                    "input_tokens": r.input_tokens,
                    "output_tokens": r.output_tokens,
                    "total_tokens": r.total_tokens,
                    "cost_usd": r.cost_usd,
                    "response_time_ms": r.response_time_ms,
                    "success": r.success,
                    "error": r.error,
                    "response_preview": r.response_content
                }
                for r in test_results
            ]
        
        with open(json_file, "w") as f:
            json.dump(json_data, f, indent=2)
        
        print(f"\n✅ Analysis complete!")
        print(f"📊 Report saved to: {report_file}")
        print(f"📁 Raw data saved to: {json_file}")
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(report.split("## Detailed Results")[0])  # Print summary part
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
