"""导出测绘预算 Excel — 匹配 DX20260411测绘预算.xlsx 格式"""
import io
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter


thin_border = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin"),
)
header_font = Font(name="宋体", size=11, bold=True)
normal_font = Font(name="宋体", size=10)
title_font = Font(name="宋体", size=14, bold=True)
center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
header_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")


def _style_range(ws, min_row, max_row, min_col, max_col, font=None, alignment=None, border=None):
    for row in ws.iter_rows(min_row=min_row, max_row=max_row, min_col=min_col, max_col=max_col):
        for cell in row:
            if font: cell.font = font
            if alignment: cell.alignment = alignment
            if border: cell.border = border


async def export_budget_excel(db, project_id: str) -> io.BytesIO:
    """生成完整的预算 Excel 文件"""
    from app.models.budget_v2 import (
        BudgetSummary, BudgetPersonnel, BudgetMaterial,
        BudgetEquipment, BudgetDirectCost, BudgetLabor,
        BudgetSubcontract, BudgetRDOther,
    )
    from app.models import Project
    from sqlalchemy import select

    wb = Workbook()

    # ====== 加载数据 ======
    # Summary
    sum_result = await db.execute(select(BudgetSummary).where(BudgetSummary.project_id == project_id))
    s = sum_result.scalar_one_or_none()

    # Project
    proj_result = await db.execute(select(Project).where(Project.id == project_id))
    project = proj_result.scalar_one_or_none()

    project_name = s.project_name if s and s.project_name else (project.name if project else "")
    party_a = s.party_a if s else ""
    contact_person = s.contact_person if s else ""
    contact_phone = s.contact_phone if s else ""
    address = s.address if s else ""
    location = s.location if s else ""
    start_date = s.start_date if s else ""
    end_date = s.end_date if s else ""
    duration = s.planned_duration if s else ""
    contract_amount = s.contract_amount if s else 0
    tax_rate = s.tax_rate if s else 0
    contract_no = s.contract_no if s else ""
    sign_date = s.contract_sign_date if s else ""
    unit = s.implementing_unit if s else ""
    manager = s.project_manager if s else (project.manager.name if project and project.manager else "")
    tech = s.tech_lead if s else ""
    basis = s.compilation_basis if s else ""
    conditions = s.construction_conditions if s else ""
    work_content = s.work_content if s else ""
    other_info = s.other_info if s else ""
    drafter = s.drafter if s else ""
    checker = s.checker if s else ""
    reviewer = s.reviewer if s else ""

    # 人工费
    pers_result = await db.execute(select(BudgetPersonnel).where(BudgetPersonnel.project_id == project_id).order_by(BudgetPersonnel.sort_order))
    personnel_list = pers_result.scalars().all()
    shiye_list = [p for p in personnel_list if p.category == "事业编人员"]
    qiye_list = [p for p in personnel_list if p.category == "企业编人员"]

    # 材料费
    mat_result = await db.execute(select(BudgetMaterial).where(BudgetMaterial.project_id == project_id).order_by(BudgetMaterial.sort_order))
    mat_list = mat_result.scalars().all()
    mat_by_cat = {}
    for m in mat_list:
        c = m.category or "原材料"
        mat_by_cat.setdefault(c, []).append(m)

    # 机械费
    equip_result = await db.execute(select(BudgetEquipment).where(BudgetEquipment.project_id == project_id).order_by(BudgetEquipment.sort_order))
    equip_list = equip_result.scalars().all()

    # 其他直接费
    dc_result = await db.execute(select(BudgetDirectCost).where(BudgetDirectCost.project_id == project_id).order_by(BudgetDirectCost.sort_order))
    dc_list = dc_result.scalars().all()
    dc_by_cat = {}
    for d in dc_list:
        dc_by_cat.setdefault(d.category, []).append(d)

    # 劳务费
    labor_result = await db.execute(select(BudgetLabor).where(BudgetLabor.project_id == project_id).order_by(BudgetLabor.sort_order))
    labor_list = labor_result.scalars().all()

    # 分包费
    sub_result = await db.execute(select(BudgetSubcontract).where(BudgetSubcontract.project_id == project_id).order_by(BudgetSubcontract.sort_order))
    sub_list = sub_result.scalars().all()

    # 研发+其他
    rd_result = await db.execute(select(BudgetRDOther).where(BudgetRDOther.project_id == project_id).order_by(BudgetRDOther.sort_order))
    rd_other_list = rd_result.scalars().all()
    rd_list = [r for r in rd_other_list if r.cost_group == "研发费用"]
    other_list = [r for r in rd_other_list if r.cost_group != "研发费用"]

    # ====== Sheet 1: 说明 ======
    ws1 = wb.active
    ws1.title = "说明"
    ws1.column_dimensions["A"].width = 3; ws1.column_dimensions["B"].width = 20
    ws1.column_dimensions["C"].width = 30; ws1.column_dimensions["D"].width = 30
    ws1.column_dimensions["E"].width = 10; ws1.column_dimensions["F"].width = 10
    ws1.column_dimensions["G"].width = 10; ws1.column_dimensions["H"].width = 10
    ws1.column_dimensions["I"].width = 10; ws1.column_dimensions["J"].width = 10
    ws1.column_dimensions["K"].width = 10; ws1.column_dimensions["L"].width = 10
    ws1.column_dimensions["M"].width = 10; ws1.column_dimensions["N"].width = 10

    title = f"{project_name}成本费用预算编制说明" if project_name else "项目成本费用预算编制说明"
    ws1.merge_cells("A1:N1")
    ws1["A1"] = title; ws1["A1"].font = title_font; ws1["A1"].alignment = center_align

    rows_s1 = [
        ("A2", "工程概况"),
        ("B2", f"工程名称：{project_name}"),
        ("B3", f"甲方全称：{party_a}"), ("J3", "联系人"), ("K3", contact_person), ("M3", "电话"), ("N3", str(contact_phone)),
        ("B4", f"甲方通讯地址：{address}"),
        ("B5", f"工程所在地：{location}"),
        ("B6", f"开竣工日期：{start_date}-{end_date}"), ("J6", f"计划工期：{duration}"),
        ("B7", "合 同 额："), ("D7", contract_amount), ("F7", "元"), ("G7", "税率"), ("H7", tax_rate),
        ("B8", f"合同签订时间：{sign_date}"), ("J8", f"合同编号：{contract_no}"),
        ("B9", f"实施单位：{unit}"),
        ("B10", f"项目经理：{manager}                    技术负责：{tech}"),
        ("A11", "编制依据"), ("B11", basis),
        ("A15", "施工条件"), ("B15", conditions),
        ("A22", "工作内容"), ("B22", work_content),
        ("A32", "其他"), ("B32", other_info),
        ("A38", f"填表：{drafter}        校核：{checker}        审核：{reviewer}"),
    ]
    for cell_ref, val in rows_s1:
        ws1[cell_ref] = val
        ws1[cell_ref].font = normal_font
        ws1[cell_ref].alignment = left_align

    # ====== Sheet 2: 总表 ======
    ws2 = wb.create_sheet("总表")
    for i, w in enumerate([3, 5, 24, 14, 14], 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    ws2.merge_cells("A1:E1")
    ws2["A1"] = "项目成本费用预算总表"; ws2["A1"].font = title_font; ws2["A1"].alignment = center_align

    headers2 = ["", "工  作  内  容", "金额", "备 注", "税率"]
    for i, h in enumerate(headers2, 1):
        cell = ws2.cell(row=2, column=i, value=h)
        cell.font = header_font; cell.alignment = center_align; cell.fill = header_fill; cell.border = thin_border

    # 计算汇总
    # 人工费
    salary_total = sum(p.salary_subtotal for p in personnel_list)
    welfare_total = sum(p.welfare_subtotal for p in personnel_list)
    coord_total = sum(p.coordination_subtotal for p in personnel_list)
    union_total = sum(p.union_subtotal for p in personnel_list)
    personnel_total = sum(p.total for p in personnel_list)

    mat_total = sum(m.amount for m in mat_list)
    equip_total = sum(e.amount for e in equip_list)

    # 其他直接费 按科目
    def dc_sum(cat):
        return sum(d.amount for d in dc_list if d.category == cat)
    labor_total2 = sum(l.amount for l in labor_list)
    sub_total = sum(s.amount for s in sub_list)
    dc_items = [
        ("运输费", dc_sum("运输费")),
        ("装卸费", dc_sum("装卸费")),
        ("检验试验费", dc_sum("试验检测费")),
        ("维修（护）费", dc_sum("维修(护)费") + dc_sum("维修费")),
        ("办公费", dc_sum("办公费")),
        ("出版印刷费", dc_sum("出版印刷费")),
        ("水电费", dc_sum("水电费")),
        ("邮电费", dc_sum("邮电费")),
        ("取暖费", dc_sum("取暖费")),
        ("交通费", dc_sum("交通费")),
    ]
    dc_total = sum(a for _, a in dc_items) + labor_total2 + sub_total
    construction_total = personnel_total + mat_total + equip_total + dc_total
    rd_total = sum(r.amount for r in rd_list)
    other_total2 = sum(o.amount for o in other_list)

    row = 3
    tree_data = [
        (0, "一、工程施工", construction_total, "", ""),
        (1, "1.1人工费", personnel_total, "附明细", ""),
        (2, "⑴职工薪酬", round(salary_total, 2), "", ""),
        (2, "⑵职工福利费", round(welfare_total, 2), "", ""),
        (2, "⑶单位统筹", round(coord_total, 2), "", ""),
        (2, "⑷工会经费", round(union_total, 2), "", ""),
        (1, "2.1材料费", mat_total, "", ""),
        (2, "⑴原材料", round(mat_by_cat.get("原材料", [{}])[0] if "原材料" in mat_by_cat else sum(getattr(m, 'amount', 0) for m in mat_by_cat.get("原材料", [])), 2), "", ""),
        (1, "3.1机械使用费", equip_total, "", ""),
        (2, "⑴设备租赁费", equip_total, "", ""),
        (1, "4.1其他直接费", dc_total, "附明细", ""),
    ]
    for c, (level, name, amt, remark, tax) in enumerate([
        (0, "一、工程施工", construction_total, "", ""),
        (1, "1.1人工费", personnel_total, "附明细", ""),
        (2, "职工薪酬", round(salary_total, 2), "", ""),
        (2, "职工福利费", round(welfare_total, 2), "", ""),
        (2, "单位统筹", round(coord_total, 2), "", ""),
        (2, "工会经费", round(union_total, 2), "", ""),
        (1, "2.1材料费", mat_total, "", ""),
        (2, "原材料", round(sum(getattr(m, 'amount', 0) for m in mat_by_cat.get("原材料", [])), 2), "", ""),
        (2, "专用材料费", round(sum(getattr(m, 'amount', 0) for m in mat_by_cat.get("专用材料费", []) + mat_by_cat.get("专用材料", [])), 2), "", ""),
        (2, "燃油", round(sum(getattr(m, 'amount', 0) for m in mat_by_cat.get("燃油", []) + mat_by_cat.get("燃油费", [])), 2), "", ""),
        (2, "技术资料费", round(sum(getattr(m, 'amount', 0) for m in mat_by_cat.get("技术资料费", []) + mat_by_cat.get("技术资料", [])), 2), "", ""),
        (1, "3.1机械使用费", equip_total, "", ""),
        (2, "设备租赁费", equip_total, "", ""),
        (1, "4.1其他直接费", dc_total, "附明细", ""),
    ] + [(2, name, round(amt, 2), "", "") for name, amt in dc_items] + [
        (2, "劳务费", labor_total2, "", ""),
        (2, "分包工程款", sub_total, "附明细", ""),
    ]):
        indent = "    " * level
        for col_idx, val in enumerate(["" if level else indent + name, indent + name if level else "", amt, remark, ""], 1):
            if level == 0 or col_idx > 1:
                pass
        # Simplified: write with indentation
        row += 1
        ws2.cell(row=row, column=1, value="" if level else "")
        ws2.cell(row=row, column=2, value=f"{'    ' * level}  {name}").font = normal_font
        ws2.cell(row=row, column=2).alignment = left_align
        ws2.cell(row=row, column=3, value=amt).font = normal_font
        ws2.cell(row=row, column=4, value=remark).font = normal_font
        for c2 in range(1, 6):
            ws2.cell(row=row, column=c2).border = thin_border

    # 研发+其他
    if rd_total > 0:
        row += 1
        ws2.cell(row=row, column=2, value="研发费用").font = header_font
        ws2.cell(row=row, column=3, value=rd_total)
        for c2 in range(1, 6): ws2.cell(row=row, column=c2).border = thin_border
    if other_total2 > 0:
        row += 1
        ws2.cell(row=row, column=2, value="其他费用").font = header_font
        ws2.cell(row=row, column=3, value=other_total2)
        for c2 in range(1, 6): ws2.cell(row=row, column=c2).border = thin_border

    # Total row
    row += 1
    ws2.cell(row=row, column=2, value="合  计").font = Font(name="宋体", size=11, bold=True)
    ws2.cell(row=row, column=3, value=round(construction_total + rd_total + other_total2, 2)).font = Font(name="宋体", size=11, bold=True)
    for c2 in range(1, 6): ws2.cell(row=row, column=c2).border = thin_border

    # ====== Sheet 3: 1.1人工费 ======
    ws3 = wb.create_sheet("1.1人工费")
    person_headers = ["类别", "岗位", "姓名", "单位", "基本工资\n及津补贴", "绩效", "野外津贴",
                       "防暑降温", "工会经费", "单位统筹", "工作时间\n(月)", "野外时间\n(月)",
                       "薪酬小计", "福利费小计", "单位统筹小计", "工会经费小计", "合计"]
    col_widths = [10, 10, 10, 8, 12, 10, 10, 10, 10, 10, 10, 10, 10, 10, 12, 10, 10]
    for i, (h, w) in enumerate(zip(person_headers, col_widths), 1):
        ws3.column_dimensions[get_column_letter(i)].width = w
        cell = ws3.cell(row=1, column=i, value=h)
        cell.font = Font(name="宋体", size=9, bold=True); cell.alignment = center_align; cell.fill = header_fill; cell.border = thin_border

    row = 2
    for cat_label, p_list in [("事业编人员", shiye_list), ("企业编人员", qiye_list)]:
        if not p_list:
            # Empty row for structure
            ws3.cell(row=row, column=1, value=cat_label).font = normal_font
            for c in range(1, 18): ws3.cell(row=row, column=c).border = thin_border
            row += 1
            continue
        for i, p in enumerate(p_list):
            vals = [cat_label if i == 0 else "",
                    p.position or "", p.employee_name or "", "人·月",
                    p.base_salary, p.performance, p.field_allowance,
                    p.heat_prevention, p.union_fee, p.unit_coordination,
                    p.work_months, p.field_months,
                    p.salary_subtotal, p.welfare_subtotal,
                    p.coordination_subtotal, p.union_subtotal, p.total]
            for c, v in enumerate(vals, 1):
                ws3.cell(row=row, column=c, value=v if v else ("" if isinstance(v, str) else 0)).font = normal_font
                ws3.cell(row=row, column=c).alignment = center_align
                ws3.cell(row=row, column=c).border = thin_border
            row += 1

    # ====== Sheet 4: 2.1材料费 ======
    ws4 = wb.create_sheet("2.1材料费")
    mat_headers = ["序号", "科目", "名称", "型号", "单位", "单价", "数量", "金额", "预算说明"]
    for i, h in enumerate(mat_headers, 1):
        ws4.column_dimensions[get_column_letter(i)].width = 12
        cell = ws4.cell(row=1, column=i, value=h); cell.font = header_font; cell.alignment = center_align; cell.fill = header_fill; cell.border = thin_border
    row = 2
    for i, m in enumerate(mat_list, 1):
        vals = [i, m.category or "", m.name or "", m.model or "", m.unit or "", m.unit_price, m.quantity, m.amount, m.remark or ""]
        for c, v in enumerate(vals, 1):
            ws4.cell(row=row, column=c, value=v).font = normal_font
            ws4.cell(row=row, column=c).border = thin_border
        row += 1

    # ====== Sheet 5: 3.1机械费 ======
    ws5 = wb.create_sheet("3.1机械费")
    equip_headers = ["序号", "分类", "内容", "对方单位", "型号", "单价", "数量", "金额"]
    for i, h in enumerate(equip_headers, 1):
        ws5.column_dimensions[get_column_letter(i)].width = 14
        cell = ws5.cell(row=1, column=i, value=h); cell.font = header_font; cell.alignment = center_align; cell.fill = header_fill; cell.border = thin_border
    row = 2
    for i, e in enumerate(equip_list, 1):
        vals = [i, e.classification or "", e.content or "", e.counterparty or "", e.model or "", e.unit_price, e.quantity, e.amount]
        for c, v in enumerate(vals, 1):
            ws5.cell(row=row, column=c, value=v).font = normal_font
            ws5.cell(row=row, column=c).border = thin_border
        row += 1

    # ====== Sheet 6: 4.1其他直接费 ======
    ws6 = wb.create_sheet("4.1其他直接费")
    dc_headers = ["序号", "科目", "内容", "单位", "单价", "数量", "金额", "预算说明"]
    for i, h in enumerate(dc_headers, 1):
        ws6.column_dimensions[get_column_letter(i)].width = 14
        cell = ws6.cell(row=1, column=i, value=h); cell.font = header_font; cell.alignment = center_align; cell.fill = header_fill; cell.border = thin_border
    row = 2
    seq = 0
    for cat in ["运输费", "装卸费", "试验检测费", "维修(护)费", "办公费", "出版印刷费", "水电费", "邮电费", "取暖费", "交通费"]:
        items = dc_by_cat.get(cat, [])
        if not items:
            seq += 1
            vals = [seq, cat, "", "", 0, 0, 0, ""]
            for c, v in enumerate(vals, 1):
                ws6.cell(row=row, column=c, value=v).font = normal_font
                ws6.cell(row=row, column=c).border = thin_border
            row += 1
        else:
            for d in items:
                seq += 1
                vals = [seq, d.category, d.content or "", d.unit or "", d.unit_price, d.quantity, d.amount, d.remark or ""]
                for c, v in enumerate(vals, 1):
                    ws6.cell(row=row, column=c, value=v).font = normal_font
                    ws6.cell(row=row, column=c).border = thin_border
                row += 1

    # ====== Sheet 7-10: 其他明细表 ======
    def write_simple_sheet(wb, title, headers, data_rows):
        ws = wb.create_sheet(title)
        for i, h in enumerate(headers, 1):
            ws.column_dimensions[get_column_letter(i)].width = 14
            cell = ws.cell(row=1, column=i, value=h); cell.font = header_font; cell.alignment = center_align; cell.fill = header_fill; cell.border = thin_border
        for r, vals in enumerate(data_rows, 2):
            for c, v in enumerate(vals, 1):
                ws.cell(row=r, column=c, value=v).font = normal_font
                ws.cell(row=r, column=c).border = thin_border
        return ws

    labor_data = [[i, l.category, l.position or "", l.employee_name or "", l.unit or "", l.quantity, l.unit_price, l.amount, l.remark or ""]
                  for i, l in enumerate(labor_list, 1)]
    write_simple_sheet(wb, "4.1.5劳务费", ["序号", "类别", "岗位", "姓名", "单位", "数量", "单价", "金额", "预算说明"], labor_data)

    sub_data = [[i, s.category, s.item_name or "", s.counterparty or "", s.workload, s.unit_price, s.amount, s.remark or ""]
                for i, s in enumerate(sub_list, 1)]
    write_simple_sheet(wb, "4.1.7分包工程款", ["序号", "项目", "对方单位", "工作量", "单价", "合计", "预算说明", ""], sub_data)

    rd_data = [[i, r.item or "", r.unit or "", r.base_price, r.quantity, r.amount, r.remark or ""]
               for i, r in enumerate(rd_list, 1)]
    write_simple_sheet(wb, "4.1.19.1研发费用", ["序号", "项目", "单位", "基价(元)", "数量", "金额(元)", "备注"], rd_data)

    other_data = [[i, o.cost_group, o.item or "", o.unit or "", o.base_price, o.quantity, o.amount, o.remark or ""]
                  for i, o in enumerate(other_list, 1)]
    write_simple_sheet(wb, "4.1.19.2其他费用", ["序号", "类别", "项目", "单位", "基价(元)", "数量", "金额(元)", "备注"], other_data)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
