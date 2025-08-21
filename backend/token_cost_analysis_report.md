# Token Cost Analysis Report - Anthropic Claude 4 Sonnet
======================================================================

**Total Tests:** 52
**Successful Tests:** 18
**Success Rate:** 34.6%

## SMALL Queries Analysis
----------------------------------------
### Backend Method (4 successful)
- Average Input Tokens: 13.0
- Average Output Tokens: 47.2
- Average Cost: $0.000748
- Average Response Time: 3210ms

### Direct API Method (4 successful)
- Average Input Tokens: 13.0
- Average Output Tokens: 32.5
- Average Cost: $0.000526
- Average Response Time: 1841ms

### Comparison (Backend vs Direct API)
- Token Difference: +14.8
- Cost Difference: $+0.000221
- Time Difference: +1369ms

## MEDIUM Queries Analysis
----------------------------------------
### Backend Method (3 successful)
- Average Input Tokens: 41.7
- Average Output Tokens: 722.7
- Average Cost: $0.010965
- Average Response Time: 12271ms

### Direct API Method (5 successful)
- Average Input Tokens: 39.4
- Average Output Tokens: 725.8
- Average Cost: $0.011005
- Average Response Time: 11882ms

### Comparison (Backend vs Direct API)
- Token Difference: -0.9
- Cost Difference: $-0.000040
- Time Difference: +390ms

## COMPLEX Queries Analysis
----------------------------------------
### Backend Method (1 successful)
- Average Input Tokens: 230.0
- Average Output Tokens: 4096.0
- Average Cost: $0.062130
- Average Response Time: 49807ms

### Direct API Method (1 successful)
- Average Input Tokens: 230.0
- Average Output Tokens: 4096.0
- Average Cost: $0.062130
- Average Response Time: 39185ms

### Comparison (Backend vs Direct API)
- Token Difference: +0.0
- Cost Difference: $+0.000000
- Time Difference: +10622ms

## Detailed Results
----------------------------------------

### SMALL Query Details

| Method | Input | Output | Total | Cost ($) | Time (ms) | Success |
|--------|--------|--------|--------|----------|-----------|---------|
| backend | 14 | 13 | 27 | 0.000237 | 3278 | ✅ |
| direct_api | 14 | 13 | 27 | 0.000237 | 2071 | ✅ |
| backend | 13 | 39 | 52 | 0.000624 | 3222 | ✅ |
| direct_api | 13 | 39 | 52 | 0.000624 | 1967 | ✅ |
| backend | 12 | 52 | 64 | 0.000816 | 1890 | ✅ |
| direct_api | 12 | 48 | 60 | 0.000756 | 1867 | ✅ |
| backend | 0 | 0 | 0 | 0.000000 | 11206 | ❌ |
| direct_api | 13 | 30 | 43 | 0.000489 | 1459 | ✅ |
| backend | 13 | 85 | 98 | 0.001314 | 4450 | ✅ |
| direct_api | 0 | 0 | 0 | 0.000000 | 10962 | ❌ |

### MEDIUM Query Details

| Method | Input | Output | Total | Cost ($) | Time (ms) | Success |
|--------|--------|--------|--------|----------|-----------|---------|
| backend | 47 | 279 | 326 | 0.004326 | 9382 | ✅ |
| direct_api | 47 | 266 | 313 | 0.004131 | 7399 | ✅ |
| backend | 34 | 1361 | 1395 | 0.020517 | 17759 | ✅ |
| direct_api | 34 | 1233 | 1267 | 0.018597 | 13847 | ✅ |
| backend | 0 | 0 | 0 | 0.000000 | 3323 | ❌ |
| direct_api | 35 | 404 | 439 | 0.006165 | 7499 | ✅ |
| backend | 44 | 528 | 572 | 0.008052 | 9673 | ✅ |
| direct_api | 44 | 517 | 561 | 0.007887 | 11386 | ✅ |
| backend | 0 | 0 | 0 | 0.000000 | 3325 | ❌ |
| direct_api | 37 | 1209 | 1246 | 0.018246 | 19277 | ✅ |

### COMPLEX Query Details

| Method | Input | Output | Total | Cost ($) | Time (ms) | Success |
|--------|--------|--------|--------|----------|-----------|---------|
| backend | 0 | 0 | 0 | 0.000000 | 12913 | ❌ |
| direct_api | 0 | 0 | 0 | 0.000000 | 3248 | ❌ |
| backend | 0 | 0 | 0 | 0.000000 | 3818 | ❌ |
| direct_api | 0 | 0 | 0 | 0.000000 | 12620 | ❌ |
| backend | 230 | 4096 | 4326 | 0.062130 | 49807 | ✅ |
| direct_api | 230 | 4096 | 4326 | 0.062130 | 39185 | ✅ |

## Cost Projections
----------------------------------------

**Average cost per request:** $0.012071
**Cost for 1,000 requests:** $12.07
**Cost for 10,000 requests:** $120.71
**Cost for 100,000 requests:** $1207.10
