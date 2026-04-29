import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, Date, Float, Enum, ForeignKey, DateTime, Boolean,
)
from sqlalchemy.orm import relationship

from app.database import Base


class PersonnelStatus(str, enum.Enum):
    active = "在职"
    resigned = "离职"
    retired = "退休"


class EquipmentStatus(str, enum.Enum):
    in_use = "在用"
    disabled = "停用"
    scrapped = "报废"
    repairing = "维修中"
    outsource = "外出"


class AuthStatus(str, enum.Enum):
    valid = "有效"
    pending_renewal = "待续期"
    expired = "已过期"
    suspended = "暂停"


class AuthType(str, enum.Enum):
    domain = "检测领域授权"
    equipment = "设备操作授权"


class TrainingResult(str, enum.Enum):
    passed = "合格"
    failed = "不合格"
    pending = "待评价"


class SupervisionResult(str, enum.Enum):
    satisfied = "满意"
    improve = "待改进"
    unsatisfied = "不满意"


class CalibrationConclusion(str, enum.Enum):
    qualified = "合格"
    unqualified = "不合格"
    degraded = "降级使用"


class CheckResult(str, enum.Enum):
    satisfied = "满意"
    unsatisfied = "不满意"
    suspicious = "可疑"


class QCType(str, enum.Enum):
    interlab = "实验室间比对"
    proficiency = "能力验证"
    retest = "留样再测"
    spike = "加标回收"
    personnel = "人员比对"
    equipment = "设备比对"
    duplicate = "平行样"
    control_chart = "控制图"


class ExecutionStatus(str, enum.Enum):
    pending = "待执行"
    executing = "执行中"
    completed = "已完成"
    cancelled = "已取消"


class ResultEvaluation(str, enum.Enum):
    satisfied = "满意"
    unsatisfied = "不满意"
    suspicious = "可疑"
    pending = "待评价"


class NCRSource(str, enum.Enum):
    internal_audit = "内审"
    management_review = "管评"
    daily_supervision = "日常监督"
    customer_complaint = "客户投诉"
    proficiency_unsatisfied = "能力验证不满意"
    external_audit = "外部评审"
    self_discovery = "自我发现"


class ClosureStatus(str, enum.Enum):
    to_analyze = "待分析"
    planning = "措施制定中"
    implementing = "实施中"
    to_verify = "待验证"
    closed = "已关闭"


class DocLevel(str, enum.Enum):
    manual = "一级手册"
    procedure = "二级程序"
    sop = "三级SOP"
    record = "四级记录"


class DocStatus(str, enum.Enum):
    effective = "现行有效"
    revising = "修订中"
    obsolete = "废止"
    pending_publish = "待发布"


class ProjectStatus(str, enum.Enum):
    accepting = "申请受理"
    contract_review = "合同评审"
    sample_receiving = "样品接收"
    testing = "检测执行"
    data_review = "数据复核"
    report_drafting = "报告编制"
    approving = "审批中"
    issued = "已发放"
    completed = "已完成"
    cancelled = "已取消"


class SampleStatus(str, enum.Enum):
    pending = "待检"
    testing = "在检"
    completed = "检毕"
    retained = "留样"
    disposed = "已处置"


class ReportStatus(str, enum.Enum):
    drafting = "编制中"
    pending_approval = "待审批"
    approved = "已批准"
    issued = "已发放"
    revised = "已更改"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    display_name = Column(String(50), nullable=False)
    role = Column(String(20), default="viewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class Personnel(Base):
    __tablename__ = "personnel"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(50), nullable=False)
    position = Column(String(50))
    department = Column(String(50), index=True)
    hire_date = Column(Date)
    status = Column(Enum(PersonnelStatus), default=PersonnelStatus.active)
    email = Column(String(100))
    phone = Column(String(20))
    education = Column(Text)
    specialty = Column(Text)
    remark = Column(Text)

    authorizations = relationship("Authorization", back_populates="personnel", cascade="all, delete-orphan")
    trainings = relationship("Training", back_populates="personnel", cascade="all, delete-orphan")
    supervisions = relationship("Supervision", back_populates="personnel", cascade="all, delete-orphan")


class Authorization(Base):
    __tablename__ = "authorizations"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id"), nullable=False)
    auth_type = Column(Enum(AuthType), nullable=False)
    auth_name = Column(String(200), nullable=False)
    auth_date = Column(Date)
    expire_date = Column(Date, index=True)
    status = Column(Enum(AuthStatus), default=AuthStatus.valid)
    cert_attachment = Column(String(500))
    reviewer = Column(String(50))
    next_supervision_date = Column(Date)

    personnel = relationship("Personnel", back_populates="authorizations")


class Training(Base):
    __tablename__ = "trainings"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id"), nullable=False)
    topic = Column(String(200), nullable=False)
    training_type = Column(String(20))
    training_date = Column(Date)
    duration_hours = Column(Float)
    result = Column(Enum(TrainingResult))
    instructor = Column(String(50))
    content = Column(Text)
    cert_attachment = Column(String(500))

    personnel = relationship("Personnel", back_populates="trainings")


class Supervision(Base):
    __tablename__ = "supervisions"

    id = Column(Integer, primary_key=True, index=True)
    personnel_id = Column(Integer, ForeignKey("personnel.id"), nullable=False)
    supervision_date = Column(Date)
    supervision_type = Column(String(20))
    content = Column(Text)
    result = Column(Enum(SupervisionResult))
    improvement_requirement = Column(Text)
    supervisor = Column(String(50))
    improvement_deadline = Column(Date)
    verifier = Column(String(50))
    verify_result = Column(String(10))

    personnel = relationship("Personnel", back_populates="supervisions")


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    model = Column(String(100))
    manufacturer = Column(String(100))
    asset_tag = Column(String(50))
    location = Column(String(100))
    custodian = Column(String(50))
    status = Column(Enum(EquipmentStatus), default=EquipmentStatus.in_use, index=True)
    acceptance_date = Column(Date)
    commission_date = Column(Date)
    scrap_date = Column(Date)
    sop_link = Column(String(500))
    remark = Column(Text)

    calibrations = relationship("Calibration", back_populates="equipment", cascade="all, delete-orphan")
    checks = relationship("Check", back_populates="equipment", cascade="all, delete-orphan")
    maintenance = relationship("Maintenance", back_populates="equipment", cascade="all, delete-orphan")


class Calibration(Base):
    __tablename__ = "calibrations"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    cal_date = Column(Date)
    cal_org = Column(String(100))
    cert_number = Column(String(50))
    conclusion = Column(Enum(CalibrationConclusion))
    next_cal_date = Column(Date, index=True)
    cert_attachment = Column(String(500))
    cost = Column(Float)
    remark = Column(Text)

    equipment = relationship("Equipment", back_populates="calibrations")


class Check(Base):
    __tablename__ = "checks"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    check_date = Column(Date)
    check_item = Column(String(200))
    check_method = Column(String(200))
    result = Column(Enum(CheckResult))
    conclusion = Column(Text)
    checker = Column(String(50))
    next_check_date = Column(Date, index=True)
    remark = Column(Text)

    equipment = relationship("Equipment", back_populates="checks")


class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    maintain_date = Column(Date)
    maintain_type = Column(String(20))
    items = Column(Text)
    result = Column(String(20))
    maintainer = Column(String(50))
    cost = Column(Float)
    next_maintain_date = Column(Date)
    remark = Column(Text)

    equipment = relationship("Equipment", back_populates="maintenance")


class QualityControl(Base):
    __tablename__ = "quality_controls"

    id = Column(Integer, primary_key=True, index=True)
    qc_number = Column(String(20), unique=True, index=True, nullable=False)
    qc_type = Column(Enum(QCType), nullable=False)
    test_items = Column(String(500))
    plan_date = Column(Date)
    actual_date = Column(Date)
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.pending)
    responsible_person = Column(String(50))
    result_evaluation = Column(Enum(ResultEvaluation))
    ncr_id = Column(Integer, nullable=True)
    related_qp = Column(String(100))
    remark = Column(Text)


class InternalAudit(Base):
    __tablename__ = "internal_audits"

    id = Column(Integer, primary_key=True, index=True)
    audit_number = Column(String(20), unique=True, index=True, nullable=False)
    audit_year = Column(Integer, nullable=False)
    audit_round = Column(String(20))
    plan_date = Column(Date)
    actual_date = Column(Date)
    lead_auditor = Column(String(50))
    auditors = Column(String(200))
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.pending)
    audited_departments = Column(String(200))
    ncr_count = Column(Integer, default=0)
    report_attachment = Column(String(500))
    related_qp = Column(String(100))
    remark = Column(Text)


class ManagementReview(Base):
    __tablename__ = "management_reviews"

    id = Column(Integer, primary_key=True, index=True)
    mr_number = Column(String(20), unique=True, index=True, nullable=False)
    review_year = Column(Integer, nullable=False)
    plan_date = Column(Date)
    actual_date = Column(Date)
    host = Column(String(50))
    participants = Column(String(200))
    status = Column(Enum(ExecutionStatus), default=ExecutionStatus.pending)
    input_prev_review = Column(Boolean, default=False)
    input_audit_result = Column(Boolean, default=False)
    input_qc_result = Column(Boolean, default=False)
    input_training = Column(Boolean, default=False)
    input_calibration = Column(Boolean, default=False)
    input_customer = Column(Boolean, default=False)
    input_ncr = Column(Boolean, default=False)
    input_risk = Column(Boolean, default=False)
    output_decisions = Column(Text)
    improvement_count = Column(Integer, default=0)
    improvement_completed = Column(Integer, default=0)
    related_qp = Column(String(100))
    remark = Column(Text)


class DetectionProject(Base):
    __tablename__ = "detection_projects"

    id = Column(Integer, primary_key=True, index=True)
    project_number = Column(String(20), unique=True, index=True, nullable=False)
    project_name = Column(String(200), nullable=False)
    customer_name = Column(String(100))
    customer_contact = Column(String(50))
    customer_phone = Column(String(20))
    test_domain = Column(String(200))
    application_date = Column(Date)
    plan_complete_date = Column(Date, index=True)
    actual_complete_date = Column(Date)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.accepting, index=True)
    project_manager = Column(String(50))
    testers = Column(String(200))
    reviewers = Column(String(200))
    remark = Column(Text)

    methods = relationship("DetectionMethod", back_populates="project", cascade="all, delete-orphan")
    samples = relationship("Sample", back_populates="project", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="project", cascade="all, delete-orphan")


class DetectionMethod(Base):
    __tablename__ = "detection_methods"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("detection_projects.id"), nullable=False)
    standard = Column(String(100))
    method_name = Column(String(200))
    confirm_status = Column(String(20))
    confirm_date = Column(Date)
    confirmer = Column(String(50))
    remark = Column(Text)

    project = relationship("DetectionProject", back_populates="methods")


class Sample(Base):
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("detection_projects.id"), nullable=False)
    sample_name = Column(String(100))
    sample_number = Column(String(20))
    quantity = Column(String(50))
    specification = Column(String(100))
    receive_date = Column(Date)
    status = Column(Enum(SampleStatus), default=SampleStatus.pending)
    appearance = Column(Text)
    storage_condition = Column(String(20))
    dispose_date = Column(Date)
    dispose_method = Column(String(20))
    remark = Column(Text)

    project = relationship("DetectionProject", back_populates="samples")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("detection_projects.id"), nullable=False)
    report_number = Column(String(20))
    copies = Column(Integer)
    draft_date = Column(Date)
    approval_date = Column(Date)
    issue_date = Column(Date)
    issue_method = Column(String(20))
    status = Column(Enum(ReportStatus), default=ReportStatus.drafting)
    customer_sign = Column(String(10))
    satisfaction = Column(String(10))
    feedback = Column(Text)
    revise_reason = Column(Text)
    revise_report_number = Column(String(20))

    project = relationship("DetectionProject", back_populates="reports")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_number = Column(String(30), unique=True, index=True, nullable=False)
    doc_name = Column(String(200), nullable=False)
    doc_level = Column(Enum(DocLevel), nullable=False)
    cnas_chapter = Column(String(50), index=True)
    current_version = Column(String(10))
    effective_date = Column(Date)
    author = Column(String(50))
    reviewer = Column(String(50))
    approver = Column(String(50))
    distribution = Column(String(200))
    status = Column(Enum(DocStatus), default=DocStatus.effective, index=True)
    next_review_date = Column(Date, index=True)
    file_link = Column(String(500))
    obsolete_link = Column(String(500))
    remark = Column(Text)

    revisions = relationship("DocRevision", back_populates="document", cascade="all, delete-orphan")


class DocRevision(Base):
    __tablename__ = "doc_revisions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    version = Column(String(10))
    revision_date = Column(Date)
    revision_content = Column(Text)
    revision_reason = Column(Text)
    reviewer = Column(String(50))
    approver = Column(String(50))
    revisor = Column(String(50))

    document = relationship("Document", back_populates="revisions")


class NCR(Base):
    __tablename__ = "ncrs"

    id = Column(Integer, primary_key=True, index=True)
    ncr_number = Column(String(20), unique=True, index=True, nullable=False)
    source_type = Column(Enum(NCRSource), nullable=False)
    source_ref = Column(String(50))
    discovery_date = Column(Date)
    responsible_dept = Column(String(50))
    responsible_person = Column(String(50))
    description = Column(Text, nullable=False)
    cause_analysis = Column(Text)
    corrective_action = Column(Text)
    action_owner = Column(String(50))
    plan_complete_date = Column(Date, index=True)
    actual_complete_date = Column(Date)
    verifier = Column(String(50))
    verify_date = Column(Date)
    verify_result = Column(String(10))
    closure_status = Column(Enum(ClosureStatus), default=ClosureStatus.to_analyze, index=True)
    related_qp = Column(String(100))
    remark = Column(Text)


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    alert_type = Column(String(50))
    table_name = Column(String(50))
    field_name = Column(String(50))
    condition_expr = Column(String(200))
    threshold_days = Column(Integer)
    message_template = Column(Text)
    is_active = Column(Boolean, default=True)
