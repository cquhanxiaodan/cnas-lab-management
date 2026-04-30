import csv
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine, Base
from app.models.models import (
    Personnel, Authorization, Training, Supervision,
    Equipment, Calibration, Check, Maintenance,
    QualityControl, InternalAudit, ManagementReview,
    DetectionProject, DetectionMethod, Sample, Report,
    Document, DocRevision, NCR,
)

CSV_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "cnas-csv-templates")


def to_date(val):
    if not val:
        return None
    try:
        from datetime import datetime as dt
        return dt.strptime(val, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def read_csv(filename):
    filepath = os.path.join(CSV_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  SKIP: {filename} not found")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            cleaned = {}
            for k, v in row.items():
                if k is None:
                    continue
                cleaned[k] = v.strip() if v and v.strip() else None
            if any(cleaned.values()):
                rows.append(cleaned)
        return rows


def import_personnel(db):
    rows = read_csv("01_人员资质管理.csv")
    for r in rows:
        p = Personnel(
            employee_id=r.get("工号"),
            name=r.get("姓名"),
            position=r.get("岗位"),
            department=r.get("所属部门"),
            hire_date=to_date(r.get("入职日期")),
            status=r.get("人员状态", "在职"),
            email=r.get("联系邮箱"),
            phone=r.get("联系电话"),
            education=r.get("教育背景"),
            specialty=r.get("专业特长"),
            remark=r.get("备注"),
        )
        db.add(p)
    db.flush()
    print(f"  Personnel: {len(rows)} rows")

    sub = read_csv("01_1_资质授权.csv")
    for r in sub:
        pid = db.query(Personnel).filter(Personnel.employee_id == r.get("工号")).first()
        if not pid:
            continue
        a = Authorization(
            personnel_id=pid.id,
            auth_type=r.get("授权类型"),
            auth_name=r.get("授权名称"),
            auth_date=to_date(r.get("授权日期")),
            expire_date=to_date(r.get("有效期至")),
            status=r.get("授权状态"),
            reviewer=r.get("复核人"),
            next_supervision_date=to_date(r.get("下次监督日期")),
        )
        db.add(a)
    print(f"  Authorizations: {len(sub)} rows")

    sub = read_csv("01_2_培训记录.csv")
    for r in sub:
        pid = db.query(Personnel).filter(Personnel.employee_id == r.get("工号")).first()
        if not pid:
            continue
        t = Training(
            personnel_id=pid.id,
            topic=r.get("培训主题"),
            training_type=r.get("培训类型"),
            training_date=to_date(r.get("培训日期")),
            duration_hours=float(r.get("培训时长(小时)") or 0),
            result=r.get("培训结果"),
            instructor=r.get("培训讲师"),
            content=r.get("培训内容"),
        )
        db.add(t)
    print(f"  Trainings: {len(sub)} rows")

    sub = read_csv("01_3_监督记录.csv")
    for r in sub:
        pid = db.query(Personnel).filter(Personnel.employee_id == r.get("工号")).first()
        if not pid:
            continue
        s = Supervision(
            personnel_id=pid.id,
            supervision_date=to_date(r.get("监督日期")),
            supervision_type=r.get("监督类型"),
            content=r.get("监督内容"),
            result=r.get("监督结果"),
            improvement_requirement=r.get("改进要求"),
            supervisor=r.get("监督人"),
            improvement_deadline=to_date(r.get("改进完成日期")),
            verifier=r.get("验证人"),
            verify_result=r.get("验证结果"),
        )
        db.add(s)
    print(f"  Supervisions: {len(sub)} rows")


def import_equipment(db):
    rows = read_csv("02_设备生命周期管理.csv")
    for r in rows:
        e = Equipment(
            equipment_id=r.get("设备编号"),
            name=r.get("设备名称"),
            model=r.get("设备型号"),
            manufacturer=r.get("制造商"),
            asset_tag=r.get("资产标签"),
            location=r.get("存放位置"),
            custodian=r.get("责任人"),
            status=r.get("设备状态", "在用"),
            acceptance_date=to_date(r.get("验收日期")),
            commission_date=to_date(r.get("启用日期")),
            sop_link=r.get("操作SOP链接"),
            remark=r.get("备注"),
        )
        db.add(e)
    db.flush()
    print(f"  Equipment: {len(rows)} rows")

    sub = read_csv("02_1_校准记录.csv")
    for r in sub:
        eid = db.query(Equipment).filter(Equipment.equipment_id == r.get("设备编号")).first()
        if not eid:
            continue
        c = Calibration(
            equipment_id=eid.id,
            cal_date=to_date(r.get("校准日期")),
            cal_org=r.get("校准机构"),
            cert_number=r.get("校准证书编号"),
            conclusion=r.get("校准结论"),
            next_cal_date=to_date(r.get("下次校准日期")),
            cost=float(r.get("校准费用(元)") or 0),
            remark=r.get("备注"),
        )
        db.add(c)
    print(f"  Calibrations: {len(sub)} rows")

    sub = read_csv("02_2_期间核查记录.csv")
    for r in sub:
        eid = db.query(Equipment).filter(Equipment.equipment_id == r.get("设备编号")).first()
        if not eid:
            continue
        c = Check(
            equipment_id=eid.id,
            check_date=to_date(r.get("核查日期")),
            check_item=r.get("核查项目"),
            check_method=r.get("核查方法"),
            result=r.get("核查结果"),
            conclusion=r.get("核查结论"),
            checker=r.get("核查人"),
            next_check_date=to_date(r.get("下次核查日期")),
            remark=r.get("备注"),
        )
        db.add(c)
    print(f"  Checks: {len(sub)} rows")

    sub = read_csv("02_3_维护记录.csv")
    for r in sub:
        eid = db.query(Equipment).filter(Equipment.equipment_id == r.get("设备编号")).first()
        if not eid:
            continue
        m = Maintenance(
            equipment_id=eid.id,
            maintain_date=to_date(r.get("维护日期")),
            maintain_type=r.get("维护类型"),
            items=r.get("维护项目"),
            result=r.get("维护结果"),
            maintainer=r.get("维护人"),
            cost=float(r.get("维护费用(元)") or 0),
            next_maintain_date=to_date(r.get("下次维护日期")),
            remark=r.get("备注"),
        )
        db.add(m)
    print(f"  Maintenance: {len(sub)} rows")


def import_quality(db):
    rows = read_csv("03_1_质量控制计划.csv")
    for r in rows:
        q = QualityControl(
            qc_number=r.get("质控编号"),
            qc_type=r.get("质控类型"),
            test_items=r.get("涉及检测项目"),
            plan_date=to_date(r.get("计划执行日期")),
            actual_date=to_date(r.get("实际执行日期")),
            status=r.get("执行状态", "待执行"),
            responsible_person=r.get("质控负责人"),
            result_evaluation=r.get("结果评价"),
            related_qp=r.get("关联程序文件"),
            remark=r.get("备注"),
        )
        db.add(q)
    print(f"  QualityControl: {len(rows)} rows")

    rows = read_csv("03_2_内部审核.csv")
    for r in rows:
        a = InternalAudit(
            audit_number=r.get("内审编号"),
            audit_year=int(r.get("审核年度") or 2026),
            audit_round=r.get("审核轮次"),
            plan_date=to_date(r.get("计划审核日期")),
            actual_date=to_date(r.get("实际审核日期")),
            lead_auditor=r.get("审核组长"),
            auditors=r.get("审核员"),
            status=r.get("审核状态", "计划中"),
            audited_departments=r.get("受审核部门"),
            ncr_count=int(r.get("不符合项数量") or 0),
            related_qp=r.get("关联程序文件"),
            remark=r.get("备注"),
        )
        db.add(a)
    print(f"  InternalAudit: {len(rows)} rows")

    rows = read_csv("03_3_管理评审.csv")
    for r in rows:
        m = ManagementReview(
            mr_number=r.get("管评编号"),
            review_year=int(r.get("评审年度") or 2026),
            plan_date=to_date(r.get("计划评审日期")),
            actual_date=to_date(r.get("实际评审日期")),
            host=r.get("主持人"),
            participants=r.get("参与人员"),
            status=r.get("评审状态", "计划中"),
            input_prev_review=r.get("输入材料-上次管评决议跟踪") == "已提交",
            input_audit_result=r.get("输入材料-内审结果") == "已提交",
            input_qc_result=r.get("输入材料-质量控制活动结果") == "已提交",
            input_training=r.get("输入材料-人员培训情况") == "已提交",
            input_calibration=r.get("输入材料-设备校准和核查情况") == "已提交",
            input_customer=r.get("输入材料-客户反馈和投诉") == "已提交",
            input_ncr=r.get("输入材料-不符合项和纠正措施") == "已提交",
            input_risk=r.get("输入材料-风险和机遇") == "已提交",
            output_decisions=r.get("输出决议"),
            improvement_count=int(r.get("改进事项数量") or 0),
            improvement_completed=0,
            related_qp=r.get("关联程序文件"),
            remark=r.get("备注"),
        )
        db.add(m)
    print(f"  ManagementReview: {len(rows)} rows")


def import_detection(db):
    rows = read_csv("04_检测业务管理.csv")
    for r in rows:
        d = DetectionProject(
            project_number=r.get("项目编号"),
            project_name=r.get("项目名称"),
            customer_name=r.get("客户名称"),
            customer_contact=r.get("客户联系人"),
            customer_phone=r.get("客户联系电话"),
            test_domain=r.get("检测领域"),
            application_date=to_date(r.get("申请日期")),
            plan_complete_date=to_date(r.get("计划完成日期")),
            actual_complete_date=to_date(r.get("实际完成日期")),
            status=r.get("项目状态", "申请受理"),
            project_manager=r.get("项目负责人"),
            testers=r.get("检测人员"),
            reviewers=r.get("复核人员"),
            remark=r.get("备注"),
        )
        db.add(d)
    db.flush()
    print(f"  DetectionProject: {len(rows)} rows")

    sub = read_csv("04_1_检测方法.csv")
    for r in sub:
        pid = db.query(DetectionProject).filter(DetectionProject.project_number == r.get("项目编号")).first()
        if not pid:
            continue
        m = DetectionMethod(
            project_id=pid.id,
            standard=r.get("检测方法标准"),
            method_name=r.get("检测方法名称"),
            confirm_status=r.get("方法确认状态"),
            confirm_date=to_date(r.get("方法确认日期")),
            confirmer=r.get("方法确认人"),
            remark=r.get("备注"),
        )
        db.add(m)
    print(f"  DetectionMethod: {len(sub)} rows")

    sub = read_csv("04_2_样品记录.csv")
    for r in sub:
        pid = db.query(DetectionProject).filter(DetectionProject.project_number == r.get("项目编号")).first()
        if not pid:
            continue
        s = Sample(
            project_id=pid.id,
            sample_name=r.get("样品名称"),
            sample_number=r.get("样品编号"),
            quantity=r.get("样品数量"),
            specification=r.get("样品规格"),
            receive_date=to_date(r.get("接收日期")),
            status=r.get("样品状态", "待检"),
            appearance=r.get("接收时外观"),
            storage_condition=r.get("储存条件"),
            dispose_date=to_date(r.get("处置日期")),
            dispose_method=r.get("处置方式"),
            remark=r.get("备注"),
        )
        db.add(s)
    print(f"  Sample: {len(sub)} rows")

    sub = read_csv("04_3_报告记录.csv")
    for r in sub:
        pid = db.query(DetectionProject).filter(DetectionProject.project_number == r.get("项目编号")).first()
        if not pid:
            continue
        rp = Report(
            project_id=pid.id,
            report_number=r.get("报告编号"),
            copies=int(r.get("报告份数") or 0),
            draft_date=to_date(r.get("报告编制日期")),
            approval_date=to_date(r.get("报告审批日期")),
            issue_date=to_date(r.get("报告发放日期")),
            issue_method=r.get("报告发放方式"),
            status=r.get("报告状态", "编制中"),
            customer_sign=r.get("客户签收确认"),
            satisfaction=r.get("客户满意度"),
            feedback=r.get("客户反馈意见"),
            revise_reason=r.get("更改原因"),
            revise_report_number=r.get("更改报告编号"),
        )
        db.add(rp)
    print(f"  Report: {len(sub)} rows")


def import_documents(db):
    rows = read_csv("05_文件控制管理.csv")
    for r in rows:
        d = Document(
            doc_number=r.get("文件编号"),
            doc_name=r.get("文件名称"),
            doc_level=r.get("文件层级"),
            cnas_chapter=r.get("对应CNAS章节"),
            current_version=r.get("当前版本"),
            effective_date=to_date(r.get("生效日期")),
            author=r.get("编制人"),
            reviewer=r.get("审核人"),
            approver=r.get("批准人"),
            distribution=r.get("分发范围"),
            status=r.get("文件状态", "现行有效"),
            next_review_date=to_date(r.get("下次评审日期")),
            file_link=r.get("文件链接"),
            obsolete_link=r.get("作废文件链接"),
            remark=r.get("备注"),
        )
        db.add(d)
    db.flush()
    print(f"  Document: {len(rows)} rows")

    sub = read_csv("05_1_修订历史.csv")
    for r in sub:
        did = db.query(Document).filter(Document.doc_number == r.get("文件编号")).first()
        if not did:
            continue
        dr = DocRevision(
            document_id=did.id,
            version=r.get("修订版本"),
            revision_date=to_date(r.get("修订日期")),
            revision_content=r.get("修订内容"),
            revision_reason=r.get("修订原因"),
            reviewer=r.get("审核人"),
            approver=r.get("批准人"),
            revisor=r.get("修订人"),
        )
        db.add(dr)
    print(f"  DocRevision: {len(sub)} rows")


def import_ncr(db):
    rows = read_csv("06_不符合纠正措施.csv")
    for r in rows:
        n = NCR(
            ncr_number=r.get("不符合项编号"),
            source_type=r.get("来源类型"),
            source_ref=r.get("来源活动"),
            discovery_date=to_date(r.get("发现日期")),
            responsible_dept=r.get("责任部门"),
            responsible_person=r.get("责任人"),
            description=r.get("不符合描述"),
            cause_analysis=r.get("原因分析"),
            corrective_action=r.get("纠正措施"),
            action_owner=r.get("措施负责人"),
            plan_complete_date=to_date(r.get("计划完成日期")),
            actual_complete_date=to_date(r.get("实际完成日期")),
            verifier=r.get("验证人"),
            verify_date=to_date(r.get("验证日期")),
            verify_result=r.get("验证结果"),
            closure_status=r.get("闭环状态", "待分析"),
            related_qp=r.get("关联程序文件"),
            remark=r.get("备注"),
        )
        db.add(n)
    print(f"  NCR: {len(rows)} rows")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("Importing CSV data into database...")
        import_personnel(db)
        import_equipment(db)
        import_quality(db)
        import_detection(db)
        import_documents(db)
        import_ncr(db)

        db.commit()
        print("\nAll data imported successfully!")
    except Exception as e:
        db.rollback()
        print(f"\nImport failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
