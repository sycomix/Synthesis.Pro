# AI-Related Error Scan Report

**Date:** 2026-02-02
**Scope:** AI API calls, embeddings, rate limiting, error handling
**Status:** ⚠️ POTENTIAL ISSUES FOUND

---

## 🔍 Scan Results

### ✅ **GOOD: Existing Error Handling**

#### 1. **Rate Limiting (Client-Side)**
**Location:** [CommandValidator.cs:186-222](../Runtime/CommandValidator.cs#L186-L222)

**Status:** ✅ **WELL IMPLEMENTED**

```csharp
// Rate limiting per command type
private ValidationResult CheckRateLimit(string commandType)
{
    // Default: 1 req/sec for unknown commands
    // Tracks requests in sliding 1-second window
    // Returns clear error message with wait time
}
```

**Configured Limits:**
- Most commands: Specific limits per type
- Unknown commands: 1 req/sec (conservative default)
- Sliding window implementation (accurate)

---

#### 2. **API Key Validation**
**Locations:**
- [AnthropicAPIClient.cs:122-126](../Runtime/AnthropicAPIClient.cs#L122-L126)
- [SynLinkExtended.cs:78-84](../Runtime/SynLinkExtended.cs#L78-L84)
- [rag_engine.py:102-103](../RAG/rag_engine.py#L102-L103)

**Status:** ✅ **GOOD**

All components check for missing API keys before making calls.

---

#### 3. **JSON Parse Error Handling**
**Location:** [AnthropicAPIClient.cs:211-215](../Runtime/AnthropicAPIClient.cs#L211-L215)

**Status:** ✅ **GOOD**

```csharp
catch (Exception e)
{
    OnError?.Invoke($"Failed to parse response: {e.Message}");
    Debug.LogError($"[AnthropicAPI] Parse error: {e.Message}\nResponse: {responseText}");
}
```

---

### ⚠️ **ISSUES FOUND: Missing Error Handling**

#### 1. **No HTTP Status Code Handling** (MEDIUM PRIORITY)

**Location:** [AnthropicAPIClient.cs:190-222](../Runtime/AnthropicAPIClient.cs#L190-L222)

**Issue:**
The Anthropic API client doesn't specifically handle:
- **HTTP 429** - Rate limit exceeded (too many requests)
- **HTTP 503** - Service unavailable
- **HTTP 500** - Internal server error
- **HTTP 401** - Invalid API key
- **HTTP 400** - Invalid request

**Current Code:**
```csharp
if (webRequest.result == UnityWebRequest.Result.Success)
{
    // Handle success
}
else
{
    // Generic error handling - doesn't check HTTP status code
    string errorMessage = $"API Error: {webRequest.error}\n{webRequest.downloadHandler.text}";
    OnError?.Invoke(errorMessage);
}
```

**Problem:**
- All errors treated the same (no specific handling)
- No retry logic for transient errors (429, 503)
- No special handling for permanent errors (401, 400)
- User gets generic error message

**Recommended Fix:**
```csharp
long httpCode = webRequest.responseCode;

switch (httpCode)
{
    case 429: // Rate limit
        OnError?.Invoke("Rate limit exceeded. Please wait before retrying.");
        // Could implement exponential backoff retry
        break;

    case 503: // Service unavailable
        OnError?.Invoke("Anthropic service temporarily unavailable. Retry in a moment.");
        // Could implement retry with backoff
        break;

    case 401: // Invalid API key
        OnError?.Invoke("Invalid API key. Please check your configuration.");
        break;

    case 400: // Bad request
        OnError?.Invoke($"Invalid request: {webRequest.downloadHandler.text}");
        break;

    default:
        OnError?.Invoke($"API Error ({httpCode}): {webRequest.error}");
        break;
}
```

---

#### 2. **No Retry Logic with Exponential Backoff** (MEDIUM PRIORITY)

**Issue:**
When AI API calls fail due to:
- Temporary network issues
- Rate limiting (429)
- Service unavailable (503)

The system **immediately fails** with no retry attempts.

**Recommended Implementation:**
```csharp
private IEnumerator SendRequestWithRetry(int maxRetries = 3, float baseDelay = 1f)
{
    for (int attempt = 0; attempt < maxRetries; attempt++)
    {
        yield return SendRequestCoroutine();

        // If successful, exit
        if (lastRequestSucceeded) yield break;

        // If permanent error (401, 400), don't retry
        if (IsPermanentError(lastHttpCode)) yield break;

        // Exponential backoff: 1s, 2s, 4s
        float delay = baseDelay * Mathf.Pow(2, attempt);
        Debug.LogWarning($"[AnthropicAPI] Retry {attempt + 1}/{maxRetries} in {delay}s...");
        yield return new WaitForSeconds(delay);
    }

    OnError?.Invoke("Max retries exceeded. Request failed.");
}
```

---

#### 3. **No Request Timeout Configuration** (LOW PRIORITY)

**Issue:**
Unity's `UnityWebRequest` has a default timeout, but it's not explicitly configured.

**Current:** Uses Unity's default (likely 60-120 seconds)

**Recommendation:**
```csharp
webRequest.timeout = 30; // 30 second timeout for AI requests
```

AI requests should fail fast (30s max) rather than hanging indefinitely.

---

#### 4. **No Token Limit Validation** (LOW PRIORITY)

**Location:** [AnthropicAPIClient.cs:167](../Runtime/AnthropicAPIClient.cs#L167)

**Issue:**
The code sets `max_tokens = maxTokens` but doesn't validate against model limits.

**Potential Problem:**
- Claude models have different max token limits
- Sending over the limit returns 400 error
- No client-side validation before sending

**Model Limits:**
- Claude 3.5 Sonnet: 8192 output tokens max
- Claude 3 Opus: 4096 output tokens max
- Claude 3 Haiku: 4096 output tokens max

**Recommended Fix:**
```csharp
private int GetModelMaxTokens(string modelName)
{
    if (modelName.Contains("sonnet")) return 8192;
    if (modelName.Contains("opus")) return 4096;
    if (modelName.Contains("haiku")) return 4096;
    return 4096; // Safe default
}

// In SendRequestCoroutine:
int modelLimit = GetModelMaxTokens(model);
int safeMaxTokens = Mathf.Min(maxTokens, modelLimit);
```

---

#### 5. **No Streaming Error Handling** (MEDIUM PRIORITY)

**Location:** [AnthropicAPIClient.cs:24](../Runtime/AnthropicAPIClient.cs#L24)

**Issue:**
```csharp
[SerializeField] private bool streamResponse = true;
```

Streaming is enabled but **not implemented**. The code doesn't handle:
- Server-Sent Events (SSE) for streaming
- Partial response parsing
- Stream interruption errors

**Current Behavior:**
Even with `streamResponse = true`, the code uses standard request/response (non-streaming).

**Recommendation:**
Either:
1. **Implement proper streaming** with SSE handling
2. **Remove the setting** and document as "TODO"
3. **Default to false** and add warning

---

#### 6. **Chat Handler Has No AI Integration** (INFO)

**Location:** [websocket_server.py:395-397](../Server/websocket_server.py#L395-L397)

**Finding:**
```python
# TODO: Call AI model with context (Phase 3)
# For now, return search results
response = f"Received: {message}\nFound {len(search_results)} relevant context items."
```

**Status:** ℹ️ **DOCUMENTED TODO**

This is intentional (Phase 3 feature). Not an error, but worth noting.

---

#### 7. **OpenAI API Key Loaded from Environment** (SECURITY: ✅ GOOD)

**Location:** [SynLinkExtended.cs:78](../Runtime/SynLinkExtended.cs#L78)

**Finding:**
```csharp
openAIApiKey = System.Environment.GetEnvironmentVariable("OPENAI_API_KEY");
```

**Status:** ✅ **SECURE APPROACH**

Using environment variables instead of hardcoded keys is correct.

**Warning Present:**
```csharp
if (string.IsNullOrEmpty(openAIApiKey))
{
    Debug.LogWarning("[SynLinkExtended] OPENAI_API_KEY environment variable not set.");
}
```

---

#### 8. **No Cost/Usage Tracking** (LOW PRIORITY)

**Issue:**
No tracking of:
- Total tokens used
- Cost estimation
- Request counts per session
- Rate limit budget remaining

**Recommendation:**
Add usage tracking:
```csharp
public class APIUsageTracker
{
    public int TotalRequests { get; private set; }
    public int TotalInputTokens { get; private set; }
    public int TotalOutputTokens { get; private set; }

    public float EstimatedCost =>
        (TotalInputTokens / 1_000_000f) * 3.00f +  // $3 per 1M input
        (TotalOutputTokens / 1_000_000f) * 15.00f; // $15 per 1M output
}
```

---

### 🔐 **Security Scan: API Keys**

#### ✅ **GOOD Practices Found:**

1. **Environment Variables**
   - OpenAI key loaded from environment (SynLinkExtended.cs)
   - Not hardcoded in source

2. **PlayerPrefs Storage**
   - Anthropic key saved in PlayerPrefs (AnthropicAPIClient.cs:233)
   - Allows persistence without source code storage

3. **Warning Messages**
   - Clear warnings when API keys missing
   - User knows features are disabled

#### ⚠️ **SECURITY CONCERNS:**

**PlayerPrefs for API Keys:**
```csharp
apiKey = PlayerPrefs.GetString("Anthropic_API_Key", "");
```

**Issue:**
- PlayerPrefs stored in **plain text** on disk
- Windows: Registry (unencrypted)
- Mac: plist file (unencrypted)
- Linux: ~/.config file (unencrypted)

**Recommendation:**
For production apps, use platform-specific secure storage:
- Windows: `ProtectedData.Protect()`
- Mac/Linux: Keychain/SecretService
- Unity: Consider encrypted PlayerPrefs wrapper

---

## 📊 Summary

| Category | Status | Priority | Count |
|----------|--------|----------|-------|
| **Working Well** | ✅ | - | 7 |
| **Issues Found** | ⚠️ | High | 0 |
| **Issues Found** | ⚠️ | Medium | 3 |
| **Issues Found** | ⚠️ | Low | 3 |
| **Security Notes** | 🔐 | Info | 2 |

---

## 🎯 Recommended Fixes (Priority Order)

### **High Priority:**
None found - critical AI functionality is protected.

### **Medium Priority:**

1. **Add HTTP Status Code Handling** (30 min)
   - File: `AnthropicAPIClient.cs`
   - Add specific handling for 429, 503, 401, 400
   - User-friendly error messages

2. **Implement Retry Logic** (1 hour)
   - File: `AnthropicAPIClient.cs`
   - Exponential backoff for transient errors
   - Max 3 retries with 1s/2s/4s delays

3. **Fix Streaming Setting** (15 min)
   - File: `AnthropicAPIClient.cs`
   - Either implement or default to `false` with TODO

### **Low Priority:**

4. **Add Request Timeout** (5 min)
   - Set explicit 30s timeout

5. **Validate Token Limits** (20 min)
   - Client-side validation against model limits

6. **Add Usage Tracking** (45 min)
   - Track tokens and estimate costs

---

## ✅ What's Already Working Well

1. ✅ **Rate limiting** - Comprehensive client-side rate limiting
2. ✅ **API key validation** - All components check before calling
3. ✅ **JSON error handling** - Parse errors caught and logged
4. ✅ **Security-conscious** - Environment variables for keys
5. ✅ **Error events** - OnError callbacks for UI feedback
6. ✅ **Conversation history** - Maintains context properly
7. ✅ **Parameter validation** - Temperature and token clamping

---

## 🧪 Testing Recommendations

**Test Cases to Add:**

1. **Rate Limit Test**
   - Send 10 requests rapidly
   - Verify rate limit triggers
   - Check error messages

2. **Invalid API Key Test**
   - Use invalid key
   - Verify 401 error handled gracefully
   - Check user-friendly message

3. **Network Timeout Test**
   - Simulate slow connection
   - Verify timeout triggers (after implementing)

4. **Malformed Response Test**
   - Mock invalid JSON response
   - Verify parse error handling

5. **Token Limit Test**
   - Send request with maxTokens > model limit
   - Verify validation (after implementing)

---

## 📝 Conclusion

**Overall Assessment:** ⚠️ **GOOD with Improvements Needed**

The AI error handling is **functional and safe** for development, but would benefit from:
- Better HTTP status code handling
- Retry logic for production reliability
- Explicit timeouts

**Critical Issues:** None
**Production Blockers:** None
**Recommended Improvements:** 6 (3 medium, 3 low priority)

The existing rate limiting and API key validation provide a solid foundation. The recommended improvements would enhance user experience and reliability in production environments.
