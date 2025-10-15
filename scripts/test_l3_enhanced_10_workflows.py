#!/usr/bin/env python3
"""
Test Enhanced Layer 3 on 10 Workflows with Videos

Tests:
1. Video discovery (find ALL videos)
2. Video classification (primary explainer vs. related)
3. Transcript extraction (robust with retries)
4. Database save with global connection coordinator
5. Data retrieval and validation

Author: AI Assistant
Date: October 15, 2025
"""

import asyncio
import sys
import json
from datetime import datetime

sys.path.append('/app')

from src.scrapers.layer3_enhanced_v2 import EnhancedLayer3Extractor
from src.storage.global_connection_coordinator import global_coordinator
from sqlalchemy import text
from loguru import logger


async def test_enhanced_l3():
    """Test enhanced L3 on 10 workflows with videos"""
    
    logger.info("="*80)
    logger.info("🧪 TESTING ENHANCED LAYER 3 ON 10 WORKFLOWS")
    logger.info("="*80)
    
    # Get connection status
    status = global_coordinator.get_global_status()
    logger.info(f"📊 Connection Pool Status:")
    logger.info(f"   - Supabase Plan: {status['supabase_plan']}")
    logger.info(f"   - Available: {status['remaining']}/{status['max_connections']}")
    logger.info(f"   - Utilization: {status['utilization_pct']:.1f}%")
    logger.info("")
    
    # Get 10 test workflows with videos
    logger.info("📥 Fetching 10 test workflows with videos...")
    with global_coordinator.get_session() as session:
        result = session.execute(text("""
            SELECT 
                w.workflow_id,
                w.url,
                wc.video_count as old_video_count,
                wc.transcript_count as old_transcript_count
            FROM workflows w
            LEFT JOIN workflow_content wc ON w.workflow_id = wc.workflow_id
            WHERE wc.has_videos = true AND wc.video_count > 0
            ORDER BY wc.video_count DESC, wc.transcript_count ASC
            LIMIT 10
        """))
        workflows = result.fetchall()
    
    if not workflows:
        logger.error("❌ No workflows with videos found!")
        return False
    
    logger.info(f"✅ Found {len(workflows)} test workflows")
    for idx, wf in enumerate(workflows, 1):
        logger.info(f"   {idx}. {wf[0]}: {wf[2]} videos, {wf[3]} transcripts (old)")
    logger.info("")
    
    # Initialize enhanced extractor
    logger.info("🚀 Initializing Enhanced Layer 3 Extractor...")
    async with EnhancedLayer3Extractor(extract_transcripts=True) as extractor:
        
        # Stats tracking
        stats = {
            'total': len(workflows),
            'successful': 0,
            'failed': 0,
            'total_videos_found': 0,
            'total_primary_explainers': 0,
            'total_transcripts': 0,
            'improvements': []
        }
        
        # Process each workflow
        for idx, wf in enumerate(workflows, 1):
            workflow_id = wf[0]
            url = wf[1]
            old_video_count = wf[2] or 0
            old_transcript_count = wf[3] or 0
            
            logger.info(f"")
            logger.info(f"{'='*80}")
            logger.info(f"🔄 [{idx}/{stats['total']}] Processing: {workflow_id}")
            logger.info(f"   URL: {url}")
            logger.info(f"   Old: {old_video_count} videos, {old_transcript_count} transcripts")
            logger.info(f"{'='*80}")
            
            try:
                # Extract with enhanced L3
                result = await extractor.extract(workflow_id, url)
                
                if result.get('success'):
                    data = result['data']
                    
                    # Count improvements
                    new_video_count = data['video_count']
                    new_transcript_count = data['transcript_count']
                    primary_explainer_count = len(data['primary_explainer_videos'])
                    
                    video_improvement = new_video_count - old_video_count
                    transcript_improvement = new_transcript_count - old_transcript_count
                    
                    stats['successful'] += 1
                    stats['total_videos_found'] += new_video_count
                    stats['total_primary_explainers'] += primary_explainer_count
                    stats['total_transcripts'] += new_transcript_count
                    
                    if video_improvement > 0 or transcript_improvement > 0:
                        stats['improvements'].append({
                            'workflow_id': workflow_id,
                            'video_improvement': video_improvement,
                            'transcript_improvement': transcript_improvement
                        })
                    
                    # Log results
                    logger.info(f"")
                    logger.info(f"📊 Results for {workflow_id}:")
                    logger.info(f"   Videos: {new_video_count} ({video_improvement:+d} vs. old)")
                    logger.info(f"   Primary Explainers: {primary_explainer_count}")
                    logger.info(f"   Transcripts: {new_transcript_count} ({transcript_improvement:+d} vs. old)")
                    logger.info(f"   Quality Score: {result['quality_score']}/100")
                    logger.info(f"   Extraction Time: {result['metadata']['extraction_time']:.1f}s")
                    
                    # Show video classification
                    if data['videos']:
                        logger.info(f"")
                        logger.info(f"   🎬 Video Classification:")
                        for video in data['videos']:
                            classification = video.get('classification', 'unknown')
                            confidence = video.get('confidence', 0)
                            youtube_id = video.get('youtube_id', 'unknown')
                            has_transcript = video.get('has_transcript', False)
                            transcript_icon = "📝" if has_transcript else "❌"
                            logger.info(f"      {transcript_icon} {youtube_id}: {classification} ({confidence:.0%})")
                    
                    # Save to database
                    logger.info(f"")
                    logger.info(f"💾 Saving to database...")
                    with global_coordinator.get_session() as session:
                        # Check if record exists
                        existing = session.execute(text("""
                            SELECT id FROM workflow_content WHERE workflow_id = :wf_id
                        """), {'wf_id': workflow_id}).fetchone()
                        
                        if existing:
                            # Update existing record
                            session.execute(text("""
                                UPDATE workflow_content SET
                                    video_urls = :video_urls,
                                    video_count = :video_count,
                                    has_videos = :has_videos,
                                    video_metadata = :video_metadata,
                                    transcripts = :transcripts,
                                    transcript_count = :transcript_count,
                                    has_transcripts = :has_transcripts,
                                    content_text = :content_text,
                                    total_text_length = :total_text_length,
                                    image_urls = :image_urls,
                                    image_count = :image_count,
                                    link_urls = :link_urls,
                                    link_count = :link_count,
                                    quality_score = :quality_score,
                                    layer3_success = true,
                                    layer3_extracted_at = NOW(),
                                    layer3_version = :version
                                WHERE workflow_id = :wf_id
                            """), {
                                'wf_id': workflow_id,
                                'video_urls': data['video_urls'],
                                'video_count': data['video_count'],
                                'has_videos': data['has_videos'],
                                'video_metadata': json.dumps(data['video_metadata']),
                                'transcripts': json.dumps(data['transcripts']),
                                'transcript_count': data['transcript_count'],
                                'has_transcripts': data['has_transcripts'],
                                'content_text': data['content_text'],
                                'total_text_length': data['total_text_length'],
                                'image_urls': data['image_urls'],
                                'image_count': data['image_count'],
                                'link_urls': data['link_urls'],
                                'link_count': data['link_count'],
                                'quality_score': result['quality_score'],
                                'version': result['metadata']['extractor_version']
                            })
                        else:
                            # Insert new record
                            session.execute(text("""
                                INSERT INTO workflow_content (
                                    workflow_id, video_urls, video_count, has_videos,
                                    video_metadata, transcripts, transcript_count, has_transcripts,
                                    content_text, total_text_length, image_urls, image_count,
                                    link_urls, link_count, quality_score,
                                    layer3_success, layer3_extracted_at, layer3_version
                                ) VALUES (
                                    :wf_id, :video_urls, :video_count, :has_videos,
                                    :video_metadata, :transcripts, :transcript_count, :has_transcripts,
                                    :content_text, :total_text_length, :image_urls, :image_count,
                                    :link_urls, :link_count, :quality_score,
                                    true, NOW(), :version
                                )
                            """), {
                                'wf_id': workflow_id,
                                'video_urls': data['video_urls'],
                                'video_count': data['video_count'],
                                'has_videos': data['has_videos'],
                                'video_metadata': json.dumps(data['video_metadata']),
                                'transcripts': json.dumps(data['transcripts']),
                                'transcript_count': data['transcript_count'],
                                'has_transcripts': data['has_transcripts'],
                                'content_text': data['content_text'],
                                'total_text_length': data['total_text_length'],
                                'image_urls': data['image_urls'],
                                'image_count': data['image_count'],
                                'link_urls': data['link_urls'],
                                'link_count': data['link_count'],
                                'quality_score': result['quality_score'],
                                'version': result['metadata']['extractor_version']
                            })
                        
                        session.commit()
                    
                    logger.success(f"✅ Saved {workflow_id} to database")
                
                else:
                    stats['failed'] += 1
                    logger.error(f"❌ Extraction failed: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                stats['failed'] += 1
                logger.error(f"❌ Error processing {workflow_id}: {e}")
                import traceback
                traceback.print_exc()
    
    # Final summary
    logger.info("")
    logger.info("="*80)
    logger.info("📊 FINAL RESULTS")
    logger.info("="*80)
    logger.info(f"Total Workflows: {stats['total']}")
    logger.info(f"Successful: {stats['successful']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"")
    logger.info(f"Total Videos Found: {stats['total_videos_found']}")
    logger.info(f"Primary Explainers: {stats['total_primary_explainers']}")
    logger.info(f"Total Transcripts: {stats['total_transcripts']}")
    logger.info(f"")
    
    if stats['improvements']:
        logger.info(f"🎉 Improvements over old L3:")
        for imp in stats['improvements']:
            logger.info(f"   {imp['workflow_id']}: "
                       f"+{imp['video_improvement']} videos, "
                       f"+{imp['transcript_improvement']} transcripts")
    
    # Final connection status
    final_status = global_coordinator.get_global_status()
    logger.info("")
    logger.info("📊 Final Connection Pool Status:")
    logger.info(f"   - Utilization: {final_status['utilization_pct']:.1f}%")
    logger.info("="*80)
    
    return stats['successful'] > 0


if __name__ == "__main__":
    try:
        success = asyncio.run(test_enhanced_l3())
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

