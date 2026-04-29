import csv
import io
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth import get_current_user
from app.models.models import User, Personnel, Equipment, Document, NCR, QualityControl

router = APIRouter(prefix="/import", tags=["数据导入"])


TABLE_MODEL_MAP = {
    "01_人员资质管理": Personnel,
    "02_设备生命周期管理": Equipment,
    "05_文件控制管理": Document,
    "06_不符合纠正措施": NCR,
    "03_1_质量控制计划": QualityControl,
}

FIELD_MAPS = {
    "01_人员资质管理": {
        "工号": "employee_id", "姓名": "name", "岗位": "position",
        "所属部门": "department", "入职日期": "hire_date", "人员状态": "status",
        "联系邮箱": "email", "联系电话": "phone", "教育背景": "education",
        "专业特长": "specialty", "备注": "remark",
    },
    "02_设备生命周期管理": {
        "设备编号": "equipment_id", "设备名称": "name", "设备型号": "model",
        "制造商": "manufacturer", "资产标签": "asset_tag", "存放位置": "location",
        "责任人": "custodian", "设备状态": "status", "验收日期": "acceptance_date",
        "启用日期": "commission_date", "报废日期": "scrap_date",
        "操作SOP链接": "sop_link", "备注": "remark",
    },
    "05_文件控制管理": {
        "文件编号": "doc_number", "文件名称": "doc_name", "文件层级": "doc_level",
        "对应CNAS章节": "cnas_chapter", "当前版本": "current_version",
        "生效日期": "effective_date", "编制人": "author", "审核人": "reviewer",
        "批准人": "approver", "分发范围": "distribution", "文件状态": "status",
        "下次评审日期": "next_review_date", "文件链接": "file_link",
        "作废文件链接": "obsolete_link", "备注": "remark",
    },
    "06_不符合纠正措施": {
        "不符合项编号": "ncr_number", "来源类型": "source_type",
        "来源活动": "source_ref", "发现日期": "discovery_date",
        "责任部门": "responsible_dept", "责任人": "responsible_person",
        "不符合描述": "description", "原因分析": "cause_analysis",
        "纠正措施": "corrective_action", "措施负责人": "action_owner",
        "计划完成日期": "plan_complete_date", "实际完成日期": "actual_complete_date",
        "验证人": "verifier", "验证日期": "verify_date",
        "验证结果": "verify_result", "闭环状态": "closure_status",
        "关联程序文件": "related_qp", "备注": "remark",
    },
    "03_1_质量控制计划": {
        "质控编号": "qc_number", "质控类型": "qc_type",
        "涉及检测项目": "test_items", "计划执行日期": "plan_date",
        "实际执行日期": "actual_date", "执行状态": "status",
        "质控负责人": "responsible_person", "结果评价": "result_evaluation",
        "不符合项编号": "ncr_id", "关联程序文件": "related_qp", "备注": "remark",
    },
}


@router.post("/{table_name}")
async def import_csv(
    table_name: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if table_name not in TABLE_MODEL_MAP:
        raise HTTPException(status_code=400, detail=f"不支持的表: {table_name}")

    model = TABLE_MODEL_MAP[table_name]
    field_map = FIELD_MAPS.get(table_name, {})

    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    imported = 0
    errors = []

    for i, row in enumerate(reader):
        mapped = {}
        for cn_name, db_field in field_map.items():
            val = row.get(cn_name, "").strip() if row.get(cn_name) else None
            if val:
                mapped[db_field] = val
        if not mapped:
            continue
        try:
            item = model(**mapped)
            db.add(item)
            imported += 1
        except Exception as e:
            errors.append(f"行{i+2}: {str(e)}")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"导入失败: {str(e)}")

    return {"imported": imported, "errors": errors}
