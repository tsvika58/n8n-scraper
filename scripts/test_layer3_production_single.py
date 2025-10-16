"""
Test Production Layer 3 on Single Workflow

Tests extraction + database save + validation on 1 workflow.

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


async def test_single_workflow():
    """Test extraction + save + validation on workflow 6270"""
    
    print('🧪 SINGLE WORKFLOW TEST: Extraction + Save + Validation')
    print('=' * 80)
    print()
    
    workflow_id = '6270'
    url = 'https://n8n.io/workflows/6270-build-your-first-ai-agent/'
    
    # STEP 1: Extract
    print('STEP 1: Extraction')
    print('─' * 80)
    
    async with ProductionLayer3Extractor(extract_transcripts=True) as extractor:
        result = await extractor.extract(workflow_id, url)
    
    if not result['success']:
        print(f'❌ Extraction failed: {result.get("error")}')
        return False
    
    data = result['data']
    print(f'✅ Extraction successful')
    print(f'   Time: {result["metadata"]["extraction_time"]:.2f}s')
    print(f'   Videos: {data["video_count"]}')
    print(f'   Video URLs: {data["video_urls"][:2]}...')
    print(f'   Transcripts: {data["transcript_count"]}')
    print(f'   Text: {data["total_text_length"]:,} chars')
    print(f'   Quality: {result["quality_score"]}/100')
    print()
    
    # STEP 2: Save to database
    print('STEP 2: Database Save')
    print('─' * 80)
    
    try:
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
                    has_videos = EXCLUDED.has_videos,
                    transcripts = EXCLUDED.transcripts,
                    transcript_count = EXCLUDED.transcript_count,
                    has_transcripts = EXCLUDED.has_transcripts,
                    content_text = EXCLUDED.content_text,
                    total_text_length = EXCLUDED.total_text_length,
                    image_urls = EXCLUDED.image_urls,
                    image_count = EXCLUDED.image_count,
                    iframe_sources = EXCLUDED.iframe_sources,
                    iframe_count = EXCLUDED.iframe_count,
                    has_iframes = EXCLUDED.has_iframes,
                    quality_score = EXCLUDED.quality_score,
                    layer3_success = EXCLUDED.layer3_success,
                    layer3_extracted_at = EXCLUDED.layer3_extracted_at,
                    layer3_version = EXCLUDED.layer3_version
            """), save_data)
            
            session.commit()
            
        print('✅ Database save successful')
        print()
        
    except Exception as e:
        print(f'❌ Database save failed: {e}')
        import traceback
        traceback.print_exc()
        return False
    
    # STEP 3: Validation (read back and verify)
    print('STEP 3: Validation')
    print('─' * 80)
    
    try:
        with get_session() as session:
            read_result = session.execute(text("""
                SELECT 
                    video_urls, video_count, has_videos,
                    transcript_count, has_transcripts,
                    total_text_length, quality_score, layer3_success
                FROM workflow_content
                WHERE workflow_id = :workflow_id
            """), {'workflow_id': workflow_id}).fetchone()
            
            if not read_result:
                print('❌ No data found in database')
                return False
            
            # Validate
            validations = {
                'video_urls_count': len(read_result[0]) == len(data['video_urls']),
                'video_count': read_result[1] == data['video_count'],
                'has_videos': read_result[2] == data['has_videos'],
                'transcript_count': read_result[3] == data['transcript_count'],
                'has_transcripts': read_result[4] == data['has_transcripts'],
                'total_text_length': read_result[5] == data['total_text_length'],
                'quality_score': read_result[6] == result['quality_score'],
                'layer3_success': read_result[7] == True
            }
            
            all_valid = all(validations.values())
            
            if all_valid:
                print('✅ All validations passed')
                print(f'   Video URLs: {len(read_result[0])} ✓')
                print(f'   Video Count: {read_result[1]} ✓')
                print(f'   Transcripts: {read_result[3]} ✓')
                print(f'   Text Length: {read_result[5]:,} ✓')
                print(f'   Quality: {read_result[6]}/100 ✓')
                print()
            else:
                print('❌ Some validations failed:')
                for key, valid in validations.items():
                    status = '✓' if valid else '✗'
                    print(f'   {status} {key}')
                print()
                return False
            
    except Exception as e:
        print(f'❌ Validation failed: {e}')
        import traceback
        traceback.print_exc()
        return False
    
    # Final summary
    print('=' * 80)
    print('🎉 SINGLE WORKFLOW TEST: ALL STEPS PASSED!')
    print('=' * 80)
    print()
    print('✅ Extraction: WORKING')
    print('✅ Database Save: WORKING')
    print('✅ Validation: WORKING')
    print()
    print('🚀 Ready for small batch test!')
    print()
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_single_workflow())
    sys.exit(0 if success else 1)




