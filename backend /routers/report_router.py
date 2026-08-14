"""
Роутер отчётов.
"""
from fastapi import APIRouter, Depends, Query
from sqlmodel import select
from collections import defaultdict

from backend.db import get_session
from backend.models.order import Order
from backend.auth import require_any

router = APIRouter()

@router.get("/summary")
async def get_report_summary(
    month: int = Query(1),
    year: int = Query(2026),
    user: dict = Depends(require_any)
):
    """Сводка за месяц."""
    with get_session() as session:
        # Ищем оба формата: ДД.ММ.ГГГГ и ГГГГ-ММ-ДД
        pattern1 = f"%.{month:02d}.{year}"
        pattern2 = f"{year}-{month:02d}-%"
        
        orders = session.exec(
            select(Order).where(
                Order.date.like(pattern1) | Order.date.like(pattern2)
            )
        ).all()

    total_orders = len(orders)
    total_revenue = sum(o.total_amount for o in orders if o.status == 'completed')
    average_order = total_revenue / total_orders if total_orders else 0

    salary_by_performer = defaultdict(float)
    for o in orders:
        for perf, amt in o.salary.items():
            salary_by_performer[perf] += amt

    work_stats = defaultdict(float)
    for o in orders:
        for w in o.works:
            work_stats[w['name']] += w.get('sum_rub', 0)
    top_works = sorted(work_stats.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "status": "ok",
        "period": {"month": month, "year": year},
        "total_orders": total_orders,
        "total_revenue": round(total_revenue, 2),
        "average_order": round(average_order, 2),
        "salary_by_performer": dict(salary_by_performer),
        "top_works": top_works
    }
