"""
Usage examples for Vision Models clients.

These examples demonstrate how to use VisionAnalyzerClient and ImageGeneratorClient
in your application.
"""

import asyncio
import base64
from openai import AsyncOpenAI
from .vision_analyzer import VisionAnalyzerClient
from .image_generator import ImageGeneratorClient


async def example_analyze_url():
    """Example: Analyze a URL-based image"""
    analyzer = VisionAnalyzerClient(model="gpt-4o")
    
    async for event in analyzer.analyze_url(
        "https://example.com/photo.jpg",
        prompt="Give me a concise summary and list any safety risks you see."
    ):
        if event["type"] == "content":
            print(event["content"], end="")
        elif event["type"] == "error":
            print(f"Error: {event['error']}")
        elif event["type"] == "completion":
            print("\n--- Analysis complete ---")


async def example_analyze_local_file():
    """Example: Analyze an uploaded local image file"""
    # First upload the file
    client = AsyncOpenAI()
    with open("local_image.png", "rb") as f:
        uploaded_file = await client.files.create(file=f, purpose="vision")
    
    # Then analyze it
    analyzer = VisionAnalyzerClient()
    async for event in analyzer.analyze_file(
        uploaded_file.id, 
        prompt="Extract the table data as CSV."
    ):
        if event["type"] == "content":
            print(event["content"], end="")
        elif event["type"] == "error":
            print(f"Error: {event['error']}")
        elif event["type"] == "completion":
            print("\n--- Analysis complete ---")


async def example_generate_image():
    """Example: Generate an image and save to disk"""
    generator = ImageGeneratorClient(model="gpt-image-1")
    
    images = await generator.generate(
        "A cozy reading nook with a big window and plants, watercolor style",
        size="1024x1024",
        background="transparent",  # omit this if your account/model doesn't support it
        n=1
    )
    
    # Save the first generated image
    b64_data = images[0]["b64"]
    with open("output.png", "wb") as f:
        f.write(base64.b64decode(b64_data))
    
    print(f"Generated image saved as output.png")
    if images[0]["revised_prompt"]:
        print(f"Revised prompt: {images[0]['revised_prompt']}")


async def example_collect_full_analysis():
    """Example: Collect full analysis as a single string (non-streaming)"""
    analyzer = VisionAnalyzerClient(model="gpt-4o")
    
    full_analysis = ""
    async for event in analyzer.analyze_url(
        "https://example.com/chart.png",
        prompt="Describe this chart and extract all data points."
    ):
        if event["type"] == "content":
            full_analysis += event["content"]
        elif event["type"] == "error":
            print(f"Error: {event['error']}")
            return None
    
    return full_analysis


# Helper function to run examples
async def run_examples():
    """Run all examples (modify as needed for your use case)"""
    print("=== Vision Models Examples ===\n")
    
    # Uncomment the examples you want to run:
    # await example_analyze_url()
    # await example_analyze_local_file()
    # await example_generate_image()
    
    analysis = await example_collect_full_analysis()
    if analysis:
        print(f"Full analysis: {analysis}")


if __name__ == "__main__":
    asyncio.run(run_examples())
