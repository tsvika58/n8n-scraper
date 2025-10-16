#!/usr/bin/env python3
"""
Backfill extraction snapshots (JSON payloads) for specified workflows.

Creates L2V2 and L3V3 snapshot entries from existing tables:
- workflow_node_contexts → payload { node_contexts: [...] }
- workflow_standalone_docs → payload { standalone_docs: [...] }
"""

import json
from typing import List, Dict, Any
from datetime import datetime

from sqlalchemy import text

import sys, os
sys.path.append('.')
sys.path.append('../n8n-shared')
from src.storage.database import get_session


WORKFLOW_IDS = [
    '8237', '6270', '5170', '4123', '3891', '3456', '2987'
]


def snapshot_exists(session, workflow_id: str, layer: str) -> bool:
    result = session.execute(
        text("SELECT 1 FROM workflow_extraction_snapshots WHERE workflow_id=:w AND layer=:l LIMIT 1"),
        {"w": workflow_id, "l": layer}
    ).fetchone()
    return result is not None


def fetch_node_contexts(session, workflow_id: str) -> List[Dict[str, Any]]:
    rows = session.execute(text(
        """
        SELECT node_name, node_type, node_position, sticky_title, sticky_content, sticky_markdown,
               match_confidence, extraction_method, extracted_at
        FROM workflow_node_contexts
        WHERE workflow_id = :w
        ORDER BY id
        """
    ), {"w": workflow_id}).fetchall()
    contexts = []
    for r in rows:
        contexts.append({
            "node_name": r[0],
            "node_type": r[1],
            "node_position": r[2],
            "sticky_title": r[3],
            "sticky_content": r[4],
            "sticky_markdown": r[5],
            "match_confidence": float(r[6]) if r[6] is not None else None,
            "extraction_method": r[7],
            "extracted_at": r[8].isoformat() if r[8] else None,
        })
    return contexts


def fetch_standalone_docs(session, workflow_id: str) -> List[Dict[str, Any]]:
    rows = session.execute(text(
        """
        SELECT doc_type, doc_title, doc_content, doc_markdown, doc_position, confidence_score, extracted_at
        FROM workflow_standalone_docs
        WHERE workflow_id = :w
        ORDER BY id
        """
    ), {"w": workflow_id}).fetchall()
    docs = []
    for r in rows:
        docs.append({
            "doc_type": r[0],
            "doc_title": r[1],
            "doc_content": r[2],
            "doc_markdown": r[3],
            "doc_position": r[4],
            "confidence_score": float(r[5]) if r[5] is not None else None,
            "extracted_at": r[6].isoformat() if r[6] else None,
        })
    return docs


def insert_snapshot(session, workflow_id: str, layer: str, payload: Dict[str, Any]):
    session.execute(text(
        """
        INSERT INTO workflow_extraction_snapshots (workflow_id, layer, payload)
        VALUES (:w, :l, :p)
        """
    ), {"w": workflow_id, "l": layer, "p": json.dumps(payload)})


def backfill(workflow_ids: List[str]):
    created = 0
    with get_session() as session:
        for wid in workflow_ids:
            # L2V2
            if not snapshot_exists(session, wid, 'L2V2'):
                node_contexts = fetch_node_contexts(session, wid)
                if node_contexts:
                    insert_snapshot(session, wid, 'L2V2', {"node_contexts": node_contexts})
                    created += 1
            # L3V3
            if not snapshot_exists(session, wid, 'L3V3'):
                docs = fetch_standalone_docs(session, wid)
                if docs:
                    insert_snapshot(session, wid, 'L3V3', {"standalone_docs": docs})
                    created += 1
    return created


if __name__ == '__main__':
    print("🔄 Backfilling extraction snapshots for 7 workflows...")
    total = backfill(WORKFLOW_IDS)
    print(f"✅ Backfill complete. Snapshots created: {total}")



