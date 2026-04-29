from datetime import datetime, timedelta
from typing import List, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import (
    Personnel, Authorization, Training, Supervision,
    Equipment, Calibration, Check, Maintenance,
    QualityControl, InternalAudit, ManagementReview,
    DetectionProject, Sample, Report,
    Document,
    NCR,
    PersonnelStatus, EquipmentStatus, ClosureStatus,
)


def get_dashboard_stats(db: Session) -> Dict[str, Any]:
    today = datetime.now().date()
    days_30 = today + timedelta(days=30)
    days_15 = today + timedelta(days=15)

    active_personnel = db.query(func.count(Personnel.id)).filter(
        Personnel.status == PersonnelStatus.active
    ).scalar()

    active_equipment = db.query(func.count(Equipment.id)).filter(
        Equipment.status == EquipmentStatus.in_use
    ).scalar()

    repairing_equipment = db.query(func.count(Equipment.id)).filter(
        Equipment.status == EquipmentStatus.repairing
    ).scalar()

    outsource_equipment = db.query(func.count(Equipment.id)).filter(
        Equipment.status == EquipmentStatus.outsource
    ).scalar()

    auth_expiring = db.query(func.count(Authorization.id)).filter(
        Authorization.expire_date <= days_30,
        Authorization.expire_date >= today,
        Authorization.status != "已过期",
    ).scalar()

    auth_expired = db.query(func.count(Authorization.id)).filter(
        Authorization.expire_date < today,
        Authorization.status != "已过期",
    ).scalar()

    cal_expiring = db.query(func.count(Calibration.id)).filter(
        Calibration.next_cal_date <= days_30,
        Calibration.next_cal_date >= today,
    ).scalar()

    check_expiring = db.query(func.count(Check.id)).filter(
        Check.next_check_date <= days_15,
        Check.next_check_date >= today,
    ).scalar()

    qc_total = db.query(func.count(QualityControl.id)).scalar()
    qc_completed = db.query(func.count(QualityControl.id)).filter(
        QualityControl.status == "已完成"
    ).scalar()
    qc_rate = f"{qc_completed / qc_total * 100:.1f}%" if qc_total > 0 else "0%"

    ncr_total = db.query(func.count(NCR.id)).scalar()
    ncr_closed = db.query(func.count(NCR.id)).filter(
        NCR.closure_status == ClosureStatus.closed
    ).scalar()
    ncr_rate = f"{ncr_closed / ncr_total * 100:.1f}%" if ncr_total > 0 else "0%"

    ncr_overdue = db.query(func.count(NCR.id)).filter(
        NCR.plan_complete_date < today,
        NCR.closure_status != ClosureStatus.closed,
    ).scalar()

    project_in_progress = db.query(func.count(DetectionProject.id)).filter(
        DetectionProject.status.notin_(["已完成", "已取消"])
    ).scalar()

    project_overdue = db.query(func.count(DetectionProject.id)).filter(
        DetectionProject.plan_complete_date < today,
        DetectionProject.status.notin_(["已完成", "已取消"]),
    ).scalar()

    pending_reports = db.query(func.count(Report.id)).filter(
        Report.status == "待审批"
    ).scalar()

    docs_active = db.query(func.count(Document.id)).filter(
        Document.status == "现行有效"
    ).scalar()

    docs_review_needed = db.query(func.count(Document.id)).filter(
        Document.next_review_date <= days_30,
    ).scalar()

    eq_status_dist = db.query(
        Equipment.status, func.count(Equipment.id)
    ).group_by(Equipment.status).all()
    eq_status_data = {str(s.value): c for s, c in eq_status_dist}

    ncr_source_dist = db.query(
        NCR.source_type, func.count(NCR.id)
    ).group_by(NCR.source_type).all()
    ncr_source_data = {str(s.value): c for s, c in ncr_source_dist}

    ncr_closure_dist = db.query(
        NCR.closure_status, func.count(NCR.id)
    ).group_by(NCR.closure_status).all()
    ncr_closure_data = {str(s.value): c for s, c in ncr_closure_dist}

    dept_dist = db.query(
        Personnel.department, func.count(Personnel.id)
    ).filter(Personnel.status == PersonnelStatus.active).group_by(Personnel.department).all()
    dept_data = {d or "未分配": c for d, c in dept_dist}

    doc_level_dist = db.query(
        Document.doc_level, func.count(Document.id)
    ).group_by(Document.doc_level).all()
    doc_level_data = {str(s.value): c for s, c in doc_level_dist}

    doc_status_dist = db.query(
        Document.status, func.count(Document.id)
    ).group_by(Document.status).all()
    doc_status_data = {str(s.value): c for s, c in doc_status_dist}

    auth_status_dist = db.query(
        Authorization.status, func.count(Authorization.id)
    ).group_by(Authorization.status).all()
    auth_status_data = {str(s.value): c for s, c in auth_status_dist}

    project_status_dist = db.query(
        DetectionProject.status, func.count(DetectionProject.id)
    ).group_by(DetectionProject.status).all()
    project_status_data = {str(s.value): c for s, c in project_status_dist}

    qc_type_dist = db.query(
        QualityControl.qc_type, func.count(QualityControl.id)
    ).group_by(QualityControl.qc_type).all()
    qc_type_data = {str(s.value): c for s, c in qc_type_dist}

    warnings = []
    if ncr_overdue > 0:
        warnings.append(f"不符合项：{ncr_overdue}项超期未关闭")
    if cal_expiring > 0:
        warnings.append(f"设备校准：{cal_expiring}台30天内到期")
    if check_expiring > 0:
        warnings.append(f"期间核查：{check_expiring}台15天内到期")
    if auth_expiring > 0:
        warnings.append(f"人员授权：{auth_expiring}项30天内到期")
    if auth_expired > 0:
        warnings.append(f"人员授权：{auth_expired}项已过期")
    if project_overdue > 0:
        warnings.append(f"检测项目：{project_overdue}项超期")
    if docs_review_needed > 0:
        warnings.append(f"体系文件：{docs_review_needed}份待评审")

    return {
        "summary": {
            "active_personnel": active_personnel,
            "active_equipment": active_equipment,
            "qc_rate": qc_rate,
            "ncr_rate": ncr_rate,
            "project_in_progress": project_in_progress,
            "project_overdue": project_overdue,
            "docs_active": docs_active,
            "docs_review_needed": docs_review_needed,
        },
        "personnel": {
            "auth_expiring": auth_expiring,
            "auth_expired": auth_expired,
            "dept_distribution": dept_data,
            "auth_status_distribution": auth_status_data,
        },
        "equipment": {
            "repairing": repairing_equipment,
            "outsource": outsource_equipment,
            "cal_expiring": cal_expiring,
            "check_expiring": check_expiring,
            "status_distribution": eq_status_data,
        },
        "quality": {
            "qc_type_distribution": qc_type_data,
            "ncr_source_distribution": ncr_source_data,
            "ncr_closure_distribution": ncr_closure_data,
        },
        "detection": {
            "pending_reports": pending_reports,
            "status_distribution": project_status_data,
        },
        "document": {
            "level_distribution": doc_level_data,
            "status_distribution": doc_status_data,
        },
        "ncr": {
            "total": ncr_total,
            "closed": ncr_closed,
            "overdue": ncr_overdue,
        },
        "warnings": warnings,
    }
