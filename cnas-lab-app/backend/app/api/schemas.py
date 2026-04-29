from typing import Optional, List
from datetime import date
from pydantic import BaseModel

from app.models.models import (
    Personnel, Authorization, Training, Supervision,
    Equipment, Calibration, Check, Maintenance,
    QualityControl, InternalAudit, ManagementReview,
    DetectionProject, DetectionMethod, Sample, Report,
    Document, DocRevision,
    NCR,
)


class PersonnelCreate(BaseModel):
    employee_id: str
    name: str
    position: Optional[str] = None
    department: Optional[str] = None
    hire_date: Optional[date] = None
    status: Optional[str] = "在职"
    email: Optional[str] = None
    phone: Optional[str] = None
    education: Optional[str] = None
    specialty: Optional[str] = None
    remark: Optional[str] = None


class PersonnelUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    hire_date: Optional[date] = None
    status: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education: Optional[str] = None
    specialty: Optional[str] = None
    remark: Optional[str] = None


class PersonnelResponse(BaseModel):
    id: int
    employee_id: str
    name: str
    position: Optional[str] = None
    department: Optional[str] = None
    hire_date: Optional[date] = None
    status: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    education: Optional[str] = None
    specialty: Optional[str] = None
    remark: Optional[str] = None

    class Config:
        from_attributes = True


class AuthorizationCreate(BaseModel):
    personnel_id: int
    auth_type: str
    auth_name: str
    auth_date: Optional[date] = None
    expire_date: Optional[date] = None
    status: Optional[str] = "有效"
    cert_attachment: Optional[str] = None
    reviewer: Optional[str] = None
    next_supervision_date: Optional[date] = None


class AuthorizationUpdate(BaseModel):
    auth_type: Optional[str] = None
    auth_name: Optional[str] = None
    auth_date: Optional[date] = None
    expire_date: Optional[date] = None
    status: Optional[str] = None
    cert_attachment: Optional[str] = None
    reviewer: Optional[str] = None
    next_supervision_date: Optional[date] = None


class AuthorizationResponse(BaseModel):
    id: int
    personnel_id: int
    auth_type: Optional[str] = None
    auth_name: Optional[str] = None
    auth_date: Optional[date] = None
    expire_date: Optional[date] = None
    status: Optional[str] = None
    cert_attachment: Optional[str] = None
    reviewer: Optional[str] = None
    next_supervision_date: Optional[date] = None

    class Config:
        from_attributes = True


class TrainingCreate(BaseModel):
    personnel_id: int
    topic: str
    training_type: Optional[str] = None
    training_date: Optional[date] = None
    duration_hours: Optional[float] = None
    result: Optional[str] = None
    instructor: Optional[str] = None
    content: Optional[str] = None
    cert_attachment: Optional[str] = None


class TrainingUpdate(BaseModel):
    topic: Optional[str] = None
    training_type: Optional[str] = None
    training_date: Optional[date] = None
    duration_hours: Optional[float] = None
    result: Optional[str] = None
    instructor: Optional[str] = None
    content: Optional[str] = None
    cert_attachment: Optional[str] = None


class TrainingResponse(BaseModel):
    id: int
    personnel_id: int
    topic: Optional[str] = None
    training_type: Optional[str] = None
    training_date: Optional[date] = None
    duration_hours: Optional[float] = None
    result: Optional[str] = None
    instructor: Optional[str] = None
    content: Optional[str] = None
    cert_attachment: Optional[str] = None

    class Config:
        from_attributes = True


class SupervisionCreate(BaseModel):
    personnel_id: int
    supervision_date: Optional[date] = None
    supervision_type: Optional[str] = None
    content: Optional[str] = None
    result: Optional[str] = None
    improvement_requirement: Optional[str] = None
    supervisor: Optional[str] = None
    improvement_deadline: Optional[date] = None
    verifier: Optional[str] = None
    verify_result: Optional[str] = None


class SupervisionUpdate(BaseModel):
    supervision_date: Optional[date] = None
    supervision_type: Optional[str] = None
    content: Optional[str] = None
    result: Optional[str] = None
    improvement_requirement: Optional[str] = None
    supervisor: Optional[str] = None
    improvement_deadline: Optional[date] = None
    verifier: Optional[str] = None
    verify_result: Optional[str] = None


class SupervisionResponse(BaseModel):
    id: int
    personnel_id: int
    supervision_date: Optional[date] = None
    supervision_type: Optional[str] = None
    content: Optional[str] = None
    result: Optional[str] = None
    improvement_requirement: Optional[str] = None
    supervisor: Optional[str] = None
    improvement_deadline: Optional[date] = None
    verifier: Optional[str] = None
    verify_result: Optional[str] = None

    class Config:
        from_attributes = True


class EquipmentCreate(BaseModel):
    equipment_id: str
    name: str
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    asset_tag: Optional[str] = None
    location: Optional[str] = None
    custodian: Optional[str] = None
    status: Optional[str] = "在用"
    acceptance_date: Optional[date] = None
    commission_date: Optional[date] = None
    scrap_date: Optional[date] = None
    sop_link: Optional[str] = None
    remark: Optional[str] = None


class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    asset_tag: Optional[str] = None
    location: Optional[str] = None
    custodian: Optional[str] = None
    status: Optional[str] = None
    acceptance_date: Optional[date] = None
    commission_date: Optional[date] = None
    scrap_date: Optional[date] = None
    sop_link: Optional[str] = None
    remark: Optional[str] = None


class EquipmentResponse(BaseModel):
    id: int
    equipment_id: str
    name: str
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    asset_tag: Optional[str] = None
    location: Optional[str] = None
    custodian: Optional[str] = None
    status: Optional[str] = None
    acceptance_date: Optional[date] = None
    commission_date: Optional[date] = None
    scrap_date: Optional[date] = None
    sop_link: Optional[str] = None
    remark: Optional[str] = None

    class Config:
        from_attributes = True


class CalibrationCreate(BaseModel):
    equipment_id: int
    cal_date: Optional[date] = None
    cal_org: Optional[str] = None
    cert_number: Optional[str] = None
    conclusion: Optional[str] = None
    next_cal_date: Optional[date] = None
    cert_attachment: Optional[str] = None
    cost: Optional[float] = None
    remark: Optional[str] = None


class CalibrationUpdate(BaseModel):
    cal_date: Optional[date] = None
    cal_org: Optional[str] = None
    cert_number: Optional[str] = None
    conclusion: Optional[str] = None
    next_cal_date: Optional[date] = None
    cert_attachment: Optional[str] = None
    cost: Optional[float] = None
    remark: Optional[str] = None


class CalibrationResponse(BaseModel):
    id: int
    equipment_id: int
    cal_date: Optional[date] = None
    cal_org: Optional[str] = None
    cert_number: Optional[str] = None
    conclusion: Optional[str] = None
    next_cal_date: Optional[date] = None
    cert_attachment: Optional[str] = None
    cost: Optional[float] = None
    remark: Optional[str] = None

    class Config:
        from_attributes = True


class CheckCreate(BaseModel):
    equipment_id: int
    check_date: Optional[date] = None
    check_item: Optional[str] = None
    check_method: Optional[str] = None
    result: Optional[str] = None
    conclusion: Optional[str] = None
    checker: Optional[str] = None
    next_check_date: Optional[date] = None
    remark: Optional[str] = None


class CheckUpdate(BaseModel):
    check_date: Optional[date] = None
    check_item: Optional[str] = None
    check_method: Optional[str] = None
    result: Optional[str] = None
    conclusion: Optional[str] = None
    checker: Optional[str] = None
    next_check_date: Optional[date] = None
    remark: Optional[str] = None


class CheckResponse(BaseModel):
    id: int
    equipment_id: int
    check_date: Optional[date] = None
    check_item: Optional[str] = None
    check_method: Optional[str] = None
    result: Optional[str] = None
    conclusion: Optional[str] = None
    checker: Optional[str] = None
    next_check_date: Optional[date] = None
    remark: Optional[str] = None

    class Config:
        from_attributes = True


class MaintenanceCreate(BaseModel):
    equipment_id: int
    maintain_date: Optional[date] = None
    maintain_type: Optional[str] = None
    items: Optional[str] = None
    result: Optional[str] = None
    maintainer: Optional[str] = None
    cost: Optional[float] = None
    next_maintain_date: Optional[date] = None
    remark: Optional[str] = None


class MaintenanceUpdate(BaseModel):
    maintain_date: Optional[date] = None
    maintain_type: Optional[str] = None
    items: Optional[str] = None
    result: Optional[str] = None
    maintainer: Optional[str] = None
    cost: Optional[float] = None
    next_maintain_date: Optional[date] = None
    remark: Optional[str] = None


class MaintenanceResponse(BaseModel):
    id: int
    equipment_id: int
    maintain_date: Optional[date] = None
    maintain_type: Optional[str] = None
    items: Optional[str] = None
    result: Optional[str] = None
    maintainer: Optional[str] = None
    cost: Optional[float] = None
    next_maintain_date: Optional[date] = None
    remark: Optional[str] = None

    class Config:
        from_attributes = True


class QCCreate(BaseModel):
    qc_number: str
    qc_type: str
    test_items: Optional[str] = None
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: Optional[str] = "待执行"
    responsible_person: Optional[str] = None
    result_evaluation: Optional[str] = None
    ncr_id: Optional[int] = None
    related_qp: Optional[str] = None
    remark: Optional[str] = None


class QCUpdate(BaseModel):
    qc_type: Optional[str] = None
    test_items: Optional[str] = None
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: Optional[str] = None
    responsible_person: Optional[str] = None
    result_evaluation: Optional[str] = None
    ncr_id: Optional[int] = None
    related_qp: Optional[str] = None
    remark: Optional[str] = None


class QCResponse(BaseModel):
    id: int
    qc_number: str
    qc_type: Optional[str] = None
    test_items: Optional[str] = None
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: Optional[str] = None
    responsible_person: Optional[str] = None
    result_evaluation: Optional[str] = None
    ncr_id: Optional[int] = None
    related_qp: Optional[str] = None
    remark: Optional[str] = None

    class Config:
        from_attributes = True


class AuditCreate(BaseModel):
    audit_number: str
    audit_year: int
    audit_round: Optional[str] = None
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    lead_auditor: Optional[str] = None
    auditors: Optional[str] = None
    status: Optional[str] = "计划中"
    audited_departments: Optional[str] = None
    ncr_count: Optional[int] = 0
    report_attachment: Optional[str] = None
    related_qp: Optional[str] = None
    remark: Optional[str] = None


class AuditUpdate(BaseModel):
    audit_year: Optional[int] = None
    audit_round: Optional[str] = None
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    lead_auditor: Optional[str] = None
    auditors: Optional[str] = None
    status: Optional[str] = None
    audited_departments: Optional[str] = None
    ncr_count: Optional[int] = None
    report_attachment: Optional[str] = None
    related_qp: Optional[str] = None
    remark: Optional[str] = None


class AuditResponse(BaseModel):
    id: int
    audit_number: str
    audit_year: Optional[int] = None
    audit_round: Optional[str] = None
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    lead_auditor: Optional[str] = None
    auditors: Optional[str] = None
    status: Optional[str] = None
    audited_departments: Optional[str] = None
    ncr_count: Optional[int] = None
    report_attachment: Optional[str] = None
    related_qp: Optional[str] = None
    remark: Optional[str] = None

    class Config:
        from_attributes = True


class MRCreate(BaseModel):
    mr_number: str
    review_year: int
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    host: Optional[str] = None
    participants: Optional[str] = None
    status: Optional[str] = "计划中"
    input_prev_review: Optional[bool] = False
    input_audit_result: Optional[bool] = False
    input_qc_result: Optional[bool] = False
    input_training: Optional[bool] = False
    input_calibration: Optional[bool] = False
    input_customer: Optional[bool] = False
    input_ncr: Optional[bool] = False
    input_risk: Optional[bool] = False
    output_decisions: Optional[str] = None
    improvement_count: Optional[int] = 0
    improvement_completed: Optional[int] = 0
    related_qp: Optional[str] = None
    remark: Optional[str] = None


class MRUpdate(BaseModel):
    review_year: Optional[int] = None
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    host: Optional[str] = None
    participants: Optional[str] = None
    status: Optional[str] = None
    input_prev_review: Optional[bool] = None
    input_audit_result: Optional[bool] = None
    input_qc_result: Optional[bool] = None
    input_training: Optional[bool] = None
    input_calibration: Optional[bool] = None
    input_customer: Optional[bool] = None
    input_ncr: Optional[bool] = None
    input_risk: Optional[bool] = None
    output_decisions: Optional[str] = None
    improvement_count: Optional[int] = None
    improvement_completed: Optional[int] = None
    related_qp: Optional[str] = None
    remark: Optional[str] = None


class MRResponse(BaseModel):
    id: int
    mr_number: str
    review_year: Optional[int] = None
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    host: Optional[str] = None
    participants: Optional[str] = None
    status: Optional[str] = None
    input_prev_review: Optional[bool] = None
    input_audit_result: Optional[bool] = None
    input_qc_result: Optional[bool] = None
    input_training: Optional[bool] = None
    input_calibration: Optional[bool] = None
    input_customer: Optional[bool] = None
    input_ncr: Optional[bool] = None
    input_risk: Optional[bool] = None
    output_decisions: Optional[str] = None
    improvement_count: Optional[int] = None
    improvement_completed: Optional[int] = None
    related_qp: Optional[str] = None
    remark: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    project_number: str
    project_name: str
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    customer_phone: Optional[str] = None
    test_domain: Optional[str] = None
    application_date: Optional[date] = None
    plan_complete_date: Optional[date] = None
    actual_complete_date: Optional[date] = None
    status: Optional[str] = "申请受理"
    project_manager: Optional[str] = None
    testers: Optional[str] = None
    reviewers: Optional[str] = None
    remark: Optional[str] = None


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    customer_phone: Optional[str] = None
    test_domain: Optional[str] = None
    application_date: Optional[date] = None
    plan_complete_date: Optional[date] = None
    actual_complete_date: Optional[date] = None
    status: Optional[str] = None
    project_manager: Optional[str] = None
    testers: Optional[str] = None
    reviewers: Optional[str] = None
    remark: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    project_number: str
    project_name: str
    customer_name: Optional[str] = None
    customer_contact: Optional[str] = None
    customer_phone: Optional[str] = None
    test_domain: Optional[str] = None
    application_date: Optional[date] = None
    plan_complete_date: Optional[date] = None
    actual_complete_date: Optional[date] = None
    status: Optional[str] = None
    project_manager: Optional[str] = None
    testers: Optional[str] = None
    reviewers: Optional[str] = None
    remark: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    doc_number: str
    doc_name: str
    doc_level: str
    cnas_chapter: Optional[str] = None
    current_version: Optional[str] = None
    effective_date: Optional[date] = None
    author: Optional[str] = None
    reviewer: Optional[str] = None
    approver: Optional[str] = None
    distribution: Optional[str] = None
    status: Optional[str] = "现行有效"
    next_review_date: Optional[date] = None
    file_link: Optional[str] = None
    obsolete_link: Optional[str] = None
    remark: Optional[str] = None


class DocumentUpdate(BaseModel):
    doc_name: Optional[str] = None
    doc_level: Optional[str] = None
    cnas_chapter: Optional[str] = None
    current_version: Optional[str] = None
    effective_date: Optional[date] = None
    author: Optional[str] = None
    reviewer: Optional[str] = None
    approver: Optional[str] = None
    distribution: Optional[str] = None
    status: Optional[str] = None
    next_review_date: Optional[date] = None
    file_link: Optional[str] = None
    obsolete_link: Optional[str] = None
    remark: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    doc_number: str
    doc_name: str
    doc_level: Optional[str] = None
    cnas_chapter: Optional[str] = None
    current_version: Optional[str] = None
    effective_date: Optional[date] = None
    author: Optional[str] = None
    reviewer: Optional[str] = None
    approver: Optional[str] = None
    distribution: Optional[str] = None
    status: Optional[str] = None
    next_review_date: Optional[date] = None
    file_link: Optional[str] = None
    obsolete_link: Optional[str] = None
    remark: Optional[str] = None

    class Config:
        from_attributes = True


class NCRCreate(BaseModel):
    ncr_number: str
    source_type: str
    source_ref: Optional[str] = None
    discovery_date: Optional[date] = None
    responsible_dept: Optional[str] = None
    responsible_person: Optional[str] = None
    description: str
    cause_analysis: Optional[str] = None
    corrective_action: Optional[str] = None
    action_owner: Optional[str] = None
    plan_complete_date: Optional[date] = None
    actual_complete_date: Optional[date] = None
    verifier: Optional[str] = None
    verify_date: Optional[date] = None
    verify_result: Optional[str] = None
    closure_status: Optional[str] = "待分析"
    related_qp: Optional[str] = None
    remark: Optional[str] = None


class NCRUpdate(BaseModel):
    source_type: Optional[str] = None
    source_ref: Optional[str] = None
    discovery_date: Optional[date] = None
    responsible_dept: Optional[str] = None
    responsible_person: Optional[str] = None
    description: Optional[str] = None
    cause_analysis: Optional[str] = None
    corrective_action: Optional[str] = None
    action_owner: Optional[str] = None
    plan_complete_date: Optional[date] = None
    actual_complete_date: Optional[date] = None
    verifier: Optional[str] = None
    verify_date: Optional[date] = None
    verify_result: Optional[str] = None
    closure_status: Optional[str] = None
    related_qp: Optional[str] = None
    remark: Optional[str] = None


class NCRResponse(BaseModel):
    id: int
    ncr_number: str
    source_type: Optional[str] = None
    source_ref: Optional[str] = None
    discovery_date: Optional[date] = None
    responsible_dept: Optional[str] = None
    responsible_person: Optional[str] = None
    description: Optional[str] = None
    cause_analysis: Optional[str] = None
    corrective_action: Optional[str] = None
    action_owner: Optional[str] = None
    plan_complete_date: Optional[date] = None
    actual_complete_date: Optional[date] = None
    verifier: Optional[str] = None
    verify_date: Optional[date] = None
    verify_result: Optional[str] = None
    closure_status: Optional[str] = None
    related_qp: Optional[str] = None
    remark: Optional[str] = None

    class Config:
        from_attributes = True
