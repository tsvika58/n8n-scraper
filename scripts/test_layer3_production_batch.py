"""
Test Production Layer 3 on Small Batch

Tests extraction + save + validation on 5 workflows to validate stability.

Author: Developer-2 (Dev2)
Date: October 14, 2025
"""

import asyncio
import sys
import json
from datetime import datetime

sys.path.append('/app')

from src.scrapers.layer3_production_ready import ProductionLayer3Extractor
from src.storage.database import get_session
from sqlalchemy import text
from loguru import logger


async def test_batch():
    """Test on 5 workflows"""
    
    print('🧪 SMALL BATCH TEST: 5 Workflows')
    print('=' * 80)
    print()
    
    # Get 5 workflows
    with get_session() as session:
        result = session.execute(text("""
            SELECT workflow_id, url
            FROM workflows
            WHERE url IS NOT NULL
            ORDER BY workflow_id
            LIMIT 5
        """)).fetchall()
        
        workflows = [{'workflow_id': r[0], 'url': r[1]} for r in result]
    
    print(f'Testing {len(workflows)} workflows:')
    for wf in workflows:
        print(f'   - {wf["workflow_id"]}')
    print()
    
    results = []
    
    async with ProductionLayer3Extractor(extract_transcripts=True) as extractor:
        for i, workflow in enumerate(workflows, 1):
            workflow_id = workflow['workflow_id']
            url = workflow['url']
            
            print(f'[{i}/{len(workflows)}] Processing {workflow_id}...')
            
            try:
                # Extract
                result = await extractor.extract(workflow_id, url)
                
                if not result['success']:
                    print(f'   ❌ Extraction failed: {result.get("error")}')
                    results.append({'workflow_id': workflow_id, 'success': False})
                    continue
                
                data = result['data']
                
                # Save
                with get_session() as session:
                    save_data = {
                        'workflow_id': workflow_id,
                        'video_urls': data['video_urls'],
                        'video_metadata': json.dumps(data['videos']),
                        'video_count': data['video_count'],
                        'has_videos': data['has_videos'],
                        'transcripts': json.dumps(data['transcripts']),
                        'transcript_count': data['transcript_count'],
                        'has_transcripts': data['has_transcripts'],
                        'content_text': data['content_text'],
                        'total_text_length': data['total_text_length'],
                        'image_urls': data['image_urls'],
                        'image_count': data['image_count'],
                        'iframe_sources': data['iframe_sources'],
                        'iframe_count': data['iframe_count'],
                        'has_iframes': data['has_iframes'],
                        'quality_score': result['quality_score'],
                        'layer3_success': True,
                        'layer3_extracted_at': datetime.utcnow(),
                        'layer3_version': result['metadata']['extractor_version']
                    }
                    
                    session.execute(text("""
                        INSERT INTO workflow_content (
                            workflow_id, video_urls, video_metadata, video_count, has_videos,
                            transcripts, transcript_count, has_transcripts,
                            content_text, total_text_length,
                            image_urls, image_count,
                            iframe_sources, iframe_count, has_iframes,
                            quality_score, layer3_success, layer3_extracted_at, layer3_version
                        ) VALUES (
                            :workflow_id, :video_urls, :video_metadata, :video_count, :has_videos,
                            :transcripts, :transcript_count, :has_transcripts,
                            :content_text, :total_text_length,
                            :image_urls, :image_count,
                            :iframe_sources, :iframe_count, :has_iframes,
                            :quality_score, :layer3_success, :layer3_extracted_at, :layer3_version
                        )
                        ON CONFLICT (workflow_id) DO UPDATE SET
                            video_urls = EXCLUDED.video_urls,
                            video_metadata = EXCLUDED.video_metadata,
                            video_count = EXCLUDED.video_count,
                            transcripts = EXCLUDED.transcripts,
                            transcript_count = EXCLUDED.transcript_count,
                            content_text = EXCLUDED.content_text,
                            total_text_length = EXCLUDED.total_text_length,
                            quality_score = EXCLUDED.quality_score,
                            layer3_success = EXCLUDED.layer3_success,
                            layer3_extracted_at = EXCLUDED.layer3_extracted_at
                    """), save_data)
                    
                    session.commit()
                
                print(f'   ✅ Saved: {data["video_count"]} videos, {data["transcript_count"]} transcripts, Q:{result["quality_score"]}/100')
                
                results.append({
                    'workflow_id': workflow_id,
                    'success': True,
                    'video_count': data['video_count'],
                    'transcript_count': data['transcript_count'],
                    'quality_score': result['quality_score'],
                    'time': result['metadata']['extraction_time']
                })
                
            except Exception as e:
                print(f'   ❌ Failed: {e}')
                results.append({'workflow_id': workflow_id, 'success': False})
    
    # Summary
    print()
    print('=' * 80)
    print('🎯 BATCH TEST RESULTS')
    print('=' * 80)
    print()
    
    successful = [r for r in results if r['success']]
    
    print(f'✅ Successful: {len(successful)}/{len(results)}')
    
    if successful:
        total_videos = sum(r['video_count'] for r in successful)
        total_transcripts = sum(r['transcript_count'] for r in successful)
        avg_quality = sum(r['quality_score'] for r in successful) / len(successful)
        avg_time = sum(r['time'] for r in successful) / len(successful)
        
        print(f'🎥 Total Videos: {total_videos}')
        print(f'📝 Total Transcripts: {total_transcripts}')
        print(f'📊 Avg Quality: {avg_quality:.1f}/100')
        print(f'⏱️  Avg Time: {avg_time:.2f}s')
        print()
        
        if len(successful) == len(results):
            print('🎉 ALL TESTS PASSED!')
            print()
            print('✅ Ready for full production scrape!')
            return True
        else:
            print('⚠️  Some tests failed')
            return False
    else:
        print('❌ All tests failed')
        return False


if __name__ == "__main__":
    success = asyncio.run(test_batch())
    sys.exit(0 if success else 1)



