# Layer 3 Video Discovery Analysis

## 🔍 **PROBLEM IDENTIFIED**

Based on analysis of the 105 completed workflows, the video discovery is finding:

### ❌ **WRONG URLs Being Captured:**

1. **`https://www.youtube.com/c/n8n-io`**
   - Type: Channel URL (not a video!)
   - Found in: 100+ workflows
   - Cannot extract transcripts: YES
   - Problem: This is n8n's channel link, not embedded videos

2. **`/workflows/2679-ai-powered-youtube-video-summarization/`**
   - Type: Relative URL to another workflow
   - Found in: Multiple workflows
   - Cannot extract transcripts: YES
   - Problem: This is a link to another n8n workflow, not a YouTube video

### ✅ **CORRECT URLs Found:**

1. **`https://youtu.be/laHIzhsz12E`**
   - Type: Actual YouTube video URL
   - Found in: Workflow 6270
   - Transcript extracted: YES (4,339 chars)
   - This is the CORRECT format we want!

---

## 📊 **STATISTICS**

From 105 workflows:
- **127 "videos" found**
- **2 transcripts extracted** (1.6% success rate)
- **~125 false positives** (channel URLs, relative links)

---

## 🎯 **ROOT CAUSE**

The video discovery logic is too broad:

```python
# Current (TOO BROAD):
video_links = await frame.query_selector_all('a[href*="youtube"], a[href*="youtu.be"]')
```

This captures:
- ✅ `https://youtu.be/VIDEO_ID` (GOOD)
- ❌ `https://www.youtube.com/c/n8n-io` (CHANNEL)
- ❌ `https://www.youtube.com/@username` (CHANNEL)
- ❌ `/workflows/...` (RELATIVE LINK)

---

## 💡 **SOLUTION**

### **Fix 1: Filter Video URLs (Immediate)**

Only accept URLs matching actual video patterns:

```python
def is_valid_youtube_video_url(url: str) -> bool:
    """Check if URL is an actual YouTube video (not channel/playlist)"""
    if not url:
        return False
    
    # Must contain video ID patterns
    video_patterns = [
        r'youtube\.com/watch\?v=[\w-]{11}',  # watch?v=VIDEO_ID (11 chars)
        r'youtu\.be/[\w-]{11}',               # youtu.be/VIDEO_ID
        r'youtube\.com/embed/[\w-]{11}',      # embed/VIDEO_ID
    ]
    
    # Must NOT be channel/user/playlist
    invalid_patterns = [
        r'youtube\.com/c/',           # Channel
        r'youtube\.com/@',            # Handle
        r'youtube\.com/user/',        # User
        r'youtube\.com/playlist',     # Playlist
        r'^/',                        # Relative URL
    ]
    
    # Check invalid patterns first
    for pattern in invalid_patterns:
        if re.search(pattern, url):
            return False
    
    # Check valid patterns
    for pattern in video_patterns:
        if re.search(pattern, url):
            return True
    
    return False
```

### **Fix 2: Extract YouTube ID and Validate**

```python
def extract_and_validate_youtube_id(url: str) -> Optional[str]:
    """Extract YouTube ID and validate it's 11 characters"""
    patterns = [
        r'youtube\.com/watch\?v=([\w-]+)',
        r'youtu\.be/([\w-]+)',
        r'youtube\.com/embed/([\w-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            # YouTube video IDs are exactly 11 characters
            if len(video_id) == 11:
                return video_id
    
    return None
```

---

## 🧪 **TESTING PLAN**

1. ✅ Test Playwright on workflow 6270 (has real video)
2. ✅ Test Playwright on workflow 8527 (should have video)
3. ✅ Identify actual video URLs vs false positives
4. ✅ Fix video discovery logic
5. ✅ Re-test on 5 workflows
6. ✅ Validate transcript extraction works
7. ✅ Run full scrape

---

## 📋 **EXPECTED FIXES**

### **Before Fix:**
- 127 "videos" found
- 2 transcripts extracted (1.6%)
- Most are channel URLs or relative links

### **After Fix:**
- ~10-20 actual videos found (per 100 workflows)
- 80%+ transcript extraction rate
- Only valid YouTube video URLs

---

## 🎯 **URLS TO TEST**

Based on user's original examples, these SHOULD have videos:

1. `https://n8n.io/workflows/6270-build-your-first-ai-agent/`
   - Should have: Embedded tutorial video
   - Expected: `https://youtu.be/laHIzhsz12E` ✅ (found this!)

2. `https://n8n.io/workflows/8527-learn-n8n-basics-in-3-easy-steps/`
   - Should have: Tutorial videos
   - Expected: Find embedded video URLs

3. `https://n8n.io/workflows/8237-personal-life-manager-with-telegram-google-services-and-voice-enabled-ai/`
   - Should have: Demo video
   - Expected: Find video URL

4. `https://n8n.io/workflows/7639-talk-to-your-google-sheets-using-chatgpt-5/`
   - Should have: Demo video
   - Expected: Find video URL

These URLs will be checked with Playwright to find the ACTUAL embedded video URLs!


