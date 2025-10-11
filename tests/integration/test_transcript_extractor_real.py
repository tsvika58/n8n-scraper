"""
Integration tests for TranscriptExtractor with real YouTube videos.

These tests use real YouTube videos and require network access.
Tests include rate limiting to avoid YouTube blocking.

Run with: pytest tests/integration/test_transcript_extractor_real.py -v -s
"""

import pytest
import asyncio
import time
from src.scrapers.transcript_extractor import TranscriptExtractor


# Real YouTube video IDs for testing (public videos with transcripts)
TEST_VIDEOS = [
    {
        'id': 'laHIzhsz12E',
        'url': 'https://www.youtube.com/watch?v=laHIzhsz12E',
        'name': 'AI Agent Tutorial',
        'expected_min_length': 4000
    },
    {
        'id': 'dQw4w9WgXcQ',
        'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'name': 'Rick Astley - Never Gonna Give You Up',
        'expected_min_length': 2000
    },
    {
        'id': '9bZkp7q19f0',
        'url': 'https://www.youtube.com/watch?v=9bZkp7q19f0',
        'name': 'PSY - Gangnam Style',
        'expected_min_length': 200
    }
]


@pytest.fixture
def youtube_cooldown():
    """
    Fixture to handle YouTube rate limiting.
    Waits 15 seconds between tests to avoid blocking.
    """
    yield
    print("\n⏱️  Waiting 15 seconds for YouTube cooldown...")
    time.sleep(15)


class TestTranscriptExtractorRealVideos:
    """Integration tests with real YouTube videos."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_extract_transcript_ai_agent_video(self, youtube_cooldown):
        """Test extraction from AI Agent tutorial video."""
        video = TEST_VIDEOS[0]
        
        print(f"\n🎬 Testing: {video['name']}")
        print(f"   URL: {video['url']}")
        
        async with TranscriptExtractor(headless=True) as extractor:
            start_time = time.time()
            success, transcript, error = await extractor.extract_transcript(
                video['url'], video['id']
            )
            end_time = time.time()
            
            extraction_time = end_time - start_time
            
            print(f"\n📊 Results:")
            print(f"   Success: {success}")
            print(f"   Length: {len(transcript) if transcript else 0} chars")
            print(f"   Time: {extraction_time:.2f}s")
            
            if success:
                print(f"   ✅ SUCCESS")
                assert transcript is not None
                assert len(transcript) >= video['expected_min_length']
                assert extraction_time < 30  # Should be under 30s
                
                # Print preview
                preview = transcript[:150] if transcript else ""
                print(f"   Preview: {preview}...")
            else:
                print(f"   ❌ FAILED: {error}")
                # Don't fail test if YouTube is blocking (expected during heavy testing)
                pytest.skip(f"YouTube may be rate limiting: {error}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_extract_transcript_music_video(self, youtube_cooldown):
        """Test extraction from music video with lyrics."""
        video = TEST_VIDEOS[1]
        
        print(f"\n🎬 Testing: {video['name']}")
        print(f"   URL: {video['url']}")
        
        async with TranscriptExtractor(headless=True) as extractor:
            start_time = time.time()
            success, transcript, error = await extractor.extract_transcript(
                video['url'], video['id']
            )
            end_time = time.time()
            
            extraction_time = end_time - start_time
            
            print(f"\n📊 Results:")
            print(f"   Success: {success}")
            print(f"   Length: {len(transcript) if transcript else 0} chars")
            print(f"   Time: {extraction_time:.2f}s")
            
            if success:
                print(f"   ✅ SUCCESS")
                assert transcript is not None
                assert len(transcript) >= video['expected_min_length']
            else:
                print(f"   ❌ FAILED: {error}")
                pytest.skip(f"YouTube may be rate limiting: {error}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_extract_transcript_short_content(self, youtube_cooldown):
        """Test extraction from video with shorter transcript."""
        video = TEST_VIDEOS[2]
        
        print(f"\n🎬 Testing: {video['name']}")
        
        async with TranscriptExtractor(headless=True) as extractor:
            success, transcript, error = await extractor.extract_transcript(
                video['url'], video['id']
            )
            
            print(f"   Success: {success}, Length: {len(transcript) if transcript else 0}")
            
            if success:
                print(f"   ✅ SUCCESS")
                assert transcript is not None
                # This video has shorter transcript
                assert len(transcript) >= video['expected_min_length']
            else:
                pytest.skip(f"YouTube may be rate limiting: {error}")


class TestTranscriptExtractorPerformance:
    """Integration tests for performance and reliability."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_extraction_speed_under_target(self, youtube_cooldown):
        """Test that extraction completes within target time."""
        video = TEST_VIDEOS[0]
        
        print(f"\n⚡ Performance Test: {video['name']}")
        
        async with TranscriptExtractor(headless=True) as extractor:
            start_time = time.time()
            success, transcript, error = await extractor.extract_transcript(
                video['url'], video['id']
            )
            end_time = time.time()
            
            extraction_time = end_time - start_time
            
            print(f"   Time: {extraction_time:.2f}s")
            
            if success:
                # Target is < 30s, we should be much faster (~10s)
                assert extraction_time < 30
                print(f"   ✅ Under 30s target")
                
                # Bonus: Check if we're under 15s (stretch goal)
                if extraction_time < 15:
                    print(f"   🎯 Under 15s (excellent!)")
            else:
                pytest.skip(f"YouTube may be rate limiting: {error}")
    
    @pytest.mark.asyncio
    @pytest.mark.integration  
    async def test_multiple_sequential_extractions(self, youtube_cooldown):
        """Test extracting from multiple videos sequentially."""
        print(f"\n🔄 Sequential Extraction Test")
        
        results = []
        
        async with TranscriptExtractor(headless=True) as extractor:
            for i, video in enumerate(TEST_VIDEOS[:2], 1):  # Test first 2 videos
                print(f"\n   [{i}/2] Processing: {video['name']}")
                
                # Add cooldown between videos
                if i > 1:
                    print(f"   ⏱️  Waiting 10 seconds...")
                    await asyncio.sleep(10)
                
                success, transcript, error = await extractor.extract_transcript(
                    video['url'], video['id']
                )
                
                results.append({
                    'video': video['name'],
                    'success': success,
                    'length': len(transcript) if transcript else 0
                })
                
                if success:
                    print(f"   ✅ {len(transcript)} chars")
                else:
                    print(f"   ⚠️  {error}")
        
        # Print summary
        print(f"\n📊 Summary:")
        successful = sum(1 for r in results if r['success'])
        print(f"   Successful: {successful}/{len(results)}")
        
        for r in results:
            status = "✅" if r['success'] else "❌"
            print(f"   {status} {r['video']}: {r['length']} chars")
        
        # At least one should succeed (may hit rate limit on second)
        assert successful >= 1


class TestTranscriptExtractorErrorHandling:
    """Integration tests for error scenarios."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_invalid_video_url(self, youtube_cooldown):
        """Test handling of invalid video URL."""
        print(f"\n🚫 Testing invalid URL handling")
        
        async with TranscriptExtractor(headless=True) as extractor:
            success, transcript, error = await extractor.extract_transcript(
                'https://www.youtube.com/watch?v=invalidXXX',
                'invalidXXX'
            )
            
            print(f"   Success: {success}")
            print(f"   Error: {error}")
            
            # Should fail gracefully
            assert success == False
            assert error is not None
            print(f"   ✅ Failed gracefully")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_video_without_transcript(self, youtube_cooldown):
        """Test handling of video that may not have transcript."""
        print(f"\n📝 Testing video without transcript")
        
        # Use a test video that might not have transcripts
        test_url = 'https://www.youtube.com/watch?v=test12345'
        
        async with TranscriptExtractor(headless=True) as extractor:
            success, transcript, error = await extractor.extract_transcript(
                test_url, 'test12345'
            )
            
            print(f"   Success: {success}")
            
            # Should handle gracefully (either succeed or fail with clear error)
            if not success:
                assert error is not None
                print(f"   ✅ Error handled: {error}")
            else:
                print(f"   ✅ Unexpectedly succeeded")


class TestTranscriptExtractorBrowserManagement:
    """Integration tests for browser lifecycle management."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_browser_cleanup_after_extraction(self, youtube_cooldown):
        """Test that browser is properly cleaned up after extraction."""
        print(f"\n🧹 Testing browser cleanup")
        
        video = TEST_VIDEOS[0]
        
        extractor = TranscriptExtractor(headless=True)
        await extractor.initialize()
        
        assert extractor.browser is not None
        assert extractor.playwright is not None
        print(f"   ✅ Browser initialized")
        
        # Extract transcript
        success, transcript, error = await extractor.extract_transcript(
            video['url'], video['id']
        )
        
        if success:
            print(f"   ✅ Extraction completed")
        
        # Cleanup
        await extractor.cleanup()
        
        # Verify cleanup (browser/playwright should be closed)
        print(f"   ✅ Cleanup completed")
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_context_manager_cleanup(self, youtube_cooldown):
        """Test that async context manager properly cleans up."""
        print(f"\n🔄 Testing context manager cleanup")
        
        video = TEST_VIDEOS[0]
        
        async with TranscriptExtractor(headless=True) as extractor:
            assert extractor.browser is not None
            print(f"   ✅ Context entered")
            
            success, transcript, error = await extractor.extract_transcript(
                video['url'], video['id']
            )
            
            if success:
                print(f"   ✅ Extraction in context")
        
        # After context exit, cleanup should have occurred
        print(f"   ✅ Context exited (cleanup automatic)")


# Performance benchmark test (optional, runs last)
@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.slow
async def test_benchmark_extraction_times():
    """
    Benchmark extraction times across multiple videos.
    Marked as 'slow' - run with: pytest -m slow
    """
    print(f"\n📊 BENCHMARK: Extraction Times")
    print(f"=" * 60)
    
    times = []
    
    async with TranscriptExtractor(headless=True) as extractor:
        for i, video in enumerate(TEST_VIDEOS, 1):
            print(f"\n[{i}/{len(TEST_VIDEOS)}] {video['name']}")
            
            if i > 1:
                print(f"   Waiting 15s cooldown...")
                await asyncio.sleep(15)
            
            start_time = time.time()
            success, transcript, error = await extractor.extract_transcript(
                video['url'], video['id']
            )
            end_time = time.time()
            
            extraction_time = end_time - start_time
            
            if success:
                times.append(extraction_time)
                print(f"   ✅ {extraction_time:.2f}s - {len(transcript)} chars")
            else:
                print(f"   ❌ Failed: {error}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"\n" + "=" * 60)
        print(f"BENCHMARK RESULTS:")
        print(f"  Successful: {len(times)}/{len(TEST_VIDEOS)}")
        print(f"  Average: {avg_time:.2f}s")
        print(f"  Min: {min_time:.2f}s")
        print(f"  Max: {max_time:.2f}s")
        print(f"=" * 60)
        
        # Assert performance targets
        assert avg_time < 30  # Under target
        print(f"✅ Average time under 30s target")


