"""
Test Complex Text Understanding - Can AI Extract Data from Meaning?
Test with complex, indirect text to see if AI can find data patterns hidden in context
"""

import asyncio
from dotenv import load_dotenv

load_dotenv()

# Complex, indirect queries - data hidden in meaning and context
COMPLEX_QUERIES = [
    """
Honestly, the weather has been all over the place this quarter, and it’s been tough keeping morale high when every other week someone is out sick. Still, the leadership team insisted that despite distractions, the northern division held its ground and brought in about **45% of total revenue**, though you wouldn’t know it from how casually it was mentioned in passing.

I remember in the last town hall someone said, “Southern is at thirty percent, east at fifteen, west trailing with ten,” but it was in the middle of a long rant about coffee budgets and nobody paid attention. Yet that single statement actually sums up the regional revenue split better than the official chart in the report.

Frontend team was praised for consistency, backend flagged some tech debt, QA mentioned they were understaffed. Later, someone casually dropped that frontend **completed 42 tickets**, backend **37**, QA **29**, but it got lost between complaints about Jira latency and office Wi-Fi outages.

From: HR Dept
To: Finance
Subject: Salary Benchmarks
Hi team, just a quick update — management roles are stable at **\$80,000**, developers hover near **\$72,000**, and design averages **\$65,000**. No action required yet, though whispers suggest competitors are creeping past our numbers. Oh and by the way, lunch catering has been switched back to Tuesdays.

January felt endless, February was shorter but busier, March had its own chaos, and April was basically survival mode. In between all that, user adoption somehow grew from **1,200 in Jan** to **1,500 in Feb**, then **1,900 in Mar** and **2,400 in Apr**. Crazy how those milestones barely made the slide deck while everyone debated office plants.


**@ops:** hey anyone know laptop stock?
**@it:** yeah around 50 left
**@ops:** monitors?
**@it:** lol only 20. keyboards are fine tho, like 70 or so.
**@ceo:** we’re running out of screens before people 🤦

According to web performance monitoring, the **average load time was 2.5s**, compared against the **2.0s target**. Not great. Worse, the **bounce rate hit 47%**, while **session duration slid to 3.1 minutes**. Conversion rate, though, stubbornly stayed near **3.9%**. Management spent half the discussion blaming fonts, as if typography was the bottleneck.

A recent market analysis indicated that Instagram retains **45% share**, TikTok has climbed to **30%**, Facebook maintains **15%**, with Twitter and others splitting the remaining **10%**. This was buried three pages into a consultancy PDF right after a glossy stock photo of smiling people in suits.

“So here’s the deal,” said the CFO, “dev needs like forty percent, marketing maybe thirty-five, ops fifteen, and research ten. That’s the split.” Then someone joked about how research never gets enough love, and the transcript even captured people laughing — but the actual budget numbers are still there if you look carefully.

At the end of the report, strangely, there’s a paragraph about consciousness and how maybe our neural networks are like corporate teams, each doing their part without seeing the whole picture. It was filler, but sitting right after the charts, it probably confused anyone trying to extract insights.
"""
]

async def test_complex_understanding():
    """Test if AI can extract data patterns from complex, indirect text"""
    
    print("🧠 Testing Complex Text Understanding")
    print("🎯 Can AI extract data patterns from meaning and context?")
    print("=" * 80)
    
    try:
        from app.services.component_matcher import ComponentMatcherClient, VectorStoreManager
        
        # Initialize
        client = ComponentMatcherClient()
        await client.initialize()
        
        vector_manager = VectorStoreManager()
        await vector_manager.initialize()
        
        print(f"✅ Initialized: {client.model}")
        print()
        
        for i, query in enumerate(COMPLEX_QUERIES, 1):
            print(f"🔍 Test {i}: Complex Text Analysis")
            print("-" * 60)
            print(f"📝 Text: {query[:100]}...")
            print()
            
            try:
                # Get response
                response = await client.quick_match(query, vector_manager)
                
                # Check if it found patterns
                has_match = client.has_match(response)
                
                if has_match:
                    print("✅ DATA PATTERNS FOUND!")
                    print(f"🎯 AI Response: {response[:200]}{'...' if len(response) > 200 else ''}")
                    
                    # Analyze what it extracted
                    if 'chart' in response.lower():
                        print("📊 Extracted: Chart/Visualization data")
                    elif 'table' in response.lower():
                        print("📋 Extracted: Tabular data")
                    elif 'data' in response.lower():
                        print("📈 Extracted: Structured data")
                    
                else:
                    print("❌ NO PATTERNS DETECTED")
                    print("   AI determined no visualizable data in this text")
                
            except Exception as e:
                print(f"❌ Error: {e}")
            
            print()
    
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        import traceback
        traceback.print_exc()

async def test_specific_complex_case():
    """Test one specific complex case in detail"""
    
    print("🔬 Detailed Analysis of Complex Case")
    print("=" * 80)
    
    complex_text = """explain in detail bout data distribution by taking a real dat online"""
    
    print(f"📝 Complex Text:")
    print(f"   {complex_text}")
    print()
    
    try:
        from app.services.component_matcher import ComponentMatcherClient, VectorStoreManager
        
        # Initialize
        client = ComponentMatcherClient()
        await client.initialize()
        
        vector_manager = VectorStoreManager()
        await vector_manager.initialize()
        
        print("📤 Streaming Analysis:")
        full_response = ""
        
        async for event in client.analyze(complex_text, vector_manager):
            if event["type"] == "content":
                content = event["content"]
                full_response += content
                print(f"   {content}", end="", flush=True)
            elif event["type"] == "error":
                print(f"\n❌ Error: {event['error']}")
            elif event["type"] == "completion":
                print(f"\n✅ Completed: {event['finish_reason']}")
        
        print(f"\n🎯 Final Analysis: {full_response}")
        has_match = client.has_match(full_response)
        print(f"   Match Found: {has_match}")
        
        if has_match:
            print(f"   🧠 AI successfully extracted data patterns from narrative text!")
            print(f"   📊 Should show: North 45%, South 30%, East 15%, West 10%")
        else:
            print(f"   🤔 AI didn't recognize the data pattern in the story")
    
    except Exception as e:
        print(f"❌ Detailed test failed: {e}")

async def main():
    """Run complex understanding tests"""
    
    print("🚀 Starting Complex Text Understanding Tests")
    print("🎯 Goal: Test if AI can extract data from meaning, not just direct formats")
    print()
    
    # Test 1: Multiple complex queries
    await test_complex_understanding()
    
    print("\n" + "=" * 80)
    
    # Test 2: Detailed analysis of one case
    await test_specific_complex_case()
    
    print("\n" + "=" * 80)
    print("📊 Understanding Test Summary:")
    print("🧠 AI should extract data patterns from:")
    print("   📈 Narrative descriptions of performance")
    print("   💬 Casual conversations with numbers")
    print("   📧 Email discussions with data")
    print("   📋 Meeting notes with metrics")
    print("   🎯 Any text containing implicit data relationships")
    print()
    print("❌ AI should ignore:")
    print("   ☁️  Weather discussions")
    print("   🤔 Abstract philosophical topics")
    print("   📚 General narrative without data")
    
    print("\n✅ Complex Understanding Test Complete!")

if __name__ == "__main__":
    asyncio.run(main())

