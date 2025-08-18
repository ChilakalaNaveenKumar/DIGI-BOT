// Test script to simulate frontend API call
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

async function testAnalyzeAPI() {
  const apiBase = 'http://localhost:8000/api';
  const url = `${apiBase}/v1/components/analyze`;
  
  const requestData = {
    content: "Show me quarterly sales data: Q1: $100k, Q2: $150k, Q3: $200k, Q4: $180k",
    context: "Test from Node.js script",
    user_preferences: {}
  };
  
  console.log('Testing Analyze API...');
  console.log('URL:', url);
  console.log('Request data:', JSON.stringify(requestData, null, 2));
  
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer dev-token'
      },
      body: JSON.stringify(requestData)
    });
    
    console.log('\n--- Response ---');
    console.log('Status:', response.status);
    console.log('Status Text:', response.statusText);
    console.log('Headers:', Object.fromEntries(response.headers.entries()));
    
    if (!response.ok) {
      const errorText = await response.text();
      console.log('Error response body:', errorText);
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    console.log('\n--- Success Response ---');
    console.log('Data:', JSON.stringify(data, null, 2));
    
  } catch (error) {
    console.error('\n--- Error ---');
    console.error('Error type:', error.constructor.name);
    console.error('Error message:', error.message);
    console.error('Full error:', error);
  }
}

// Run the test
testAnalyzeAPI().then(() => {
  console.log('\nTest completed.');
}).catch(error => {
  console.error('Test failed:', error);
});
