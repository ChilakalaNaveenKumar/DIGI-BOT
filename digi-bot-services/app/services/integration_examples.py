"""
Integration Examples: Vision Models + Chart Matcher

This module demonstrates how to combine VisionAnalyzerClient and ChartMatcherClient
for powerful image analysis and chart recreation workflows.
"""

import asyncio
import base64
import os
from typing import Dict, List, Optional, Any
from .vision_models import VisionAnalyzerClient, ImageGeneratorClient
from .chart_matcher import ChartMatcherClient, VectorStoreManager


class VisionChartIntegration:
    """Integration service combining vision analysis with chart matching"""
    
    def __init__(self):
        self.vision_analyzer = VisionAnalyzerClient(model="gpt-4o")
        self.chart_matcher = ChartMatcherClient()
        self.image_generator = ImageGeneratorClient()
        self.vector_manager = VectorStoreManager()
    
    async def initialize(self):
        """Initialize all services"""
        print("🚀 Initializing Vision-Chart Integration...")
        
        await self.vision_analyzer.initialize()
        await self.chart_matcher.initialize()
        await self.image_generator.initialize()
        await self.vector_manager.initialize()
        
        print("✅ All services initialized")
    
    async def analyze_chart_image_and_recreate(
        self, 
        image_url: str, 
        analysis_prompt: str = "Analyze this chart and extract all data points, labels, and chart type."
    ) -> Dict[str, Any]:
        """
        Complete workflow: Analyze chart image → Extract data → Find matching format → Provide recreation code
        """
        print(f"📸 Analyzing chart image: {image_url}")
        
        # Step 1: Analyze the image
        analysis_result = ""
        async for event in self.vision_analyzer.analyze_url(image_url, analysis_prompt):
            if event["type"] == "content":
                analysis_result += event["content"]
            elif event["type"] == "error":
                return {"error": f"Vision analysis failed: {event['error']}"}
            elif event["type"] == "completion":
                break
        
        print(f"🔍 Vision analysis complete")
        
        # Step 2: Extract chart type and data intent from analysis
        chart_intent_query = f"Based on this analysis, what type of chart should be created: {analysis_result[:500]}"
        
        # Step 3: Find matching chart format
        format_result = await self.chart_matcher.quick_match(chart_intent_query)
        
        if not self.chart_matcher.has_match(format_result):
            return {
                "analysis": analysis_result,
                "chart_format": None,
                "error": "No matching chart format found"
            }
        
        return {
            "analysis": analysis_result,
            "chart_format": format_result,
            "success": True
        }
    
    async def create_chart_from_description(
        self, 
        description: str,
        generate_image: bool = False
    ) -> Dict[str, Any]:
        """
        Create chart format from text description, optionally generate visual
        """
        print(f"📝 Creating chart from description: {description[:100]}...")
        
        # Step 1: Find appropriate chart format
        format_result = await self.chart_matcher.quick_match(description)
        
        if not self.chart_matcher.has_match(format_result):
            return {"error": "No matching chart format found for description"}
        
        result = {
            "description": description,
            "chart_format": format_result,
            "success": True
        }
        
        # Step 2: Optionally generate image visualization
        if generate_image:
            print("🎨 Generating chart image...")
            try:
                images = await self.image_generator.generate(
                    f"Create a professional {description}, clean design, business style",
                    size="1024x1024",
                    n=1
                )
                result["generated_image"] = images[0]["b64"]
                result["image_prompt"] = images[0]["revised_prompt"]
                print("✅ Chart image generated")
            except Exception as e:
                result["image_error"] = str(e)
                print(f"❌ Image generation failed: {e}")
        
        return result
    
    async def batch_chart_analysis(
        self, 
        image_urls: List[str],
        analysis_prompt: str = "Describe this chart type and extract key data points."
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple chart images in batch
        """
        print(f"📊 Batch analyzing {len(image_urls)} chart images...")
        
        results = []
        for i, url in enumerate(image_urls, 1):
            print(f"[{i}/{len(image_urls)}] Processing: {url}")
            
            try:
                result = await self.analyze_chart_image_and_recreate(url, analysis_prompt)
                result["image_url"] = url
                result["index"] = i
                results.append(result)
                
                if result.get("success"):
                    print(f"  ✅ Successfully analyzed")
                else:
                    print(f"  ❌ Analysis failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                results.append({
                    "image_url": url,
                    "index": i,
                    "error": str(e)
                })
                print(f"  ❌ Exception: {e}")
        
        successful = sum(1 for r in results if r.get("success"))
        print(f"📈 Batch complete: {successful}/{len(image_urls)} successful")
        
        return results


async def example_chart_image_analysis():
    """Example: Analyze chart images and recreate them"""
    print("=== Chart Image Analysis Example ===")
    
    integration = VisionChartIntegration()
    await integration.initialize()
    
    # Example chart image URLs (replace with actual URLs)
    test_images = [
        "https://example.com/sales-bar-chart.png",
        "https://example.com/market-share-pie.png",
        "https://example.com/revenue-line-chart.png"
    ]
    
    for image_url in test_images:
        print(f"\n📸 Analyzing: {image_url}")
        
        result = await integration.analyze_chart_image_and_recreate(
            image_url,
            "Analyze this chart. Extract the chart type, all data points, labels, and title. Be specific about values."
        )
        
        if result.get("success"):
            print("✅ Analysis successful!")
            print(f"📋 Chart format found: {result['chart_format'][:200]}...")
        else:
            print(f"❌ Analysis failed: {result.get('error')}")


async def example_description_to_chart():
    """Example: Create charts from text descriptions"""
    print("\n=== Description to Chart Example ===")
    
    integration = VisionChartIntegration()
    await integration.initialize()
    
    descriptions = [
        "Show quarterly sales performance as a bar chart with Q1: $100k, Q2: $150k, Q3: $200k, Q4: $180k",
        "Create a pie chart showing browser market share: Chrome 65%, Safari 20%, Firefox 10%, Edge 5%",
        "Display monthly revenue trends as a line chart from Jan to Dec 2024",
        "Make a data table with employee performance metrics including name, department, and rating"
    ]
    
    for desc in descriptions:
        print(f"\n📝 Description: {desc}")
        
        result = await integration.create_chart_from_description(desc, generate_image=True)
        
        if result.get("success"):
            print("✅ Chart format created!")
            print(f"📋 Format: {result['chart_format'][:150]}...")
            
            if result.get("generated_image"):
                print("🎨 Image generated successfully")
                # In real usage, you'd save the base64 image
                # with open(f"chart_{i}.png", "wb") as f:
                #     f.write(base64.b64decode(result["generated_image"]))
            
        else:
            print(f"❌ Failed: {result.get('error')}")


async def example_file_based_analysis():
    """Example: Analyze uploaded chart files"""
    print("\n=== File-Based Chart Analysis ===")
    
    integration = VisionChartIntegration()
    await integration.initialize()
    
    # Simulate uploading a local chart image
    # In real usage, you'd upload actual files
    print("📤 Simulating file upload and analysis...")
    
    # This would be actual file upload in real usage:
    # from openai import AsyncOpenAI
    # client = AsyncOpenAI()
    # with open("chart_image.png", "rb") as f:
    #     uploaded_file = await client.files.create(file=f, purpose="vision")
    # 
    # analysis_result = ""
    # async for event in integration.vision_analyzer.analyze_file(
    #     uploaded_file.id,
    #     "Extract all data from this chart and identify the chart type"
    # ):
    #     if event["type"] == "content":
    #         analysis_result += event["content"]
    
    print("✅ File-based analysis workflow ready")


async def example_chart_format_validation():
    """Example: Validate and enhance chart formats"""
    print("\n=== Chart Format Validation ===")
    
    integration = VisionChartIntegration()
    await integration.initialize()
    
    # Test various format queries
    test_queries = [
        "Create bar chart for sales data",
        "Make pie chart showing percentages", 
        "Display line chart with time series",
        "Show data table with metrics",
        "Random text without chart intent"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        
        result = await integration.chart_matcher.quick_match(query)
        has_match = integration.chart_matcher.has_match(result)
        
        print(f"  {'✅' if has_match else '❌'} {'Valid format found' if has_match else 'No format match'}")
        
        if has_match:
            # Validate the format structure
            is_valid_format = any(marker in result for marker in [":::pie-chart", ":::bar-chart", ":::line-chart", ":::data-table"])
            print(f"  📋 Format structure: {'Valid' if is_valid_format else 'Invalid'}")


async def example_end_to_end_workflow():
    """Complete end-to-end example workflow"""
    print("\n=== End-to-End Workflow Example ===")
    
    integration = VisionChartIntegration()
    await integration.initialize()
    
    # Scenario: User uploads chart image, wants to recreate it with different data
    print("📋 Scenario: Recreate chart with new data")
    
    # Step 1: Analyze existing chart (simulated)
    original_analysis = """
    This is a bar chart showing quarterly sales:
    Q1: $125,000
    Q2: $150,000  
    Q3: $175,000
    Q4: $200,000
    Title: Quarterly Sales Performance 2024
    """
    
    print(f"📸 Original chart analysis: {original_analysis}")
    
    # Step 2: Get format for similar chart
    new_data_query = "Create a bar chart for quarterly sales with different values"
    format_result = await integration.chart_matcher.quick_match(new_data_query)
    
    if integration.chart_matcher.has_match(format_result):
        print("✅ Found matching format template")
        
        # Step 3: Generate new chart image (optional)
        print("🎨 Generating updated chart visualization...")
        try:
            new_chart_images = await integration.image_generator.generate(
                "Professional bar chart showing quarterly sales performance, clean business style, labeled axes",
                size="1024x1024"
            )
            print("✅ New chart image generated")
            
            # In real usage, save the image:
            # with open("updated_chart.png", "wb") as f:
            #     f.write(base64.b64decode(new_chart_images[0]["b64"]))
            
        except Exception as e:
            print(f"❌ Image generation failed: {e}")
        
        print("🎉 End-to-end workflow complete!")
        
    else:
        print("❌ No matching format found")


# Utility functions for common integration patterns
async def quick_chart_recreation(image_url: str) -> Optional[str]:
    """Utility: Quick chart format extraction from image URL"""
    integration = VisionChartIntegration()
    await integration.initialize()
    
    result = await integration.analyze_chart_image_and_recreate(image_url)
    return result.get("chart_format") if result.get("success") else None


async def generate_chart_variations(base_description: str, count: int = 3) -> List[str]:
    """Utility: Generate multiple chart format variations"""
    integration = VisionChartIntegration()
    await integration.initialize()
    
    variations = []
    chart_types = ["bar chart", "pie chart", "line chart", "data table"]
    
    for chart_type in chart_types[:count]:
        query = f"Create a {chart_type} for: {base_description}"
        result = await integration.chart_matcher.quick_match(query)
        
        if integration.chart_matcher.has_match(result):
            variations.append(result)
    
    return variations


# Main example runner
async def run_integration_examples():
    """Run all integration examples"""
    print("🚀 Starting Vision-Chart Integration Examples\n")
    
    try:
        # Run individual examples
        await example_chart_image_analysis()
        await example_description_to_chart()
        await example_file_based_analysis()
        await example_chart_format_validation()
        await example_end_to_end_workflow()
        
        print("\n🎉 All integration examples completed!")
        
    except Exception as e:
        print(f"\n❌ Integration examples failed: {e}")


if __name__ == "__main__":
    asyncio.run(run_integration_examples())
