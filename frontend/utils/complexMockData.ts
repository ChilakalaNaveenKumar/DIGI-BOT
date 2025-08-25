// Enhanced mock data for testing AI component analysis
export interface MockResponse {
  id: string
  content: string
  expectedComponents: string[]
  description?: string
}

export const complexMockResponses: MockResponse[] = [
  {
    id: 'comprehensive-business-analysis',
    description: 'Complete business analysis with all component types and edge cases',
    content: `# Comprehensive Business Intelligence Report 2024

Welcome to our most detailed quarterly business analysis. This report covers multiple dimensions of our company performance and strategic insights.

## Executive Summary

Our company has experienced unprecedented growth this quarter, with significant improvements across all key performance indicators. This analysis presents data-driven insights to guide our strategic decisions.

The leadership team is particularly excited about the momentum we've built and the opportunities ahead. Our focus on customer-centric innovation continues to drive results.

## Financial Performance Overview

### Revenue Distribution Analysis

Our total quarterly revenue reached $4.2M, distributed as follows:

- SaaS Products: $1.89M (45%)
- Professional Services: $1.26M (30%) 
- Enterprise Solutions: $840K (20%)
- Training & Support: $210K (5%)

This represents a 23% increase from the previous quarter, with SaaS products showing the strongest growth trajectory. The market demand for our core platform continues to exceed expectations.

### Monthly Revenue Progression

The revenue growth throughout the quarter showed consistent upward momentum:

January generated $1.2M, February achieved $1.35M, March reached $1.65M.

This steady 12-15% month-over-month growth indicates strong market demand and effective sales execution. Our sales team has been instrumental in this success.

### Operating Expenses Analysis

Total operating expenses were $3.1M for the quarter:

- Personnel & Benefits: $1.55M (50%)
- Sales & Marketing: $620K (20%)
- Technology Infrastructure: $465K (15%)
- Research & Development: $310K (10%)
- Administrative Costs: $155K (5%)

Our expense management has improved significantly, with an 8% reduction in operational costs compared to last quarter.

## Market Analysis & Competitive Position

Understanding our market position is crucial for strategic planning. We've conducted extensive research to benchmark our performance.

### Market Share Distribution

Current market analysis shows our competitive position:

We hold 18% market share, while CompetitorA leads with 28%, CompetitorB has 22%, CompetitorC maintains 15%, and other players collectively hold 17% of the market.

The competitive landscape remains dynamic, with opportunities for growth through differentiation and superior customer experience.

### Customer Acquisition Performance

New customer acquisition this quarter totaled 1,840 customers through various channels:

- Organic Search: 736 customers (40%)
- Paid Advertising: 552 customers (30%)
- Partner Referrals: 368 customers (20%)
- Social Media: 184 customers (10%)

Our organic search performance has improved by 35% compared to last quarter, indicating strong SEO and content marketing effectiveness.

## Product Performance Analytics

Product performance metrics provide valuable insights into user behavior and market preferences.

### Product Line Profitability

Different product lines showed varying profitability margins:

Enterprise Suite achieved 42% profit margin, Professional Tools maintained 35% margin, Starter Package delivered 28% margin, and Add-on Services reached 55% margin.

The high margin on Add-on Services suggests opportunities for expanding our service offerings.

### Feature Adoption Rates

User engagement with key features varies significantly:

Dashboard Analytics: 89% adoption, Automated Reports: 76% adoption, API Integration: 62% adoption, Mobile App: 45% adoption, Advanced Customization: 23% adoption.

These metrics guide our product development priorities and help identify areas for improvement.

## Human Resources & Team Analytics

Our people are our greatest asset. This section analyzes team performance and satisfaction metrics.

### Employee Satisfaction Results

Our quarterly employee survey (428 responses, 94% response rate) revealed:

- Extremely Satisfied: 38% (163 employees)
- Very Satisfied: 31% (133 employees)
- Satisfied: 19% (81 employees)
- Neutral: 8% (34 employees)
- Dissatisfied: 4% (17 employees)

Overall satisfaction score improved from 7.2 to 8.1 on a 10-point scale, reflecting our ongoing investment in workplace culture.

### Department Performance Ratings

Performance scores by department show consistent excellence across teams:

Engineering scored 8.7, Product Management achieved 8.4, Sales reached 8.2, Marketing scored 7.9, Customer Success achieved 8.6, HR scored 8.1, and Finance reached 7.8.

These scores reflect the dedication and expertise of our team members across all functions.

### Team Growth Trajectory

Our headcount evolution throughout the year demonstrates strategic expansion:

January: 45 employees, February: 52 employees, March: 58 employees, April: 65 employees, May: 73 employees, June: 82 employees, July: 89 employees, August: 97 employees, September: 106 employees, October: 115 employees, November: 124 employees, December: 135 employees.

This represents a 200% growth in team size, with strategic hires across all departments.

## Customer Success Metrics

Customer satisfaction and retention are key indicators of long-term business health.

### Customer Retention by Tier

Customer retention rates by subscription tier show strong performance:

Enterprise customers: 96% retention, Professional: 89% retention, Standard: 82% retention, Basic: 74% retention.

The correlation between tier level and retention suggests the value proposition strengthens with higher-tier offerings.

### Support Performance Analysis

Our customer support team handled 2,847 tickets this quarter:

Critical issues: 142 tickets (5%) - avg resolution 2.1 hours
High priority: 569 tickets (20%) - avg resolution 8.3 hours  
Medium priority: 1,423 tickets (50%) - avg resolution 24.7 hours
Low priority: 713 tickets (25%) - avg resolution 72.5 hours

Resolution times improved by 25% compared to last quarter, reflecting process improvements and team training.

### Net Promoter Score Analysis

NPS survey results from 1,200 customer responses:

Promoters (9-10): 54% (648 customers)
Passives (7-8): 32% (384 customers)
Detractors (0-6): 14% (168 customers)

Our NPS score of 40 places us in the "Good" category, with significant improvement potential.

## Technology & Infrastructure

Our technology platform forms the foundation of our service delivery and customer experience.

### System Performance Overview

Application uptime maintained 99.7% availability, with average response times of 145ms for API calls and 2.1 seconds for page loads. Our infrastructure successfully handled peak loads of 15,000 concurrent users.

These metrics demonstrate the reliability and scalability of our technical architecture.

### Security Incident Summary

Security monitoring detected and resolved 23 minor incidents, 3 medium-severity issues, and 0 critical breaches. All incidents were resolved within SLA requirements.

Our proactive security approach continues to protect customer data and maintain trust.

## Regional Performance Analysis

Geographic performance analysis reveals opportunities for expansion and optimization.

### Sales by Region

Geographic revenue distribution shows:

North America: $1.89M (45%), Europe: $1.26M (30%), Asia-Pacific: $840K (20%), Latin America: $210K (5%).

North America continues to be our strongest market, though Asia-Pacific shows the highest growth rate at 67% year-over-year.

### Market Penetration Analysis

Regional market penetration analysis reveals growth opportunities:

North America: 12% penetration, Europe: 8% penetration, Asia-Pacific: 3% penetration, Latin America: 1% penetration.

Significant opportunities exist for expansion, particularly in emerging markets.

## Strategic Recommendations

Based on this comprehensive analysis, we recommend focusing on key strategic initiatives that will drive continued growth and market leadership.

Our recommendations include:

1. **Product Development**: Invest in API integration improvements and mobile app enhancement
2. **Market Expansion**: Accelerate Asia-Pacific growth initiatives  
3. **Customer Success**: Implement advanced retention programs for Basic tier customers
4. **Operational Efficiency**: Optimize support ticket routing to improve resolution times
5. **Team Development**: Continue strategic hiring in high-performing departments

## Conclusion

This quarter demonstrates strong execution across all business dimensions. Our data-driven approach continues to deliver measurable results, positioning us well for sustained growth.

The combination of strong financial performance, improving customer satisfaction, and strategic team expansion creates a solid foundation for achieving our ambitious 2025 targets.

We remain committed to our mission of delivering exceptional value to customers while building a sustainable, profitable business.`,
    expectedComponents: [
      'pie-chart', // Revenue distribution
      'line-chart', // Monthly revenue progression  
      'pie-chart', // Operating expenses
      'pie-chart', // Market share
      'pie-chart', // Customer acquisition channels
      'bar-chart', // Product profitability
      'bar-chart', // Feature usage statistics
      'pie-chart', // Employee satisfaction
      'bar-chart', // Department performance
      'line-chart', // Team growth
      'bar-chart', // Customer retention
      'data-table', // Support tickets
      'pie-chart', // NPS distribution
      'pie-chart', // Regional sales
      'bar-chart' // Market penetration
    ]
  },
  {
    id: 'social-media-analysis',
    description: 'Social media platform usage analysis with multiple data types',
    content: `# Social Media Platform Analysis 2024

Our latest survey reveals interesting usage patterns across different platforms:

**Platform Preferences:**
Instagram leads with 45% user preference, followed by TikTok at 30%, Facebook at 20%, and Twitter at 5%. This represents a significant shift from last year's data.

**Age Demographics:**
The 18-25 age group comprises 60% of our respondents, 26-35 makes up 25%, 36-45 represents 10%, and over 45 accounts for 5%.

**Daily Usage Patterns:**
Average daily usage shows Instagram at 2.5 hours, TikTok at 2.1 hours, Facebook at 1.2 hours, and Twitter at 0.8 hours per day.

**Engagement Metrics:**
Post interaction rates vary significantly: Instagram stories have 45% engagement, TikTok videos achieve 38%, Facebook posts get 15%, and Twitter tweets receive 12% engagement rates.

**Geographic Distribution:**
Urban users represent 65% of our sample, suburban users 25%, and rural users 10%. Usage patterns differ significantly across these demographics.

**Content Preference Analysis:**
Video content is preferred by 70% of users, image posts by 20%, text-only content by 8%, and live streams by 2%.`,
    expectedComponents: [
      'pie-chart', // Platform preferences
      'pie-chart', // Age demographics  
      'bar-chart', // Daily usage patterns
      'bar-chart', // Engagement metrics
      'pie-chart', // Geographic distribution
      'pie-chart' // Content preferences
    ]
  },
  
  {
    id: 'financial-quarterly-report',
    description: 'Comprehensive quarterly financial report with revenue and cost breakdowns',
    content: `# Q4 2024 Financial Performance

## Revenue Breakdown
Our total revenue reached $2.4M this quarter, with the following distribution:
- Product sales: $1.2M (50%)
- Services: $720K (30%) 
- Subscriptions: $360K (15%)
- Other: $120K (5%)

## Monthly Performance
January started strong at $650K, February maintained momentum at $720K, March saw exceptional growth reaching $950K, and December closed at $1.1M.

## Cost Analysis
Operating expenses totaled $1.8M:
- Personnel: $900K (50%)
- Marketing: $360K (20%)
- Infrastructure: $270K (15%)
- R&D: $180K (10%) 
- Other: $90K (5%)

## Profit Margins by Product Line
Premium products achieved 35% margin, Standard products maintained 25% margin, Basic tier delivered 15% margin, and Enterprise solutions reached 45% margin.

## Customer Acquisition Metrics
We acquired 1,200 new customers this quarter through various channels:
- Organic search: 480 customers (40%)
- Paid advertising: 360 customers (30%)
- Referrals: 240 customers (20%)
- Social media: 120 customers (10%)`,
    expectedComponents: [
      'pie-chart', // Revenue breakdown
      'line-chart', // Monthly performance
      'pie-chart', // Cost analysis
      'bar-chart', // Profit margins
      'pie-chart' // Customer acquisition
    ]
  },

  {
    id: 'product-comparison-table',
    description: 'Detailed product comparison with specifications and pricing',
    content: `# Product Comparison Analysis

## Smartphone Market Analysis

We analyzed the top smartphones in the market based on specifications, pricing, and user ratings:

**iPhone 15 Pro** costs $999, features 256GB storage, 4.8/5 user rating, 48MP camera, and iOS 17 operating system.

**Samsung Galaxy S24 Ultra** is priced at $1,199, offers 512GB storage, 4.6/5 user rating, 200MP camera, and Android 14.

**Google Pixel 8 Pro** retails for $899, includes 128GB storage, 4.5/5 user rating, 50MP camera, and Android 14.

**OnePlus 12** costs $799, provides 256GB storage, 4.4/5 user rating, 64MP camera, and OxygenOS 14.

**Xiaomi 14 Ultra** is available for $749, contains 512GB storage, 4.3/5 user rating, 50MP camera, and MIUI 15.

## Performance Benchmarks
Processing power tests show iPhone 15 Pro scoring 1,750 points, Galaxy S24 Ultra achieving 1,680 points, Pixel 8 Pro reaching 1,420 points, OnePlus 12 scoring 1,380 points, and Xiaomi 14 Ultra getting 1,360 points.`,
    expectedComponents: [
      'data-table', // Product specifications
      'bar-chart' // Performance benchmarks
    ]
  },

  {
    id: 'time-series-growth',
    description: 'Company growth metrics over time with multiple data series',
    content: `# Company Growth Metrics 2024

## Website Traffic Evolution
Our website traffic has shown remarkable growth throughout the year:

January started with 25,000 monthly visitors, February increased to 32,000, March reached 41,000, April hit 55,000, May achieved 68,000, June peaked at 82,000, July maintained 79,000, August reached 95,000, September hit 108,000, October achieved 125,000, November reached 142,000, and December peaked at 158,000 visitors.

## Revenue Growth Trend
Monthly recurring revenue followed a similar trajectory:
January: $45,000, February: $52,000, March: $61,000, April: $73,000, May: $86,000, June: $102,000, July: $118,000, August: $135,000, September: $154,000, October: $175,000, November: $198,000, December: $225,000.

## Team Expansion
Our team grew from 12 employees in January to 45 employees by December, with key hires in engineering, sales, and customer success departments.

## Customer Base Growth
We started the year with 450 active customers and ended with 2,100 active customers, representing a 367% growth rate.`,
    expectedComponents: [
      'line-chart', // Website traffic
      'line-chart', // Revenue growth
      'line-chart' // Team/customer growth
    ]
  },

  {
    id: 'survey-results-mixed',
    description: 'Employee satisfaction survey with various question types',
    content: `# Employee Satisfaction Survey Results

## Overall Satisfaction Rating
Our annual employee satisfaction survey received 340 responses (85% response rate):

**Satisfaction Levels:**
Very Satisfied: 45% (153 employees)
Satisfied: 35% (119 employees)  
Neutral: 12% (41 employees)
Dissatisfied: 6% (20 employees)
Very Dissatisfied: 2% (7 employees)

## Work-Life Balance Scores
Departments scored differently on work-life balance (1-10 scale):
Engineering: 7.8, Marketing: 8.2, Sales: 6.9, HR: 8.5, Finance: 7.1, Operations: 7.4, Customer Success: 8.0

## Remote Work Preferences
When asked about work arrangements:
- Fully remote: 40% prefer
- Hybrid (2-3 days office): 45% prefer
- Fully in-office: 15% prefer

## Benefits Utilization
Health insurance: 95% enrolled, Dental: 78% enrolled, Vision: 65% enrolled, 401k: 82% enrolled, Flexible PTO: 88% using, Professional development: 34% using.

## Training Program Effectiveness
Participants rated training programs: Leadership training 8.7/10, Technical skills 9.1/10, Communication skills 7.9/10, Project management 8.3/10.`,
    expectedComponents: [
      'pie-chart', // Overall satisfaction
      'bar-chart', // Department scores
      'pie-chart', // Work preferences
      'bar-chart', // Benefits utilization
      'bar-chart' // Training ratings
    ]
  },

  {
    id: 'simple-percentage-data',
    description: 'Simple percentage breakdown for basic pie chart testing',
    content: `# Market Share Analysis

The latest market research shows clear leaders in the cloud storage industry:

Google Drive dominates with 35% market share, followed by Dropbox at 25%, Microsoft OneDrive at 20%, Apple iCloud at 15%, and other providers collectively holding 5% of the market.

This distribution has remained relatively stable over the past quarter, with Google Drive maintaining its leadership position.`,
    expectedComponents: [
      'pie-chart' // Market share
    ]
  },

  {
    id: 'quarterly-comparison',
    description: 'Simple quarterly comparison for bar chart testing',
    content: `# Sales Performance by Quarter

Our sales team delivered strong results throughout 2024:

Q1 2024 achieved $125,000 in revenue, Q2 reached $180,000, Q3 hit $220,000, and Q4 is projected to reach $195,000. This represents consistent growth with Q3 being our strongest quarter.

The performance exceeded our initial projections by 15% overall.`,
    expectedComponents: [
      'bar-chart' // Quarterly sales
    ]
  },

  {
    id: 'no-data-content',
    description: 'Content without data patterns to test negative cases',
    content: `# Company Culture and Values

## Our Mission
We believe in creating technology that empowers people to achieve their goals. Our mission is to build innovative solutions that make complex tasks simple and accessible to everyone.

## Core Values
**Innovation**: We constantly push boundaries and explore new possibilities.
**Integrity**: We operate with honesty and transparency in all our interactions.
**Collaboration**: We believe diverse perspectives create better outcomes.
**Excellence**: We strive for the highest quality in everything we deliver.

## Team Philosophy
Our team operates on the principle that great products come from great people. We foster an environment where creativity thrives, mistakes are learning opportunities, and everyone's voice matters.

## Future Vision
We envision a world where technology seamlessly integrates into daily life, making people more productive, connected, and fulfilled. Our role is to bridge the gap between complex capabilities and user-friendly experiences.`,
    expectedComponents: [] // No data patterns, should not generate components
  }
]

// Helper function to get random mock response
export const getRandomMockResponse = (): MockResponse => {
  const randomIndex = Math.floor(Math.random() * complexMockResponses.length)
  const response = complexMockResponses[randomIndex]
  if (!response) {
    throw new Error('No mock responses available')
  }
  return response
}

// Helper function to get mock response by ID
export const getMockResponseById = (id: string): MockResponse => {
  const response = complexMockResponses.find(response => response.id === id)
  if (!response) {
    throw new Error(`Mock response with id '${id}' not found`)
  }
  return response
}

// Get all mock response IDs for testing
export const getAllMockIds = (): string[] => {
  return complexMockResponses.map(response => response.id)
}
