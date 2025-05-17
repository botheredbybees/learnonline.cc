from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from db.database import get_db
from auth.auth_bearer import JWTBearer
from auth.auth_handler import get_current_user

router = APIRouter(
    prefix="/units",
    tags=["units"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{unit_code}")
async def get_unit(unit_code: str, db: Session = Depends(get_db)):
    """Get a unit by code"""
    unit = db.execute("""
        SELECT 
            id, code, title, description, status,
            release_date, elements_json
        FROM units
        WHERE code = %s
    """, (unit_code,)).fetchone()
    
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    
    return {"unit": dict(unit)}

@router.get("/{unit_code}/elements")
async def get_unit_elements(unit_code: str, db: Session = Depends(get_db)):
    """Get elements and performance criteria for a unit"""
    # First check if we have JSON data for quick retrieval
    unit = db.execute("""
        SELECT elements_json
        FROM units
        WHERE code = %s
    """, (unit_code,)).fetchone()
    
    if not unit or not unit['elements_json']:
        # Retrieve from tables with full structure
        unit_id = db.execute("""
            SELECT id FROM units WHERE code = %s
        """, (unit_code,)).fetchone()
        
        if not unit_id:
            raise HTTPException(status_code=404, detail="Unit not found")
            
        elements = db.execute("""
            SELECT id, element_num, element_text
            FROM unit_elements
            WHERE unit_id = %s
            ORDER BY element_num
        """, (unit_id['id'],)).fetchall()
        
        result = []
        for element in elements:
            element_dict = dict(element)
            
            # Get PCs for this element
            pcs = db.execute("""
                SELECT pc_num, pc_text
                FROM unit_performance_criteria
                WHERE element_id = %s
                ORDER BY pc_num
            """, (element['id'],)).fetchall()
            
            element_dict['performance_criteria'] = [dict(pc) for pc in pcs]
            result.append(element_dict)
            
        return {"elements": result}
    
    # Return JSON data if available
    return {"elements": unit['elements_json']}

@router.get("/search")
async def search_units(
    query: Optional[str] = None,
    tp_code: Optional[str] = None, 
    page: int = 1, 
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """Search units"""
    # Build WHERE clause
    where_clause = []
    params = []
    
    if query:
        where_clause.append("(u.code ILIKE %s OR u.title ILIKE %s)")
        params.extend([f"%{query}%", f"%{query}%"])
        
    if tp_code:
        where_clause.append("tp.code ILIKE %s")
        params.append(f"%{tp_code}%")
        
    # Create final WHERE clause
    where_sql = " AND ".join(where_clause) if where_clause else "1=1"
    
    # Count total
    count_sql = f"""
        SELECT COUNT(*) as total
        FROM units u
        JOIN training_packages tp ON u.training_package_id = tp.id
        WHERE {where_sql}
    """
    
    total = db.execute(count_sql, params).fetchone()['total']
    
    # Get page of results
    offset = (page - 1) * page_size
    params.extend([page_size, offset])
    
    units_sql = f"""
        SELECT 
            u.id, u.code, u.title, u.status,
            tp.code as tp_code,
            (CASE WHEN u.elements_json IS NOT NULL THEN true ELSE false END) as has_elements
        FROM units u
        JOIN training_packages tp ON u.training_package_id = tp.id
        WHERE {where_sql}
        ORDER BY u.code
        LIMIT %s OFFSET %s
    """
    
    units = db.execute(units_sql, params).fetchall()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "units": [dict(unit) for unit in units]
    }
