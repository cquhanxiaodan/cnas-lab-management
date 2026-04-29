#!/usr/bin/env python3
"""
CNAS体系多维表 - 一键处理脚本
功能：
  1. 校验所有CSV数据完整性和格式
  2. 生成HTML仪表盘预览页面
  3. 合并主表+子表为钉钉多维表友好的格式
  4. 生成数据字典
"""

import csv
import os
import sys
import json
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from pathlib import Path

BASE_DIR = Path(__file__).parent

TABLE_DEFINITIONS = {
    "01_人员资质管理": {
        "name": "人员资质管理",
        "cnas": "6.2 人员",
        "sub_tables": ["01_1_资质授权", "01_2_培训记录", "01_3_监督记录"],
        "key_field": "工号",
    },
    "02_设备生命周期管理": {
        "name": "设备生命周期管理",
        "cnas": "6.4 设备 + 6.5 计量溯源",
        "sub_tables": ["02_1_校准记录", "02_2_期间核查记录", "02_3_维护记录"],
        "key_field": "设备编号",
    },
    "03_1_质量控制计划": {
        "name": "质量控制计划",
        "cnas": "7.7 结果有效性",
        "sub_tables": [],
        "key_field": "质控编号",
    },
    "03_2_内部审核": {
        "name": "内部审核",
        "cnas": "8.8 内部审核",
        "sub_tables": [],
        "key_field": "内审编号",
    },
    "03_3_管理评审": {
        "name": "管理评审",
        "cnas": "8.9 管理评审",
        "sub_tables": [],
        "key_field": "管评编号",
    },
    "04_检测业务管理": {
        "name": "检测业务管理",
        "cnas": "7.1~7.5 检测全流程",
        "sub_tables": ["04_1_检测方法", "04_2_样品记录", "04_3_报告记录"],
        "key_field": "项目编号",
    },
    "05_文件控制管理": {
        "name": "文件控制管理",
        "cnas": "8.3 文件控制 + 8.4 记录控制",
        "sub_tables": ["05_1_修订历史"],
        "key_field": "文件编号",
    },
    "06_不符合纠正措施": {
        "name": "不符合/纠正措施",
        "cnas": "7.10 不符合工作 + 8.7 纠正措施",
        "sub_tables": [],
        "key_field": "不符合项编号",
    },
    "07_基础数据配置": {
        "name": "基础数据配置",
        "cnas": "-",
        "sub_tables": [],
        "key_field": "配置项",
    },
}

SELECT_FIELDS = {
    "岗位": ["检测工程师", "质量负责人", "设备管理员", "文件管理员", "人事专员", "实验室主任", "技术负责人"],
    "所属部门": ["化学检测部", "物理检测部", "设备管理部", "质量管理部", "行政综合部"],
    "人员状态": ["在职", "离职", "退休"],
    "设备状态": ["在用", "停用", "报废", "维修中", "外出"],
    "授权状态": ["有效", "待续期", "已过期", "暂停"],
    "授权类型": ["检测领域授权", "设备操作授权"],
    "培训类型": ["内部培训", "外部培训", "在线学习"],
    "培训结果": ["合格", "不合格", "待评价"],
    "监督类型": ["现场监督", "报告审查", "样品考核"],
    "监督结果": ["满意", "待改进", "不满意"],
    "验证结果": ["通过", "不通过"],
    "校准结论": ["合格", "不合格", "降级使用"],
    "核查结果": ["满意", "不满意", "可疑"],
    "维护类型": ["日常维护", "定期维护", "故障维修"],
    "维护结果": ["正常", "异常", "待观察"],
    "质控类型": ["实验室间比对", "能力验证", "留样再测", "加标回收", "人员比对", "设备比对", "平行样", "控制图"],
    "执行状态": ["待执行", "执行中", "已完成", "已取消"],
    "结果评价": ["满意", "不满意", "可疑", "待评价"],
    "审核轮次": ["第一次", "第二次", "第三次", "专项审核"],
    "审核状态": ["计划中", "进行中", "已完成"],
    "评审状态": ["计划中", "已完成"],
    "方法确认状态": ["已确认", "待确认", "不适用"],
    "样品状态": ["待检", "在检", "检毕", "留样", "已处置"],
    "储存条件": ["室温", "冷藏", "冷冻", "其他"],
    "处置方式": ["归还", "销毁", "留样"],
    "报告状态": ["编制中", "待审批", "已批准", "已发放", "已更改"],
    "客户签收确认": ["已签收", "未签收"],
    "客户满意度": ["满意", "基本满意", "不满意"],
    "报告发放方式": ["自取", "邮寄", "电子版"],
    "文件层级": ["一级手册", "二级程序", "三级SOP", "四级记录"],
    "文件状态": ["现行有效", "修订中", "废止", "待发布"],
    "来源类型": ["内审", "管评", "日常监督", "客户投诉", "能力验证不满意", "外部评审", "自我发现"],
    "闭环状态": ["待分析", "措施制定中", "实施中", "待验证", "已关闭"],
}


def read_csv(filepath):
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def validate_csv(filepath):
    errors = []
    warnings = []
    rows = read_csv(filepath)
    filename = os.path.basename(filepath)
    table_key = filename.replace(".csv", "")

    if not rows:
        errors.append(f"[{filename}] 文件为空，没有数据行")
        return errors, warnings

    headers = list(rows[0].keys())

    for field_name, valid_values in SELECT_FIELDS.items():
        if field_name in headers:
            col_idx = headers.index(field_name)
            for i, row in enumerate(rows):
                val = row.get(field_name, "").strip()
                if not val:
                    continue
                if val not in valid_values:
                    errors.append(
                        f"[{filename}] 行{i+2} 字段'{field_name}'值'{val}'不在有效选项中: {valid_values}"
                    )

    for table_def_key, table_def in TABLE_DEFINITIONS.items():
        if table_key == table_def_key:
            key_field = table_def["key_field"]
            if key_field in headers:
                keys = [row[key_field] for row in rows if row.get(key_field)]
                dup_keys = [k for k, c in Counter(keys).items() if c > 1]
                if dup_keys:
                    warnings.append(
                        f"[{filename}] 主键字段'{key_field}'存在重复值: {dup_keys}"
                    )

    for i, row in enumerate(rows):
        for h in headers:
            val = row.get(h)
            if val is None or isinstance(val, list):
                continue
            val = str(val).strip()
            if "日期" in h and val:
                try:
                    datetime.strptime(val, "%Y-%m-%d")
                except ValueError:
                    errors.append(
                        f"[{filename}] 行{i+2} 字段'{h}'日期格式错误: '{val}'，应为YYYY-MM-DD"
                    )

    return errors, warnings


def generate_stats():
    stats = {}
    for table_key, table_def in TABLE_DEFINITIONS.items():
        filepath = BASE_DIR / f"{table_key}.csv"
        if filepath.exists():
            rows = read_csv(filepath)
            stats[table_key] = {
                "name": table_def["name"],
                "cnas": table_def["cnas"],
                "count": len(rows),
                "fields": len(rows[0].keys()) if rows else 0,
                "sub_tables": table_def["sub_tables"],
            }
            for sub_key in table_def["sub_tables"]:
                sub_path = BASE_DIR / f"{sub_key}.csv"
                if sub_path.exists():
                    sub_rows = read_csv(sub_path)
                    stats[sub_key] = {
                        "name": sub_key.split("_", 1)[1],
                        "count": len(sub_rows),
                        "fields": len(sub_rows[0].keys()) if sub_rows else 0,
                    }
    return stats


def generate_dashboard_html():
    stats = generate_stats()

    personnel = read_csv(BASE_DIR / "01_人员资质管理.csv") if (BASE_DIR / "01_人员资质管理.csv").exists() else []
    equipment = read_csv(BASE_DIR / "02_设备生命周期管理.csv") if (BASE_DIR / "02_设备生命周期管理.csv").exists() else []
    quality_control = read_csv(BASE_DIR / "03_1_质量控制计划.csv") if (BASE_DIR / "03_1_质量控制计划.csv").exists() else []
    internal_audit = read_csv(BASE_DIR / "03_2_内部审核.csv") if (BASE_DIR / "03_2_内部审核.csv").exists() else []
    management_review = read_csv(BASE_DIR / "03_3_管理评审.csv") if (BASE_DIR / "03_3_管理评审.csv").exists() else []
    detection = read_csv(BASE_DIR / "04_检测业务管理.csv") if (BASE_DIR / "04_检测业务管理.csv").exists() else []
    documents = read_csv(BASE_DIR / "05_文件控制管理.csv") if (BASE_DIR / "05_文件控制管理.csv").exists() else []
    ncr = read_csv(BASE_DIR / "06_不符合纠正措施.csv") if (BASE_DIR / "06_不符合纠正措施.csv").exists() else []
    authorizations = read_csv(BASE_DIR / "01_1_资质授权.csv") if (BASE_DIR / "01_1_资质授权.csv").exists() else []

    active_personnel = len([p for p in personnel if p.get("人员状态") == "在职"])
    active_equipment = len([e for e in equipment if e.get("设备状态") == "在用"])
    repair_equipment = len([e for e in equipment if e.get("设备状态") == "维修中"])
    outside_equipment = len([e for e in equipment if e.get("设备状态") == "外出"])

    today = datetime.now().strftime("%Y-%m-%d")
    today_dt = datetime.now()

    auth_expiring = 0
    auth_expired = 0
    for a in authorizations:
        exp_date = a.get("有效期至", "")
        if exp_date:
            try:
                exp_dt = datetime.strptime(exp_date, "%Y-%m-%d")
                if exp_dt <= today_dt:
                    auth_expired += 1
                elif exp_dt <= today_dt + timedelta(days=30):
                    auth_expiring += 1
            except ValueError:
                pass

    valid_auth = len([a for a in authorizations if a.get("授权状态") == "有效"])

    qc_completed = len([q for q in quality_control if q.get("执行状态") == "已完成"])
    qc_total = len(quality_control)
    qc_rate = f"{qc_completed / qc_total * 100:.1f}%" if qc_total > 0 else "0%"

    ncr_closed = len([n for n in ncr if n.get("闭环状态") == "已关闭"])
    ncr_total = len(ncr)
    ncr_rate = f"{ncr_closed / ncr_total * 100:.1f}%" if ncr_total > 0 else "0%"

    detection_in_progress = len([d for d in detection if d.get("项目状态") not in ["已完成", "已取消"]])
    detection_overdue = 0
    for d in detection:
        plan_date = d.get("计划完成日期", "")
        status = d.get("项目状态", "")
        if plan_date and status not in ["已完成", "已取消"]:
            try:
                if datetime.strptime(plan_date, "%Y-%m-%d") < today_dt:
                    detection_overdue += 1
            except ValueError:
                pass

    pending_reports = len([d for d in detection if d.get("项目状态") == "审批中"])

    docs_active = len([d for d in documents if d.get("文件状态") == "现行有效"])
    docs_review_needed = 0
    for d in documents:
        review_date = d.get("下次评审日期", "")
        if review_date:
            try:
                if datetime.strptime(review_date, "%Y-%m-%d") <= today_dt + timedelta(days=30):
                    docs_review_needed += 1
            except ValueError:
                pass

    eq_status_counter = Counter([e.get("设备状态", "未知") for e in equipment])
    ncr_source_counter = Counter([n.get("来源类型", "未知") for n in ncr])
    ncr_closure_counter = Counter([n.get("闭环状态", "未知") for n in ncr])
    dept_counter = Counter([p.get("所属部门", "未知") for p in personnel])
    position_counter = Counter([p.get("岗位", "未知") for p in personnel])
    doc_level_counter = Counter([d.get("文件层级", "未知") for d in documents])
    doc_status_counter = Counter([d.get("文件状态", "未知") for d in documents])
    auth_status_counter = Counter([a.get("授权状态", "未知") for a in authorizations])
    qc_type_counter = Counter([q.get("质控类型", "未知") for q in quality_control])
    qc_status_counter = Counter([q.get("执行状态", "未知") for q in quality_control])
    detection_status_counter = Counter([d.get("项目状态", "未知") for d in detection])

    def counter_to_chart_data(counter_obj):
        labels = list(counter_obj.keys())
        values = list(counter_obj.values())
        return labels, values

    def pie_data_js(var_name, counter_obj, colors=None):
        labels, values = counter_to_chart_data(counter_obj)
        default_colors = ["#4CAF50", "#FF9800", "#F44336", "#2196F3", "#9C27B0", "#00BCD4", "#795548", "#607D8B"]
        if colors is None:
            colors = default_colors[:len(labels)]
        bg_colors = colors[:len(labels)]
        return f"""var {var_name} = {{
            labels: {json.dumps(labels, ensure_ascii=False)},
            datasets: [{{
                data: {json.dumps(values)},
                backgroundColor: {json.dumps(bg_colors)},
                borderWidth: 2,
                borderColor: '#fff'
            }}]
        }};"""

    def bar_data_js(var_name, counter_obj, color="#2196F3"):
        labels, values = counter_to_chart_data(counter_obj)
        return f"""var {var_name} = {{
            labels: {json.dumps(labels, ensure_ascii=False)},
            datasets: [{{
                label: '数量',
                data: {json.dumps(values)},
                backgroundColor: '{color}',
                borderRadius: 4
            }}]
        }};"""

    overdue_ncr = []
    for n in ncr:
        plan_date = n.get("计划完成日期", "")
        closure = n.get("闭环状态", "")
        if plan_date and closure != "已关闭":
            try:
                if datetime.strptime(plan_date, "%Y-%m-%d") < today_dt:
                    overdue_ncr.append(n)
            except ValueError:
                pass

    cal_expiring = []
    cal_records = read_csv(BASE_DIR / "02_1_校准记录.csv") if (BASE_DIR / "02_1_校准记录.csv").exists() else []
    for c in cal_records:
        next_cal = c.get("下次校准日期", "")
        if next_cal:
            try:
                if datetime.strptime(next_cal, "%Y-%m-%d") <= today_dt + timedelta(days=30):
                    cal_expiring.append(c)
            except ValueError:
                pass

    warning_items = []
    for n in overdue_ncr:
        warning_items.append(f"NC: {n.get('不符合项编号', '')} - {n.get('不符合描述', '')[:30]}... 超期")
    for c in cal_expiring:
        warning_items.append(f"校准: {c.get('设备编号', '')} 下次校准 {c.get('下次校准日期', '')}")
    if auth_expiring > 0:
        warning_items.append(f"人员: {auth_expiring}人授权30天内到期")
    if auth_expired > 0:
        warning_items.append(f"人员: {auth_expired}人授权已过期")

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CNAS体系管理仪表盘</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: #f0f2f5;
            color: #333;
            min-height: 100vh;
        }}
        .header {{
            background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #3949ab 100%);
            color: white;
            padding: 20px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }}
        .header h1 {{ font-size: 22px; font-weight: 600; }}
        .header .date {{ font-size: 14px; opacity: 0.85; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 24px; }}
        .section-title {{
            font-size: 16px;
            font-weight: 600;
            color: #1a237e;
            margin: 24px 0 12px 0;
            padding-left: 12px;
            border-left: 4px solid #1a237e;
        }}
        .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.12); }}
        .card .label {{ font-size: 13px; color: #666; margin-bottom: 8px; }}
        .card .value {{ font-size: 32px; font-weight: 700; }}
        .card .unit {{ font-size: 14px; color: #999; margin-left: 4px; }}
        .card.primary .value {{ color: #1a237e; }}
        .card.success .value {{ color: #4CAF50; }}
        .card.warning .value {{ color: #FF9800; }}
        .card.danger .value {{ color: #F44336; }}
        .card.info .value {{ color: #2196F3; }}
        .charts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; margin-bottom: 24px; }}
        .chart-box {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        }}
        .chart-box h3 {{
            font-size: 15px;
            font-weight: 600;
            color: #333;
            margin-bottom: 16px;
        }}
        .chart-container {{ position: relative; height: 280px; }}
        .warning-panel {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            margin-bottom: 24px;
        }}
        .warning-panel h3 {{
            font-size: 15px;
            font-weight: 600;
            color: #F44336;
            margin-bottom: 12px;
        }}
        .warning-list {{ list-style: none; }}
        .warning-list li {{
            padding: 8px 12px;
            border-bottom: 1px solid #f5f5f5;
            font-size: 14px;
            display: flex;
            align-items: center;
        }}
        .warning-list li::before {{
            content: '';
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #F44336;
            margin-right: 10px;
            flex-shrink: 0;
        }}
        .warning-list li:last-child {{ border-bottom: none; }}
        .warning-list li.no-warning {{ color: #4CAF50; }}
        .warning-list li.no-warning::before {{ background: #4CAF50; }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        .data-table th {{
            background: #f5f5f5;
            padding: 10px 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid #ddd;
        }}
        .data-table td {{
            padding: 8px 12px;
            border-bottom: 1px solid #f0f0f0;
        }}
        .data-table tr:hover {{ background: #fafafa; }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 12px;
            font-weight: 500;
        }}
        .badge-green {{ background: #E8F5E9; color: #2E7D32; }}
        .badge-red {{ background: #FFEBEE; color: #C62828; }}
        .badge-orange {{ background: #FFF3E0; color: #E65100; }}
        .badge-blue {{ background: #E3F2FD; color: #1565C0; }}
        .badge-gray {{ background: #F5F5F5; color: #616161; }}
        .tabs {{
            display: flex;
            gap: 4px;
            margin-bottom: 20px;
            background: white;
            border-radius: 8px;
            padding: 4px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.08);
            overflow-x: auto;
        }}
        .tab {{
            padding: 10px 20px;
            border: none;
            background: transparent;
            cursor: pointer;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            color: #666;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        .tab:hover {{ background: #f5f5f5; }}
        .tab.active {{ background: #1a237e; color: white; }}
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #999;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>CNAS实验室管理体系 - 仪表盘</h1>
        <div class="date">数据截止：{today}</div>
    </div>

    <div class="container">
        <div class="section-title">核心指标</div>
        <div class="cards">
            <div class="card primary">
                <div class="label">在职人员</div>
                <div class="value">{active_personnel}<span class="unit">人</span></div>
            </div>
            <div class="card success">
                <div class="label">在用设备</div>
                <div class="value">{active_equipment}<span class="unit">台</span></div>
            </div>
            <div class="card info">
                <div class="label">年度质控完成率</div>
                <div class="value">{qc_rate}</div>
            </div>
            <div class="card success">
                <div class="label">不符合项闭环率</div>
                <div class="value">{ncr_rate}</div>
            </div>
            <div class="card warning">
                <div class="label">进行中检测项目</div>
                <div class="value">{detection_in_progress}<span class="unit">项</span></div>
            </div>
            <div class="card danger">
                <div class="label">超期项目</div>
                <div class="value">{detection_overdue}<span class="unit">项</span></div>
            </div>
            <div class="card info">
                <div class="label">现行有效文件</div>
                <div class="value">{docs_active}<span class="unit">份</span></div>
            </div>
            <div class="card warning">
                <div class="label">待评审文件</div>
                <div class="value">{docs_review_needed}<span class="unit">份</span></div>
            </div>
        </div>

        <div class="section-title">预警提醒</div>
        <div class="warning-panel">
            <h3>待处理预警</h3>
            <ul class="warning-list">
                {"<li>" + "</li><li>".join(warning_items) + "</li>" if warning_items else '<li class="no-warning">当前无待处理预警</li>'}
            </ul>
        </div>

        <div class="section-title">详细分析</div>
        <div class="tabs">
            <button class="tab active" onclick="switchTab('personnel')">人员管理</button>
            <button class="tab" onclick="switchTab('equipment')">设备管理</button>
            <button class="tab" onclick="switchTab('quality')">质量活动</button>
            <button class="tab" onclick="switchTab('detection')">检测业务</button>
            <button class="tab" onclick="switchTab('document')">文件管理</button>
            <button class="tab" onclick="switchTab('ncr')">不符合项</button>
        </div>

        <div id="tab-personnel" class="tab-content active">
            <div class="cards">
                <div class="card info">
                    <div class="label">有效授权</div>
                    <div class="value">{valid_auth}<span class="unit">项</span></div>
                </div>
                <div class="card warning">
                    <div class="label">30天内到期</div>
                    <div class="value">{auth_expiring}<span class="unit">项</span></div>
                </div>
                <div class="card danger">
                    <div class="label">已过期</div>
                    <div class="value">{auth_expired}<span class="unit">项</span></div>
                </div>
            </div>
            <div class="charts">
                <div class="chart-box">
                    <h3>人员部门分布</h3>
                    <div class="chart-container"><canvas id="chart-dept"></canvas></div>
                </div>
                <div class="chart-box">
                    <h3>授权状态分布</h3>
                    <div class="chart-container"><canvas id="chart-auth-status"></canvas></div>
                </div>
                <div class="chart-box">
                    <h3>岗位分布</h3>
                    <div class="chart-container"><canvas id="chart-position"></canvas></div>
                </div>
            </div>
        </div>

        <div id="tab-equipment" class="tab-content">
            <div class="cards">
                <div class="card success">
                    <div class="label">在用设备</div>
                    <div class="value">{active_equipment}<span class="unit">台</span></div>
                </div>
                <div class="card warning">
                    <div class="label">维修中</div>
                    <div class="value">{repair_equipment}<span class="unit">台</span></div>
                </div>
                <div class="card info">
                    <div class="label">外出送校</div>
                    <div class="value">{outside_equipment}<span class="unit">台</span></div>
                </div>
                <div class="card danger">
                    <div class="label">30天内校准到期</div>
                    <div class="value">{len(cal_expiring)}<span class="unit">台</span></div>
                </div>
            </div>
            <div class="charts">
                <div class="chart-box">
                    <h3>设备状态分布</h3>
                    <div class="chart-container"><canvas id="chart-eq-status"></canvas></div>
                </div>
                <div class="chart-box">
                    <h3>设备清单</h3>
                    <div style="max-height:280px;overflow:auto;">
                        <table class="data-table">
                            <thead><tr><th>编号</th><th>名称</th><th>状态</th><th>责任人</th></tr></thead>
                            <tbody>
                                {"".join(f'<tr><td>{e.get("设备编号","")}</td><td>{e.get("设备名称","")}</td><td><span class="badge {{"在用":"badge-green","维修中":"badge-orange","外出":"badge-blue","停用":"badge-gray","报废":"badge-red"}}.get(e.get("设备状态",""), "badge-gray")">{e.get("设备状态","")}</span></td><td>{e.get("责任人","")}</td></tr>' for e in equipment)}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <div id="tab-quality" class="tab-content">
            <div class="charts">
                <div class="chart-box">
                    <h3>质控类型分布</h3>
                    <div class="chart-container"><canvas id="chart-qc-type"></canvas></div>
                </div>
                <div class="chart-box">
                    <h3>质控执行状态</h3>
                    <div class="chart-container"><canvas id="chart-qc-status"></canvas></div>
                </div>
                <div class="chart-box">
                    <h3>内审不符合项闭环</h3>
                    <div class="chart-container"><canvas id="chart-ncr-closure"></canvas></div>
                </div>
                <div class="chart-box">
                    <h3>管理评审状态</h3>
                    <div class="chart-container"><canvas id="chart-mr-status"></canvas></div>
                </div>
            </div>
        </div>

        <div id="tab-detection" class="tab-content">
            <div class="cards">
                <div class="card info">
                    <div class="label">进行中项目</div>
                    <div class="value">{detection_in_progress}<span class="unit">项</span></div>
                </div>
                <div class="card danger">
                    <div class="label">超期项目</div>
                    <div class="value">{detection_overdue}<span class="unit">项</span></div>
                </div>
                <div class="card warning">
                    <div class="label">待审批报告</div>
                    <div class="value">{pending_reports}<span class="unit">份</span></div>
                </div>
            </div>
            <div class="charts">
                <div class="chart-box">
                    <h3>项目状态分布</h3>
                    <div class="chart-container"><canvas id="chart-detection-status"></canvas></div>
                </div>
                <div class="chart-box">
                    <h3>检测项目清单</h3>
                    <div style="max-height:280px;overflow:auto;">
                        <table class="data-table">
                            <thead><tr><th>编号</th><th>项目名称</th><th>客户</th><th>状态</th><th>计划完成</th></tr></thead>
                            <tbody>
                                {"".join(f'<tr><td>{d.get("项目编号","")}</td><td>{d.get("项目名称","")}</td><td>{d.get("客户名称","")}</td><td><span class="badge {{"已完成":"badge-green","审批中":"badge-orange","报告编制":"badge-blue","检测执行":"badge-blue","样品接收":"badge-blue"}}.get(d.get("项目状态",""), "badge-gray")">{d.get("项目状态","")}</span></td><td>{d.get("计划完成日期","")}</td></tr>' for d in detection)}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <div id="tab-document" class="tab-content">
            <div class="cards">
                <div class="card success">
                    <div class="label">现行有效</div>
                    <div class="value">{docs_active}<span class="unit">份</span></div>
                </div>
                <div class="card warning">
                    <div class="label">待评审</div>
                    <div class="value">{docs_review_needed}<span class="unit">份</span></div>
                </div>
            </div>
            <div class="charts">
                <div class="chart-box">
                    <h3>文件层级分布</h3>
                    <div class="chart-container"><canvas id="chart-doc-level"></canvas></div>
                </div>
                <div class="chart-box">
                    <h3>文件状态分布</h3>
                    <div class="chart-container"><canvas id="chart-doc-status"></canvas></div>
                </div>
            </div>
        </div>

        <div id="tab-ncr" class="tab-content">
            <div class="cards">
                <div class="card info">
                    <div class="label">不符合项总数</div>
                    <div class="value">{ncr_total}<span class="unit">项</span></div>
                </div>
                <div class="card success">
                    <div class="label">已关闭</div>
                    <div class="value">{ncr_closed}<span class="unit">项</span></div>
                </div>
                <div class="card danger">
                    <div class="label">超期未关闭</div>
                    <div class="value">{len(overdue_ncr)}<span class="unit">项</span></div>
                </div>
            </div>
            <div class="charts">
                <div class="chart-box">
                    <h3>不符合项来源统计</h3>
                    <div class="chart-container"><canvas id="chart-ncr-source"></canvas></div>
                </div>
                <div class="chart-box">
                    <h3>闭环状态分布</h3>
                    <div class="chart-container"><canvas id="chart-ncr-closure-status"></canvas></div>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        CNAS实验室管理体系仪表盘 | 自动生成于 {today} | 数据仅供预览参考
    </div>

    <script>
        function switchTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tabName).classList.add('active');
            event.target.classList.add('active');
        }}

        Chart.defaults.font.family = "-apple-system, BlinkMacSystemFont, 'PingFang SC', 'Microsoft YaHei', sans-serif";
        Chart.defaults.font.size = 12;

        {pie_data_js("deptData", dept_counter, ["#1a237e","#283593","#3949ab","#5c6bc0","#7986cb"])}
        new Chart(document.getElementById('chart-dept'), {{
            type: 'doughnut',
            data: deptData,
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }}
        }});

        {pie_data_js("authStatusData", auth_status_counter, ["#4CAF50","#FF9800","#F44336","#9C27B0"])}
        new Chart(document.getElementById('chart-auth-status'), {{
            type: 'doughnut',
            data: authStatusData,
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }}
        }});

        {bar_data_js("positionData", position_counter, "#3949ab")}
        new Chart(document.getElementById('chart-position'), {{
            type: 'bar',
            data: positionData,
            options: {{ responsive: true, maintainAspectRatio: false, indexAxis: 'y', plugins: {{ legend: {{ display: false }} }} }}
        }});

        {pie_data_js("eqStatusData", eq_status_counter, ["#4CAF50","#9E9E9E","#F44336","#2196F3","#FF9800"])}
        new Chart(document.getElementById('chart-eq-status'), {{
            type: 'doughnut',
            data: eqStatusData,
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }}
        }});

        {bar_data_js("qcTypeData", qc_type_counter, "#1a237e")}
        new Chart(document.getElementById('chart-qc-type'), {{
            type: 'bar',
            data: qcTypeData,
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
        }});

        {pie_data_js("qcStatusData", qc_status_counter, ["#FF9800","#2196F3","#4CAF50","#9E9E9E"])}
        new Chart(document.getElementById('chart-qc-status'), {{
            type: 'doughnut',
            data: qcStatusData,
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }}
        }});

        {pie_data_js("ncrClosureData", ncr_closure_counter, ["#9E9E9E","#FF9800","#2196F3","#9C27B0","#4CAF50"])}
        new Chart(document.getElementById('chart-ncr-closure'), {{
            type: 'doughnut',
            data: ncrClosureData,
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }}
        }});

        {pie_data_js("mrStatusData", Counter([m.get("评审状态","未知") for m in management_review]), ["#FF9800","#4CAF50"])}
        new Chart(document.getElementById('chart-mr-status'), {{
            type: 'doughnut',
            data: mrStatusData,
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }}
        }});

        {pie_data_js("detectionStatusData", detection_status_counter, ["#4CAF50","#FF9800","#2196F3","#9C27B0","#9E9E9E"])}
        new Chart(document.getElementById('chart-detection-status'), {{
            type: 'doughnut',
            data: detectionStatusData,
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }}
        }});

        {pie_data_js("docLevelData", doc_level_counter, ["#1a237e","#3949ab","#7986cb","#9fa8da"])}
        new Chart(document.getElementById('chart-doc-level'), {{
            type: 'doughnut',
            data: docLevelData,
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }}
        }});

        {pie_data_js("docStatusData", doc_status_counter, ["#4CAF50","#FF9800","#9E9E9E","#2196F3"])}
        new Chart(document.getElementById('chart-doc-status'), {{
            type: 'doughnut',
            data: docStatusData,
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }}
        }});

        {bar_data_js("ncrSourceData", ncr_source_counter, "#F44336")}
        new Chart(document.getElementById('chart-ncr-source'), {{
            type: 'bar',
            data: ncrSourceData,
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }} }}
        }});

        {pie_data_js("ncrClosureStatusData", ncr_closure_counter, ["#9E9E9E","#FF9800","#2196F3","#9C27B0","#4CAF50"])}
        new Chart(document.getElementById('chart-ncr-closure-status'), {{
            type: 'doughnut',
            data: ncrClosureStatusData,
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ position: 'right' }} }} }}
        }});
    </script>
</body>
</html>"""

    return html


def generate_data_dictionary():
    lines = ["# CNAS体系多维表 - 数据字典\n"]
    lines.append(f"生成日期：{datetime.now().strftime('%Y-%m-%d')}\n")

    for table_key, table_def in TABLE_DEFINITIONS.items():
        filepath = BASE_DIR / f"{table_key}.csv"
        if not filepath.exists():
            continue

        rows = read_csv(filepath)
        if not rows:
            continue

        lines.append(f"\n## {table_def['name']}（{table_def['cnas']}）\n")
        lines.append("| 字段名 | 字段类型 | 说明 |")
        lines.append("|--------|----------|------|")

        headers = list(rows[0].keys())
        for h in headers:
            field_type = "单行文本"
            for field_name, valid_values in SELECT_FIELDS.items():
                if h == field_name:
                    field_type = f"单选（{'/'.join(valid_values[:5])}...）"
                    break
            if "日期" in h:
                field_type = "日期"
            elif "费用" in h or "时长" in h or "数量" in h:
                field_type = "数字"
            elif h == "备注":
                field_type = "多行文本"
            elif "邮箱" in h:
                field_type = "邮箱"
            elif "电话" in h:
                field_type = "电话"
            elif "链接" in h:
                field_type = "超链接"
            elif h == table_def.get("key_field"):
                field_type = "单行文本（主键）"

            lines.append(f"| {h} | {field_type} | |")

        for sub_key in table_def.get("sub_tables", []):
            sub_path = BASE_DIR / f"{sub_key}.csv"
            if not sub_path.exists():
                continue
            sub_rows = read_csv(sub_path)
            if not sub_rows:
                continue
            sub_name = sub_key.split("_", 1)[1]
            lines.append(f"\n### 子表：{sub_name}\n")
            lines.append("| 字段名 | 字段类型 | 说明 |")
            lines.append("|--------|----------|------|")
            sub_headers = list(sub_rows[0].keys())
            for h in sub_headers:
                if h is None:
                    continue
                field_type = "单行文本"
                for field_name, valid_values in SELECT_FIELDS.items():
                    if h == field_name:
                        field_type = f"单选（{'/'.join(valid_values[:5])}...）"
                        break
                if "日期" in h:
                    field_type = "日期"
                elif "费用" in h or "时长" in h or "数量" in h:
                    field_type = "数字"
                elif h == "备注":
                    field_type = "多行文本"
                lines.append(f"| {h} | {field_type} | |")

    return "\n".join(lines)


def main():
    print("=" * 60)
    print("  CNAS体系多维表 - 一键处理脚本")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("""
用法: python cnas_toolkit.py <命令>

命令:
  validate    校验所有CSV数据完整性和格式
  dashboard   生成HTML仪表盘预览页面
  dictionary  生成数据字典
  all         执行全部操作

示例:
  python cnas_toolkit.py validate
  python cnas_toolkit.py dashboard
  python cnas_toolkit.py all
""")
        sys.exit(0)

    command = sys.argv[1]

    if command in ("validate", "all"):
        print("\n[1/3] 校验CSV数据...")
        print("-" * 40)
        total_errors = 0
        total_warnings = 0

        csv_files = sorted(BASE_DIR.glob("*.csv"))
        for csv_file in csv_files:
            if csv_file.name == "07_基础数据配置.csv":
                continue
            errors, warnings = validate_csv(csv_file)
            if errors or warnings:
                for e in errors:
                    print(f"  ERROR: {e}")
                    total_errors += 1
                for w in warnings:
                    print(f"  WARN:  {w}")
                    total_warnings += 1
            else:
                print(f"  OK: {csv_file.name}")

        print(f"\n校验结果: {len(csv_files)}个文件, {total_errors}个错误, {total_warnings}个警告")

    if command in ("dashboard", "all"):
        print("\n[2/3] 生成仪表盘预览...")
        print("-" * 40)
        html = generate_dashboard_html()
        output_path = BASE_DIR / "dashboard_preview.html"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  仪表盘预览已生成: {output_path}")
        print(f"  请在浏览器中打开查看")

    if command in ("dictionary", "all"):
        print("\n[3/3] 生成数据字典...")
        print("-" * 40)
        dictionary = generate_data_dictionary()
        output_path = BASE_DIR / "数据字典.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dictionary)
        print(f"  数据字典已生成: {output_path}")

    if command not in ("validate", "dashboard", "dictionary", "all"):
        print(f"未知命令: {command}")
        print("可用命令: validate, dashboard, dictionary, all")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  处理完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
