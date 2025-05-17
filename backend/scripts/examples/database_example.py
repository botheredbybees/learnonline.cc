#!/usr/bin/env python3
"""
Example script for working with TGA data in the database

This script shows how to:
1. Connect to the database
2. Query units and their elements
3. Update elements and performance criteria
"""
import os
import sys
import json
import logging
from pathlib import Path
import psycopg2
from psycopg2.extras import DictCursor, Json
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to path for imports
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
sys.path.insert(0, ROOT_DIR)

# Load environment variables
load_dotenv()

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}

def example_query_units():
    """
    Example of querying units and their elements from the database
    """
    try:
        # Connect to the database
        logger.info("Connecting to database...")
        with psycopg2.connect(**DB_PARAMS) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                # Query units with elements
                logger.info("Querying units with elements...")
                cur.execute("""
                    SELECT 
                        u.id, u.code, u.title, u.elements_json,
                        (SELECT COUNT(*) FROM unit_elements ue WHERE ue.unit_id = u.id) as element_count,
                        (SELECT COUNT(*) FROM unit_performance_criteria upc WHERE upc.unit_id = u.id) as pc_count
                    FROM units u
                    WHERE u.elements_json IS NOT NULL
                    ORDER BY u.code
                    LIMIT 5
                """)
                
                units = cur.fetchall()
                
                if not units:
                    logger.warning("No units with elements found in the database")
                    return
                
                # Display the results
                logger.info(f"Found {len(units)} units with elements:")
                
                for i, unit in enumerate(units):
                    logger.info(f"Unit {i+1}: {unit['code']} - {unit['title']}")
                    logger.info(f"  Elements: {unit['element_count']}")
                    logger.info(f"  Performance Criteria: {unit['pc_count']}")
                    
                    # Get elements detail
                    cur.execute("""
                        SELECT 
                            ue.id, ue.element_num, ue.element_text,
                            (
                                SELECT json_agg(
                                    json_build_object(
                                        'id', upc.id, 
                                        'pc_num', upc.pc_num, 
                                        'pc_text', upc.pc_text
                                    )
                                )
                                FROM unit_performance_criteria upc
                                WHERE upc.element_id = ue.id
                                ORDER BY upc.pc_num
                            ) as performance_criteria
                        FROM unit_elements ue
                        WHERE ue.unit_id = %s
                        ORDER BY ue.element_num
                    """, (unit['id'],))
                    
                    elements = cur.fetchall()
                    
                    for j, element in enumerate(elements):
                        logger.info(f"    Element {element['element_num']}: {element['element_text']}")
                        
                        if element['performance_criteria']:
                            pcs = element['performance_criteria']
                            logger.info(f"      {len(pcs)} Performance Criteria:")
                            for k, pc in enumerate(pcs):
                                if k < 3:  # Show first 3 PCs only
                                    logger.info(f"        {pc['pc_num']}: {pc['pc_text']}")
                                elif k == 3:
                                    logger.info(f"        ... and {len(pcs) - 3} more")
                                    break
                        else:
                            logger.info("      No performance criteria found")
    
    except Exception as e:
        logger.error(f"Error querying database: {e}")

if __name__ == "__main__":
    example_query_units()
