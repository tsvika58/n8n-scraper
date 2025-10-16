# Layer 3 Video Discovery Analysis & Improvement Plan

**Date**: October 15, 2025  
**Status**: Analysis Complete - Ready for Implementation

---

## 🎯 **Current State Analysis**

### What's Working ✅
1. **Basic Video Discovery**: Finds YouTube videos via Playwright and BeautifulSoup
2. **Deduplication**: Removes duplicate videos by YouTube ID
3. **Transcript Extraction**: Has infrastructure for transcript extraction
4. **Database Integration**: Saves to `workflow_content` table
5. **Resume Capability**: Can skip already-processed workflows

### What's NOT Working ❌
1. **Low Transcript Success Rate**: 0 transcripts for most workflows (only 1/10 test workflows has transcripts)
2. **Missing Contextual Videos**: Not identifying which videos are workflow explainers vs. related content
3. **Incomplete Video Discovery**: May miss videos in dynamically loaded iframes
4. **No Video Classification**: Can't distinguish between:
   - Main workflow explainer videos
   - Related workflow videos
   - Tutorial/guide videos
   - Channel/playlist links (false positives)

---

## 🔍 **Test Data**

Found 10 workflows with videos for testing:

| Workflow ID | Videos | Transcripts | URL |
|-------------|--------|-------------|-----|
| 1956 | 4 | 0 | ai-summarize-podcast-episode |
| 1217 | 4 | 0 | fetch-youtube-playlist |
| 1599 | 4 | 0 | send-youtube-videos-to-telegram |
| 1802 | 3 | 1 | generate-random-mock-data |
| 1282 | 3 | 0 | send-file-s3-to-textract |
| 1520 | 3 | 0 | openai-powered-tweet-generator |
| 1394 | 3 | 0 | transcribe-audio-files |
| 1048 | 3 | 0 | create-update-webflow |
| 1393 | 3 | 0 | extract-text-from-images |
| 1111 | 3 | 0 | create-transcription-jobs |

**Key Observation**: 9 out of 10 workflows have 0 transcripts despite having 3-4 videos each!

---

## 🐛 **Root Cause Analysis**

### Issue 1: Transcript Extraction Failures
**Problem**: TranscriptExtractor is failing silently or timing out

**Likely Causes**:
- YouTube API rate limiting
- Timeout too short (default 30s)
- Videos don't have captions/transcripts available
- Transcript extractor not handling errors properly

**Solution**:
- Increase timeout to 60s
- Add retry logic with exponential backoff
- Better error logging to understand why transcripts fail
- Check if video has captions before attempting extraction

### Issue 2: Video Classification Missing
**Problem**: Can't identify which videos are contextual explainers for the workflow

**Current Behavior**:
- Finds ALL videos on page (including related workflows, ads, etc.)
- No way to know which video explains THIS workflow

**What We Need**:
1. **Primary Explainer Video**: The main video that explains how to use THIS workflow
2. **Related Videos**: Other n8n workflow videos shown on the page
3. **Tutorial Videos**: General n8n tutorial videos
4. **False Positives**: Channel links, playlists, etc.

**Solution**:
- Analyze video context (surrounding text, iframe title, video title)
- Check if video is in the main content area vs. sidebar
- Look for keywords like "workflow", "tutorial", "how to use"
- Prioritize videos embedded in iframes over links

### Issue 3: Iframe Navigation Issues
**Problem**: May not be fully navigating into all iframes to find embedded videos

**Current Behavior**:
```python
iframes = await page.query_selector_all('iframe')
for iframe in iframes:
    frame_content = await iframe.content_frame()
    if frame_content:
        videos = await self._discover_videos_playwright(frame_content)
```

**Potential Issues**:
- `content_frame()` may return None for cross-origin iframes
- Not waiting for iframe content to load
- Not scrolling to make iframes visible
- Not handling nested iframes

**Solution**:
- Add wait for iframe to be visible
- Handle cross-origin restrictions gracefully
- Extract iframe src and analyze HTML directly
- Look for video embeds in iframe src URLs

---

## 🎯 **Improvement Plan**

### Phase 1: Enhanced Video Discovery ✨
**Goal**: Find 100% of videos, including those in iframes

**Changes**:
1. Add iframe visibility check before accessing
2. Extract iframe src URLs and analyze them
3. Look for video embeds in iframe HTML
4. Handle cross-origin iframes by analyzing src attribute
5. Add scroll-to-view for lazy-loaded iframes

### Phase 2: Video Classification 🏷️
**Goal**: Identify contextual explainer videos vs. related content

**New Fields**:
```python
{
    'url': 'https://youtu.be/...',
    'youtube_id': '...',
    'type': 'primary_explainer' | 'related_workflow' | 'tutorial' | 'other',
    'context': {
        'iframe_title': '...',
        'surrounding_text': '...',
        'position': 'main_content' | 'sidebar' | 'footer',
        'confidence': 0.0-1.0
    }
}
```

**Classification Logic**:
1. **Primary Explainer** (highest priority):
   - In main content iframe
   - Title/description mentions workflow name
   - First video on page
   - Embedded (not just linked)

2. **Related Workflow**:
   - In sidebar or "Related workflows" section
   - Links to other n8n workflow pages

3. **Tutorial**:
   - General n8n tutorials
   - Not specific to this workflow

4. **Other**:
   - Ads, channel links, playlists

### Phase 3: Robust Transcript Extraction 📝
**Goal**: Get transcripts for all videos that have them

**Improvements**:
1. Increase timeout from 30s to 60s
2. Add retry logic (3 attempts with backoff)
3. Check if video has captions before attempting
4. Better error handling and logging
5. Fallback to youtube-transcript-api if Playwright fails

### Phase 4: Database Schema Updates 💾
**Goal**: Store video classification and context

**New Columns** (already exist, just need to use them properly):
- `video_urls`: ARRAY - All video URLs
- `video_metadata`: JSONB - Video details with classification
- `transcripts`: JSONB - Transcripts by video URL
- `video_count`: INTEGER - Total videos found
- `transcript_count`: INTEGER - Successful transcripts

---

## 🚀 **Implementation Steps**

### Step 1: Update Layer 3 Extractor ✅
- [x] Audit current code
- [ ] Add enhanced iframe navigation
- [ ] Implement video classification
- [ ] Improve transcript extraction
- [ ] Add detailed logging

### Step 2: Update to Global Connection Coordinator ✅
- [ ] Replace `get_session()` with `global_coordinator.get_session()`
- [ ] Test connection pooling with L3

### Step 3: Create Test Script ✅
- [ ] Test on 10 workflows with videos
- [ ] Verify all videos found
- [ ] Verify video classification
- [ ] Verify transcript extraction
- [ ] Compare before/after results

### Step 4: Validate & Deploy ✅
- [ ] Run on test workflows
- [ ] Analyze results
- [ ] Fix any issues
- [ ] Deploy to production

---

## 📊 **Success Criteria**

### Video Discovery
- ✅ Find 100% of videos on page
- ✅ Correctly identify primary explainer videos
- ✅ Classify all videos by type
- ✅ No false positives (channel/playlist links)

### Transcript Extraction
- ✅ Get transcripts for 80%+ of videos (that have them)
- ✅ Handle videos without captions gracefully
- ✅ Proper error logging for failures

### Performance
- ✅ < 60s per workflow (increased from 30s for transcripts)
- ✅ Stable connection pool usage
- ✅ No memory leaks from Playwright

### Data Quality
- ✅ All videos stored with metadata
- ✅ Video classification accurate
- ✅ Transcripts properly formatted
- ✅ Quality score reflects actual content

---

## 🎓 **Key Learnings**

1. **Iframe Navigation is Complex**: Cross-origin restrictions, lazy loading, nested iframes
2. **Video Classification Matters**: Not all videos are equal - need to identify explainers
3. **Transcripts are Valuable**: But not all videos have them - need graceful handling
4. **Testing is Critical**: Need real workflows with videos to validate

---

## 📝 **Next Actions**

1. ✅ Create enhanced Layer 3 extractor with all improvements
2. ✅ Update to use global connection coordinator
3. ✅ Create comprehensive test script
4. ✅ Run on 10 test workflows
5. ✅ Analyze and fix any issues
6. ✅ Deploy to production

---

**Status**: Ready for implementation  
**Estimated Time**: 2-3 hours  
**Risk**: Low (can rollback to current version if needed)


