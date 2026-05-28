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
sub_header_font = Font(name="宋体", size=9, bold=True)
normal_font = Font(name="宋体", size=10)
small_font = Font(name="宋体", size=9)
title_font = Font(name="宋体", size=14, bold=True)
section_font = Font(name="宋体", size=11, bold=True)
center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
header_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")


def _style_range(ws, min_r, max_r, min_c, max_c, **kwargs):
    for row in ws.iter_rows(min_row=min_r, max_row=max_r, min_col=min_c, max_col=max_c):
        for cell in row:
            if "font" in kwargs: cell.font = kwargs["font"]
            if "alignment" in kwargs: cell.alignment = kwargs["alignment"]
            if "border" in kwargs: cell.border = kwargs["border"]
            if "fill" in kwargs: cell.fill = kwargs["fill"]


def _write_row(ws, row, data, font=None, alignment=None, border=None):
    for c, val in enumerate(data, 1):
        cell = ws.cell(row=row, column=c, value=val)
        if font: cell.font = font
        if alignment: cell.alignment = alignment
        if border: cell.border = border


async def export_budget_excel(db, project_id: str) -> io.BytesIO:
    """生成完整的预算 Excel 文件，匹配 DX20260411测绘预算.xlsx 格式"""
    from app.models.budget_v2 import (
        BudgetSummary, BudgetPersonnel, BudgetMaterial,
        BudgetEquipment, BudgetDirectCost, BudgetLabor,
        BudgetSubcontract, BudgetRDOther,
    )
    from app.models import Project
    from app.models.contract import Contract
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    wb = Workbook()

    # ====== 加载数据 ======
    sum_result = await db.execute(select(BudgetSummary).where(BudgetSummary.project_id == project_id))
    s = sum_result.scalar_one_or_none()

    proj_result = await db.execute(
        select(Project).options(selectinload(Project.manager)).where(Project.id == project_id)
    )
    project = proj_result.scalar_one_or_none()

    contract_result = await db.execute(select(Contract).where(Contract.project_id == project_id))
    contract = contract_result.scalar_one_or_none()

    # 合并项目信息
    project_name = project.name if project else (s.project_name if s else "")
    party_a = project.party_a if project else (s.party_a if s else "")
    contact_person = project.contact_person if project else (s.contact_person if s else "")
    contact_phone = project.contact_phone if project else (s.contact_phone if s else "")
    manager = project.manager.name if project and project.manager else (s.project_manager if s else "")
    contract_no = contract.contract_no if contract else (s.contract_no if s else "")
    contract_amount = contract.contract_amount if contract else (s.contract_amount if s else 0)
    sign_date = str(contract.sign_date) if contract and contract.sign_date else (s.contract_sign_date if s else "")
    drafter = contract.drafter if contract else (s.drafter if s else "")
    reviewer = contract.reviewer if contract else (s.reviewer if s else "")
    address = s.address if s else ""
    location = s.location if s else ""
    start_date = s.start_date if s else ""
    end_date = s.end_date if s else ""
    duration = s.planned_duration if s else ""
    tax_rate = s.tax_rate if s else 0
    unit = s.implementing_unit if s else ""
    tech = s.tech_lead if s else ""
    basis = s.compilation_basis if s else ""
    conditions = s.construction_conditions if s else ""
    work_content = s.work_content if s else ""
    other_info = s.other_info if s else ""
    checker = s.checker if s else ""

    # 人工费
    pers_result = await db.execute(select(BudgetPersonnel).where(BudgetPersonnel.project_id == project_id).order_by(BudgetPersonnel.sort_order))
    personnel_list = pers_result.scalars().all()
    shiye_list = [p for p in personnel_list if p.category == "事业编人员"]
    qiye_list = [p for p in personnel_list if p.category == "企业编人员"]

    # 材料费
    mat_result = await db.execute(select(BudgetMaterial).where(BudgetMaterial.project_id == project_id).order_by(BudgetMaterial.sort_order))
    mat_list = mat_result.scalars().all()

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

    # ====== 通用计算 ======
    salary_total = sum(p.salary_subtotal for p in personnel_list)
    welfare_total = sum(p.welfare_subtotal for p in personnel_list)
    coord_total = sum(p.coordination_subtotal for p in personnel_list)
    union_total = sum(p.union_subtotal for p in personnel_list)
    personnel_total = sum(p.total for p in personnel_list)

    mat_total = sum(m.amount for m in mat_list)
    equip_total = sum(e.amount for e in equip_list)
    labor_total = sum(l.amount for l in labor_list)
    sub_total = sum(s2.amount for s2 in sub_list)

    def dc_sum(cat):
        return sum(d.amount for d in dc_list if d.category == cat)

    dc_all = [
        ("运输费", dc_sum("运输费")),
        ("装卸费", dc_sum("装卸费")),
        ("检验试验费", dc_sum("试验检测费")),
        ("维修（护）费", dc_sum("维修(护)费") + dc_sum("维修费")),
        ("劳务费", labor_total),
        ("分包工程款", sub_total),
        ("办公费", dc_sum("办公费")),
        ("出版印刷费", dc_sum("出版印刷费")),
        ("水电费", dc_sum("水电费")),
        ("邮电费", dc_sum("邮电费")),
        ("取暖费", dc_sum("取暖费")),
        ("交通费", dc_sum("交通费")),
    ]
    dc_total = sum(a for _, a in dc_all)
    construction_total = personnel_total + mat_total + equip_total + dc_total
    rd_total = sum(r.amount for r in rd_list)
    other_total = sum(o.amount for o in other_list)

    han_shui = contract_amount
    shui_lv = tax_rate
    xiao_xiang = round(han_shui / (1 + shui_lv) * shui_lv, 2) if shui_lv > 0 else 0
    jin_xiang = 0
    ying_jiao = round(xiao_xiang - jin_xiang, 2)
    fu_jia = round(ying_jiao * 0.12, 2)
    gong_cheng_cb = round(construction_total + fu_jia, 2)
    shui_hou_sr = round(han_shui / (1 + shui_lv), 2) if shui_lv > 0 else han_shui
    mao_li_run = round(shui_hou_sr - gong_cheng_cb, 2)
    li_run_lv = round(mao_li_run / shui_hou_sr, 4) if shui_hou_sr > 0 else 0

    # =====================================================================
    # Sheet 1: 说明 - 匹配 DX20260411测绘预算.xlsx 格式
    # =====================================================================
    ws1 = wb.active
    ws1.title = "说明"

    # Column widths matching reference
    col_w1 = [5.625, 8.625, 17.5, 6.75, 7.375, 10.25, 9.375, 10.5, 11.375, 11.875, 11.25, 9.5, 7.75, 22.125]
    for i, w in enumerate(col_w1, 1):
        ws1.column_dimensions[get_column_letter(i)].width = w

    # Row heights matching reference
    ws1.row_dimensions[1].height = 61.15
    for r in range(2, 38):
        ws1.row_dimensions[r].height = 21.75
    ws1.row_dimensions[38].height = 43.9

    # Fonts matching reference
    s1_title_font = Font(name="宋体", size=18, bold=True, underline="single")
    s1_section_font = Font(name="宋体", size=16, bold=True)
    s1_content_font = Font(name="宋体", size=14, bold=True)
    s1_bottom_font = Font(name="宋体", size=16, bold=True)
    s1_center_wrap = Alignment(horizontal="center", vertical="center", wrap_text=True)
    s1_center = Alignment(horizontal="center", vertical="center")
    s1_left = Alignment(horizontal="left", vertical="center")
    s1_left_wrap = Alignment(horizontal="left", vertical="center", wrap_text=True)

    def _s1(ws, r, c, val, font=None, align=None):
        """Set cell value, font, alignment, and thin border"""
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = font or s1_content_font
        cell.alignment = align or s1_left
        cell.border = thin_border
        return cell

    def _border_all(ws, min_r, max_r, min_c, max_c):
        """Apply thin border to all cells in range"""
        for row in range(min_r, max_r + 1):
            for col in range(min_c, max_c + 1):
                ws.cell(row=row, column=col).border = thin_border

    # --- Title row 1 ---
    ws1.merge_cells("A1:N1")
    _s1(ws1, 1, 1, f"{project_name}成本费用预算编制说明" if project_name else "项目成本费用预算编制说明",
        font=s1_title_font, align=s1_center_wrap)

    # --- Section: 工程概况 (rows 2-10) ---
    ws1.merge_cells("A2:A10")
    _s1(ws1, 2, 1, "工程概况", font=s1_section_font, align=s1_center_wrap)

    ws1.merge_cells("B2:N2")
    _s1(ws1, 2, 2, f"工程名称：{project_name}")

    ws1.merge_cells("B3:I3")
    _s1(ws1, 3, 2, f"甲方全称：{party_a}")
    _s1(ws1, 3, 10, "联系人")
    ws1.merge_cells("K3:L3")
    _s1(ws1, 3, 11, contact_person or "", align=s1_center_wrap)
    _s1(ws1, 3, 13, "电话", align=s1_center_wrap)
    _s1(ws1, 3, 14, str(contact_phone) if contact_phone else "")

    ws1.merge_cells("B4:N4")
    _s1(ws1, 4, 2, f"甲方通讯地址：{address}")

    ws1.merge_cells("B5:N5")
    _s1(ws1, 5, 2, f"工程所在地：{location}")

    ws1.merge_cells("B6:I6")
    _s1(ws1, 6, 2, f"开竣工日期：{start_date}-{end_date}")
    ws1.merge_cells("J6:N6")
    _s1(ws1, 6, 10, f"计划工期：{duration}")

    # Row 7: 合同额 + 税率
    _s1(ws1, 7, 2, "合 同 额：")
    ws1.merge_cells("D7:E7")
    _s1(ws1, 7, 4, contract_amount if contract_amount else "", align=s1_center)
    _s1(ws1, 7, 6, "元")
    _s1(ws1, 7, 7, "税率", align=s1_center)
    ws1.merge_cells("H7:I7")
    _s1(ws1, 7, 8, tax_rate if tax_rate else "", align=s1_center)
    ws1.merge_cells("J7:N7")

    ws1.merge_cells("B8:I8")
    _s1(ws1, 8, 2, f"合同签订时间：{sign_date}", align=Alignment(horizontal="left", vertical="top"))
    ws1.merge_cells("J8:N8")
    _s1(ws1, 8, 10, f"合同编号：{contract_no}")

    ws1.merge_cells("B9:N9")
    _s1(ws1, 9, 2, f"实施单位：{unit}")

    ws1.merge_cells("B10:N10")
    _s1(ws1, 10, 2, f"项目经理：{manager}                          技术负责：{tech}")

    # --- Section: 编制依据 (rows 11-14) ---
    ws1.merge_cells("A11:A14")
    _s1(ws1, 11, 1, "编制依据", font=s1_section_font, align=s1_center_wrap)
    ws1.merge_cells("B11:N14")
    _s1(ws1, 11, 2, basis or "", align=s1_left_wrap)

    # --- Section: 施工条件 (rows 15-21) ---
    ws1.merge_cells("A15:A21")
    _s1(ws1, 15, 1, "施工条件", font=s1_section_font, align=s1_center_wrap)
    ws1.merge_cells("B15:N21")
    _s1(ws1, 15, 2, conditions or "", align=s1_left_wrap)

    # --- Section: 工作内容 (rows 22-31) ---
    ws1.merge_cells("A22:A31")
    _s1(ws1, 22, 1, "工作内容", font=s1_section_font, align=s1_center_wrap)
    ws1.merge_cells("B22:N31")
    _s1(ws1, 22, 2, work_content or "", align=s1_left_wrap)

    # --- Section: 其他 (rows 32-37) ---
    ws1.merge_cells("A32:A37")
    _s1(ws1, 32, 1, "其他", font=s1_section_font, align=s1_center_wrap)
    ws1.merge_cells("B32:N37")
    _s1(ws1, 32, 2, other_info or "", align=s1_center)

    # --- Bottom row 38 ---
    ws1.merge_cells("A38:N38")
    bottom_text = f"填表：{drafter}                      校核：{checker}                       审核：{reviewer}"
    _s1(ws1, 38, 1, bottom_text, font=s1_bottom_font, align=s1_center_wrap)

    # Apply thin borders to all cells in the sheet
    _border_all(ws1, 1, 38, 1, 14)

    # =====================================================================
    # Sheet 2: 项目成本科目及归集说明
    # =====================================================================
    ws2 = wb.create_sheet("项目成本科目及归集说明")
    # Column widths matching reference
    col_w2 = [5, 13, 4.88, 36.25, 24.38, 167, 12.62, 14.75]
    for i, w in enumerate(col_w2, 1):
        ws2.column_dimensions[get_column_letter(i)].width = w

    # Row heights
    ws2.row_dimensions[1].height = 22.5
    for r in range(2, 60):
        ws2.row_dimensions[r].height = 19.5

    # Fonts matching reference
    s2_title = Font(name="宋体", size=18, bold=True)
    s2_hdr = Font(name="宋体", size=16)
    s2_hdr_tnr = Font(name="Times New Roman", size=16)
    s2_cat = Font(name="宋体", size=16, bold=True)
    s2_item = Font(name="宋体", size=16)
    s2_align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    s2_align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    s2_green = PatternFill(start_color="FF92D050", end_color="FF92D050", fill_type="solid")

    def _s2_cell(ws, r, c, val, font=None, align=None, fill=None):
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = font or s2_item
        cell.alignment = align or s2_align_left
        cell.border = thin_border
        if fill:
            cell.fill = fill
        return cell

    def _s2_border_row(ws, r, max_c):
        for c in range(1, max_c + 1):
            ws.cell(row=r, column=c).border = thin_border

    # Title
    ws2.merge_cells("A1:H1")
    _s2_cell(ws2, 1, 1, "项目成本科目及归集说明", font=s2_title, align=s2_align_center)

    # Headers in rows 2-3 (merged vertically)
    ws2.merge_cells("A2:C3")
    ws2.merge_cells("D2:D3")
    ws2.merge_cells("E2:E3")
    ws2.merge_cells("F2:F3")
    ws2.merge_cells("G2:G3")
    ws2.merge_cells("H2:H3")
    _s2_cell(ws2, 2, 4, "工   作   内   容", font=s2_hdr_tnr, align=s2_align_center)
    _s2_cell(ws2, 2, 5, "科目代码", font=s2_hdr, align=s2_align_center)
    _s2_cell(ws2, 2, 6, "包括事项", font=s2_hdr, align=s2_align_center)
    _s2_cell(ws2, 2, 7, "金额", font=s2_hdr, align=s2_align_center)
    _s2_cell(ws2, 2, 8, "备 注", font=s2_hdr, align=s2_align_center)
    for r in [2, 3]:
        _s2_border_row(ws2, r, 8)

    # ---- Cost科目 tree ----
    # Computed subtotals for material categories
    mat_yuan = round(sum(m.amount for m in mat_list if m.category in ("原材料",)), 2)
    mat_zhuan = round(sum(m.amount for m in mat_list if m.category in ("专用材料费", "专用材料")), 2)
    mat_ran = round(sum(m.amount for m in mat_list if m.category in ("燃油", "燃油费")), 2)
    mat_tech = round(sum(m.amount for m in mat_list if m.category in ("技术资料费", "技术资料")), 2)

    dc_data = {}  # category -> sum
    for d in dc_list:
        dc_data[d.category] = round((dc_data.get(d.category, 0) + d.amount), 2)

    def _dc(cat):
        return dc_data.get(cat, 0)

    er_total = dc_sum("运输费")
    xie_total = dc_sum("装卸费")
    jianyan_total = dc_sum("试验检测费")
    weixiu_total = dc_sum("维修(护)费") + dc_sum("维修费")
    bangong_total = dc_sum("办公费")
    chuban_total = dc_sum("出版印刷费")
    shuidian_total = dc_sum("水电费")
    youdian_total = dc_sum("邮电费")
    qunuan_total = dc_sum("取暖费")
    jiaotong_total = dc_sum("交通费")

    # Tree structure: (row, col, val, font, merge, align)
    r2 = 4
    # Row 4: 一、工程施工
    ws2.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=4)
    _s2_cell(ws2, r2, 1, "一、工程施工", font=s2_cat)
    _s2_cell(ws2, r2, 7, round(construction_total, 2), align=s2_align_center, fill=s2_green)
    _s2_cell(ws2, r2, 8, "元", align=s2_align_center)
    _s2_border_row(ws2, r2, 8)
    r2 += 1

    # 1.1人工费
    ws2.merge_cells(start_row=r2, start_column=2, end_row=r2, end_column=4)
    _s2_cell(ws2, r2, 2, "1.1人工费", font=s2_cat)
    _s2_cell(ws2, r2, 6, "企事业编", font=s2_cat)
    _s2_border_row(ws2, r2, 8)
    r2 += 1

    personnel_items = [
        ("⑴职工薪酬", "5401.01.01", "基本工资、津贴补贴和基础绩效工资、野外津贴", salary_total),
        ("⑵职工福利费", "5401.01.02", "特指防暑降温费", welfare_total),
        ("⑶单位统筹", "5401.01.03", "反映单位为在职人员缴纳的养老保险、职业年金、医疗保险、工伤保险、失业保险等各类社会保险费、残保金及住房公积金。（单位计提部分）", coord_total),
        ("⑷工会经费", "5401.01.05", "反映单位单位计提的工会经费", union_total),
    ]
    for name, code, desc, amt in personnel_items:
        ws2.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=2)
        ws2.merge_cells(start_row=r2, start_column=3, end_row=r2, end_column=4)
        _s2_cell(ws2, r2, 1, name)
        _s2_cell(ws2, r2, 5, code, align=s2_align_center)
        _s2_cell(ws2, r2, 6, desc)
        _s2_cell(ws2, r2, 7, round(amt, 2), align=s2_align_center, fill=s2_green)
        _s2_border_row(ws2, r2, 8)
        r2 += 1

    # 2.1材料费
    ws2.merge_cells(start_row=r2, start_column=2, end_row=r2, end_column=4)
    _s2_cell(ws2, r2, 2, "2.1材料费", font=s2_cat)
    _s2_border_row(ws2, r2, 8)
    r2 += 1

    mat_items = [
        ("⑴原材料", "5401.02.01", "除专用材料外的钢材、水泥、粒料、土方等材料", mat_yuan),
        ("⑵燃油", "5401.02.02", "为动力设备提供的燃油费（柴油费用）", mat_ran),
        ("⑷专用材料费", "5401.02.04", "为项目采购的或者专项定制的钻杆、钻具、钻头、地质管等材料", mat_zhuan),
        ("⑸技术资料费", "5401.02.05", "购买标书费、资料收集费", mat_tech),
    ]
    for name, code, desc, amt in mat_items:
        ws2.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=2)
        ws2.merge_cells(start_row=r2, start_column=3, end_row=r2, end_column=4)
        _s2_cell(ws2, r2, 1, name)
        _s2_cell(ws2, r2, 5, code, align=s2_align_center)
        _s2_cell(ws2, r2, 6, desc)
        _s2_cell(ws2, r2, 7, amt, align=s2_align_center, fill=s2_green)
        _s2_border_row(ws2, r2, 8)
        r2 += 1

    # 3.1机械使用费
    ws2.merge_cells(start_row=r2, start_column=2, end_row=r2, end_column=4)
    _s2_cell(ws2, r2, 2, "3.1机械使用费", font=Font(name="Times New Roman", size=16, bold=True))
    _s2_border_row(ws2, r2, 8)
    r2 += 1

    equip_items = [
        ("⑴折旧费", "5401.03.01", "自有设备折旧费", 0),
        ("⑵设备租赁费", "5401.03.02", "租赁机械设备仪器发生的费用（非交通工具）", equip_total),
    ]
    for name, code, desc, amt in equip_items:
        ws2.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=2)
        ws2.merge_cells(start_row=r2, start_column=3, end_row=r2, end_column=4)
        _s2_cell(ws2, r2, 1, name)
        _s2_cell(ws2, r2, 5, code, align=s2_align_center)
        _s2_cell(ws2, r2, 6, desc)
        _s2_cell(ws2, r2, 7, round(amt, 2), align=s2_align_center, fill=s2_green)
        _s2_border_row(ws2, r2, 8)
        r2 += 1

    # 4.1其他直接费
    ws2.merge_cells(start_row=r2, start_column=2, end_row=r2, end_column=4)
    _s2_cell(ws2, r2, 2, "4.1其他直接费", font=s2_cat)
    _s2_border_row(ws2, r2, 8)
    r2 += 1

    dc_items = [
        ("⑴运输费", "5401.04.01", "运输费用", er_total),
        ("⑵装卸费", "5401.04.02", "装卸费用、转运费用、搬倒费用", xie_total),
        ("⑶检验试验费", "5401.04.03", "水泥、钢筋等原材料的抽检费用", jianyan_total),
        ("⑷维修（护）费", "5401.04.04", "机械设备维修", weixiu_total),
        ("⑸劳务费", "5401.04.05", "", labor_total),
        ("⑺分包工程款", "5401.04.07", "劳务分包、专业分包、技术服务费、委托试验费等费用", sub_total),
        ("⑻办公费", "5401.04.08", "购买办公耗材、办公器具、临时办公配套设施费、生活用品等", bangong_total),
        ("⑼出版印刷费", "5401.04.09", "报告装订、打印费用", chuban_total),
        ("⑽水电费", "5401.04.10", "", shuidian_total),
        ("⑾邮电费", "5401.04.11", "", youdian_total),
        ("⒀交通费", "5401.04.13", "", jiaotong_total),
    ]
    for name, code, desc, amt in dc_items:
        ws2.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=2)
        ws2.merge_cells(start_row=r2, start_column=3, end_row=r2, end_column=4)
        _s2_cell(ws2, r2, 1, name)
        _s2_cell(ws2, r2, 5, code, align=s2_align_center)
        _s2_cell(ws2, r2, 6, desc)
        _s2_cell(ws2, r2, 7, round(amt, 2), align=s2_align_center, fill=s2_green)
        _s2_border_row(ws2, r2, 8)
        r2 += 1

    # 取暖费 (usually 0, but include if present)
    if qunuan_total > 0:
        ws2.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=2)
        ws2.merge_cells(start_row=r2, start_column=3, end_row=r2, end_column=4)
        _s2_cell(ws2, r2, 1, "⑿取暖费")
        _s2_cell(ws2, r2, 5, "5401.04.12", align=s2_align_center)
        _s2_cell(ws2, r2, 7, round(qunuan_total, 2), align=s2_align_center, fill=s2_green)
        _s2_border_row(ws2, r2, 8)
        r2 += 1

    # Bottom summary row
    ws2.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=8)
    _s2_cell(ws2, r2, 1, "", align=s2_align_center)
    _s2_border_row(ws2, r2, 8)
    r2 += 1

    # Tax / profit rows
    rd_company = 0  # 二、公司承担研发费用
    tax_lines = [
        ("二、公司承担研发费用", 0),
        (f"三、销项增值税 = 含税合同额/(1+税率)*税率", xiao_xiang),
        ("四、可抵扣进项增值税合计", jin_xiang),
        (f"五、应缴税额 = (三 - 四)", ying_jiao),
        ("六、附加税 = 五 * 12%", fu_jia),
        ("七、工程成本费用 = (一 - 二 + 六)", gong_cheng_cb),
        (f"八、税后收入 = 含税合同额/(1+税率)", shui_hou_sr),
        ("九、工程预算毛利润 = (八 - 七)", mao_li_run),
    ]
    for name, amt in tax_lines:
        ws2.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=4)
        _s2_cell(ws2, r2, 1, name, font=s2_cat)
        _s2_cell(ws2, r2, 7, round(amt, 2), align=s2_align_center, fill=s2_green)
        _s2_border_row(ws2, r2, 8)
        r2 += 1

    # =====================================================================
    # Sheet 3: 总表
    # =====================================================================
    ws3 = wb.create_sheet("总表")
    col_w3 = [5, 13, 4.88, 41.25, 19, 17.25, 13.38, 35.75]
    for i, w in enumerate(col_w3, 1):
        ws3.column_dimensions[get_column_letter(i)].width = w

    ws3.row_dimensions[1].height = 43.15
    ws3.row_dimensions[2].height = 24.95
    ws3.row_dimensions[3].height = 24.95

    # Fonts
    s3_title = Font(name="宋体", size=18, bold=True)
    s3_hdr = Font(name="宋体", size=16)
    s3_hdr_tnr = Font(name="Times New Roman", size=16)
    s3_cat = Font(name="宋体", size=16, bold=True)
    s3_item = Font(name="宋体", size=16)
    s3_sub = Font(name="宋体", size=14)  # for deeper levels
    s3_align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    s3_align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)

    def _s3_cell(ws, r, c, val, font=None, align=None, fill=None):
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = font or s3_item
        cell.alignment = align or s3_align_left
        cell.border = thin_border
        if fill: cell.fill = fill
        return cell

    def _s3_border_row(ws, r):
        for c in range(1, 9):
            ws.cell(row=r, column=c).border = thin_border

    # Title
    ws3.merge_cells("A1:H1")
    _s3_cell(ws3, 1, 1, "项目成本费用预算总表", font=s3_title, align=s3_align_center)

    # Headers
    ws3.merge_cells("A2:C3")
    ws3.merge_cells("D2:D3")
    ws3.merge_cells("E2:E3")
    ws3.merge_cells("F2:F3")
    ws3.merge_cells("G2:G3")
    ws3.merge_cells("H2:H3")
    _s3_cell(ws3, 2, 4, "工   作   内   容", font=s3_hdr_tnr, align=s3_align_center)
    _s3_cell(ws3, 2, 5, "金额", font=s3_hdr, align=s3_align_center)
    _s3_cell(ws3, 2, 6, "备 注", font=s3_hdr, align=s3_align_center)
    _s3_cell(ws3, 2, 7, "税率", font=s3_hdr, align=s3_align_center)
    _s3_cell(ws3, 2, 8, "可抵扣增值税", font=s3_hdr, align=s3_align_center)
    for r in [2, 3]:
        _s3_border_row(ws3, r)

    # Content rows
    r3 = 4
    # Row 4: 一、工程施工
    ws3.merge_cells(start_row=r3, start_column=1, end_row=r3, end_column=4)
    _s3_cell(ws3, r3, 1, "一、工程施工", font=s3_cat)
    _s3_cell(ws3, r3, 5, round(construction_total, 2), font=Font(name="Times New Roman", size=16, bold=True), align=s3_align_center, fill=s2_green)
    _s3_cell(ws3, r3, 6, "元", align=s3_align_center)
    _s3_cell(ws3, r3, 8, round(construction_total * tax_rate if tax_rate > 0 else 0, 2), font=Font(name="宋体", size=16, bold=True), align=s3_align_center, fill=s2_green)
    for rr in range(r3, r3 + 1):
        for cc in range(1, 9):
            ws3.cell(row=rr, column=cc).border = thin_border
            if ws3.cell(row=rr, column=cc).alignment.vertical is None:
                ws3.cell(row=rr, column=cc).alignment = s3_align_center
    r3 += 1

    # Row 5: 1.1人工费
    ws3.merge_cells(start_row=r3, start_column=2, end_row=r3, end_column=4)
    _s3_cell(ws3, r3, 2, "1.1人工费", font=s3_cat)
    _s3_cell(ws3, r3, 5, round(personnel_total, 2), font=Font(name="Times New Roman", size=16, bold=True), align=s3_align_center, fill=s2_green)
    _s3_cell(ws3, r3, 6, "附明细", align=s3_align_center)
    _s3_border_row(ws3, r3)
    r3 += 1

    # Personnel sub-items
    pers_subs = [
        ("⑴职工薪酬", salary_total),
        ("⑵职工福利费", welfare_total),
        ("⑶单位统筹", coord_total),
        ("⑷工会经费", union_total),
    ]
    for name, amt in pers_subs:
        ws3.merge_cells(start_row=r3, start_column=1, end_row=r3, end_column=2)
        ws3.merge_cells(start_row=r3, start_column=3, end_row=r3, end_column=4)
        _s3_cell(ws3, r3, 1, name, font=s3_item)
        _s3_cell(ws3, r3, 5, round(amt, 2), font=Font(name="Times New Roman", size=16), align=s3_align_center, fill=s2_green)
        _s3_cell(ws3, r3, 7, tax_rate if tax_rate > 0 else "", align=s3_align_center)
        _s3_cell(ws3, r3, 8, round(amt * tax_rate, 2) if tax_rate > 0 else "", align=s3_align_center, fill=s2_green)
        _s3_border_row(ws3, r3)
        r3 += 1

    # Row: 2.1材料费
    ws3.merge_cells(start_row=r3, start_column=2, end_row=r3, end_column=4)
    _s3_cell(ws3, r3, 2, "2.1材料费", font=s3_cat)
    _s3_cell(ws3, r3, 5, round(mat_total, 2), font=Font(name="宋体", size=16, bold=True), align=s3_align_center, fill=s2_green)
    _s3_cell(ws3, r3, 8, round(mat_total * tax_rate if tax_rate > 0 else 0, 2), font=Font(name="宋体", size=16, bold=True), align=s3_align_center, fill=s2_green)
    _s3_border_row(ws3, r3)
    r3 += 1

    mat_subs = [
        ("⑴原材料", mat_yuan),
        ("⑵专用材料费", mat_zhuan),
        ("⑶燃油", mat_ran),
        ("⑷技术资料费", mat_tech),
    ]
    for name, amt in mat_subs:
        ws3.merge_cells(start_row=r3, start_column=1, end_row=r3, end_column=2)
        ws3.merge_cells(start_row=r3, start_column=3, end_row=r3, end_column=4)
        _s3_cell(ws3, r3, 1, name, font=s3_item)
        _s3_cell(ws3, r3, 5, amt, font=Font(name="Times New Roman", size=16), align=s3_align_center, fill=s2_green)
        _s3_cell(ws3, r3, 7, tax_rate if tax_rate > 0 else "", align=s3_align_center)
        _s3_cell(ws3, r3, 8, round(amt * tax_rate, 2) if tax_rate > 0 else "", align=s3_align_center, fill=s2_green)
        _s3_border_row(ws3, r3)
        r3 += 1

    # Row: 3.1机械使用费
    ws3.merge_cells(start_row=r3, start_column=2, end_row=r3, end_column=4)
    _s3_cell(ws3, r3, 2, "3.1机械使用费", font=Font(name="Times New Roman", size=16, bold=True))
    _s3_cell(ws3, r3, 5, round(equip_total, 2), font=Font(name="Times New Roman", size=16, bold=True), align=s3_align_center, fill=s2_green)
    _s3_cell(ws3, r3, 8, round(equip_total * tax_rate if tax_rate > 0 else 0, 2), font=Font(name="Times New Roman", size=16, bold=True), align=s3_align_center, fill=s2_green)
    _s3_border_row(ws3, r3)
    r3 += 1

    # 设备租赁费
    ws3.merge_cells(start_row=r3, start_column=1, end_row=r3, end_column=2)
    ws3.merge_cells(start_row=r3, start_column=3, end_row=r3, end_column=4)
    _s3_cell(ws3, r3, 1, "⑴设备租赁费", font=s3_item)
    _s3_cell(ws3, r3, 5, round(equip_total, 2), font=Font(name="Times New Roman", size=16), align=s3_align_center, fill=s2_green)
    _s3_cell(ws3, r3, 7, tax_rate if tax_rate > 0 else "", align=s3_align_center)
    _s3_cell(ws3, r3, 8, round(equip_total * tax_rate, 2) if tax_rate > 0 else "", align=s3_align_center, fill=s2_green)
    _s3_border_row(ws3, r3)
    r3 += 1

    # Row: 4.1其他直接费
    ws3.merge_cells(start_row=r3, start_column=2, end_row=r3, end_column=4)
    _s3_cell(ws3, r3, 2, "4.1其他直接费", font=s3_cat)
    _s3_cell(ws3, r3, 5, round(dc_total, 2), font=Font(name="Times New Roman", size=16, bold=True), align=s3_align_center, fill=s2_green)
    _s3_cell(ws3, r3, 6, "附明细", align=s3_align_center)
    _s3_cell(ws3, r3, 8, round(dc_total * tax_rate if tax_rate > 0 else 0, 2), font=Font(name="宋体", size=16, bold=True), align=s3_align_center, fill=s2_green)
    _s3_border_row(ws3, r3)
    r3 += 1

    # Direct cost sub-items (matching reference tree)
    dc_tree = [
        ("⑴运输费", er_total),
        ("⑵装卸费", xie_total),
        ("⑶检验试验费", jianyan_total),
        ("⑷维修（护）费", weixiu_total),
        ("⑸劳务费", labor_total),
        ("⑺分包工程款", sub_total),
        ("⑻办公费", bangong_total),
        ("⑼出版印刷费", chuban_total),
        ("⑽水电费", shuidian_total),
        ("⑾邮电费", youdian_total),
        ("⑿取暖费", qunuan_total),
        ("⒀交通费", jiaotong_total),
    ]
    for name, amt in dc_tree:
        if amt == 0 and name not in ["⑸劳务费", "⑺分包工程款"]:
            # Skip sub-items with 0 amount, except structural ones
            pass
        ws3.merge_cells(start_row=r3, start_column=1, end_row=r3, end_column=2)
        ws3.merge_cells(start_row=r3, start_column=3, end_row=r3, end_column=4)
        _s3_cell(ws3, r3, 1, name, font=s3_item)
        _s3_cell(ws3, r3, 5, round(amt, 2), font=Font(name="Times New Roman", size=16), align=s3_align_center, fill=s2_green)
        _s3_cell(ws3, r3, 7, tax_rate if tax_rate > 0 else "", align=s3_align_center)
        _s3_cell(ws3, r3, 8, round(amt * tax_rate, 2) if tax_rate > 0 else "", align=s3_align_center, fill=s2_green)
        _s3_border_row(ws3, r3)
        r3 += 1

    # Empty separator
    ws3.merge_cells(start_row=r3, start_column=1, end_row=r3, end_column=4)
    _s3_cell(ws3, r3, 1, "", font=s3_cat)
    _s3_border_row(ws3, r3)
    r3 += 1

    # R&D and other costs (if any)
    if rd_total > 0:
        ws3.merge_cells(start_row=r3, start_column=1, end_row=r3, end_column=4)
        _s3_cell(ws3, r3, 1, "研发费用", font=s3_cat)
        _s3_cell(ws3, r3, 5, round(rd_total, 2), align=s3_align_center, fill=s2_green)
        _s3_border_row(ws3, r3)
        r3 += 1
    if other_total > 0:
        ws3.merge_cells(start_row=r3, start_column=1, end_row=r3, end_column=4)
        _s3_cell(ws3, r3, 1, "其他费用", font=s3_cat)
        _s3_cell(ws3, r3, 5, round(other_total, 2), align=s3_align_center, fill=s2_green)
        _s3_border_row(ws3, r3)
        r3 += 1

    # Tax section
    tax3 = [
        ("二、公司承担研发费用", 0),
        (f"三、销项增值税 = 含税合同额/(1+{tax_rate})×{tax_rate}", xiao_xiang),
        ("四、可抵扣进项增值税合计", jin_xiang),
        ("五、应缴税额 = (三 - 四)", ying_jiao),
        ("六、附加税 = 五 × 12%", fu_jia),
        ("七、工程成本费用 = (一 - 二 + 六)", gong_cheng_cb),
        (f"八、税后收入 = 含税合同额/(1+{tax_rate})", shui_hou_sr),
        ("九、工程预算毛利润 = (八 - 七)", mao_li_run),
    ]
    for name, amt in tax3:
        ws3.merge_cells(start_row=r3, start_column=1, end_row=r3, end_column=4)
        _s3_cell(ws3, r3, 1, name, font=s3_cat)
        _s3_cell(ws3, r3, 5, round(amt, 2), font=Font(name="Times New Roman", size=16, bold=True), align=s3_align_center, fill=s2_green)
        _s3_border_row(ws3, r3)
        r3 += 1

    # Set alignment for all cells in the sheet
    for rr in range(4, r3):
        for cc in range(1, 9):
            cell = ws3.cell(row=rr, column=cc)
            if cell.alignment.vertical is None:
                cell.alignment = s3_align_center
            cell.border = thin_border

    # Row heights for content
    for rr in range(4, r3):
        if ws3.row_dimensions[rr].height is None:
            ws3.row_dimensions[rr].height = 30 if rr <= 6 else 28.15

    # =====================================================================
    # Sheet 4: 1.1人工费
    # =====================================================================
    ws4 = wb.create_sheet("1.1人工费")
    # Columns: A(类别) B(岗位) C(姓名) D(单位) E-J(工资构成) K(工作时间) L(野外时间)
    #           M(薪酬小计) N(福利费小计) O(单位统筹小计) P(工会经费小计) Q(合计) R(单位人工费/月) S(归集)
    col_w4 = [5.62, 10.25, 10.12, 6.12, 11.25, 13, 9.38, 9.75, 13, 10.5,
              8.25, 10.75, 9.75, 13, 13, 13, 13, 11.62, 7.75]
    for i, w in enumerate(col_w4, 1):
        ws4.column_dimensions[get_column_letter(i)].width = w

    ws4.row_dimensions[1].height = 37.9
    ws4.row_dimensions[2].height = 27.95
    ws4.row_dimensions[3].height = 27.95

    s4_title = Font(name="宋体", size=16, bold=True)
    s4_hdr = Font(name="宋体", size=12, bold=True)
    s4_sub = Font(name="宋体", size=11, bold=True)
    s4_data = Font(name="宋体", size=11)
    s4_data_bold = Font(name="宋体", size=11, bold=True)
    s4_cat = Font(name="宋体", size=16, bold=True)
    s4_center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def _s4_cell(ws, r, c, val, font=None, align=None, fill=None):
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = font or s4_data
        cell.alignment = align or s4_center
        cell.border = thin_border
        if fill: cell.fill = fill
        return cell

    # Title
    ws4.merge_cells("A1:S1")
    _s4_cell(ws4, 1, 1, "1.1人工费", font=s4_title)

    # Row 2: main headers
    ws4.merge_cells("A2:A3")
    ws4.merge_cells("B2:B3")
    ws4.merge_cells("C2:C3")
    ws4.merge_cells("D2:D3")
    _s4_cell(ws4, 2, 1, "类别", font=s4_hdr)
    _s4_cell(ws4, 2, 2, "岗位", font=s4_hdr)
    _s4_cell(ws4, 2, 3, "姓名", font=s4_hdr)
    _s4_cell(ws4, 2, 4, "单位", font=s4_hdr)

    # 工资构成 merged header (E2:J2, 6 cols)
    ws4.merge_cells("E2:J2")
    _s4_cell(ws4, 2, 5, "工资构成", font=s4_hdr)

    ws4.merge_cells("K2:K3")
    ws4.merge_cells("L2:L3")
    _s4_cell(ws4, 2, 11, "工作时间", font=s4_hdr)
    _s4_cell(ws4, 2, 12, "野外时间", font=s4_hdr)

    # Remaining headers
    for c, label in [(13, "薪酬小计"), (14, "福利费\n小计"), (15, "单位统筹小计"),
                      (16, "工会经费\n小计"), (17, "合计"), (18, "单位人工费\n（月）"), (19, "归集")]:
        ws4.merge_cells(start_row=2, start_column=c, end_row=3, end_column=c)
        _s4_cell(ws4, 2, c, label, font=s4_hdr)

    # Row 3: sub-headers for 工资构成
    wage_subs = {5: "基本工资及津补贴", 6: "绩效", 7: "野外津贴", 8: "防暑降温", 9: "工会经费", 10: "单位统筹"}
    for c, label in wage_subs.items():
        _s4_cell(ws4, 3, c, label, font=s4_sub)

    # Fill borders on all header cells
    for r in [2, 3]:
        for c in range(1, 20):
            cell = ws4.cell(row=r, column=c)
            cell.border = thin_border

    # ---- Data rows ----
    def write_personnel_section(ws, start_row, cat_label, p_list):
        """Write a personnel category section matching reference format"""
        row = start_row
        if not p_list:
            _s4_cell(ws, row, 1, cat_label, font=s4_cat)
            for c in range(2, 20):
                _s4_cell(ws, row, c, "")
            return row + 1

        # Merge category label vertically
        end_row = start_row + len(p_list) - 1
        if len(p_list) > 1:
            ws.merge_cells(start_row=start_row, start_column=1, end_row=end_row, end_column=1)
        _s4_cell(ws, start_row, 1, cat_label, font=s4_cat)

        for i, p in enumerate(p_list):
            rr = start_row + i
            unit_cost = round(p.total / p.work_months, 2) if p.work_months and p.work_months > 0 else 0

            _s4_cell(ws, rr, 1, "", font=s4_cat)  # merged, only first has label
            _s4_cell(ws, rr, 2, p.position or "")
            _s4_cell(ws, rr, 3, p.employee_name or "")
            _s4_cell(ws, rr, 4, "人·月")

            # Wage components (E-J)
            _s4_cell(ws, rr, 5, p.base_salary)
            _s4_cell(ws, rr, 6, p.performance)
            _s4_cell(ws, rr, 7, p.field_allowance)
            _s4_cell(ws, rr, 8, p.heat_prevention)
            _s4_cell(ws, rr, 9, p.union_fee)
            _s4_cell(ws, rr, 10, p.unit_coordination)

            # Work months & field months (K, L)
            _s4_cell(ws, rr, 11, p.work_months)
            _s4_cell(ws, rr, 12, p.field_months)

            # Subtotals (M-Q) with green fills
            _s4_cell(ws, rr, 13, p.salary_subtotal, fill=s2_green)
            _s4_cell(ws, rr, 14, p.welfare_subtotal, fill=s2_green)
            _s4_cell(ws, rr, 15, p.coordination_subtotal, fill=s2_green)
            _s4_cell(ws, rr, 16, p.union_subtotal, fill=s2_green)
            _s4_cell(ws, rr, 17, p.total, fill=s2_green)

            _s4_cell(ws, rr, 18, unit_cost)
            _s4_cell(ws, rr, 19, "")

        return start_row + len(p_list)

    row4 = 4
    row4 = write_personnel_section(ws4, row4, "事业编人员", shiye_list)
    row4 = write_personnel_section(ws4, row4, "企业编人员", qiye_list)

    # ---- Summary row (row 18) ----
    # 事业编人员工资合计 (A18:B18) | =SUM(Q4:Q9) in C18:D18
    # 企业编人员工资合计 (E18:G18) | =SUM(Q10:Q17) in H18
    # 全部在职人员合计 (I18) | =SUM(K4:K17) in K18, etc.

    shiye_end = 3 + len(shiye_list)  # last row of shiye data
    qiye_start = shiye_end + 1
    qiye_end = qiye_start + len(qiye_list) - 1

    # Total summary row
    sum_row = row4
    ws4.merge_cells(start_row=sum_row, start_column=1, end_row=sum_row, end_column=2)
    ws4.merge_cells(start_row=sum_row, start_column=3, end_row=sum_row, end_column=4)
    ws4.merge_cells(start_row=sum_row, start_column=5, end_row=sum_row, end_column=7)
    _s4_cell(ws4, sum_row, 1, "事业编人员工资合计", font=s4_data_bold)
    _s4_cell(ws4, sum_row, 3, round(sum(p.total for p in shiye_list), 2), fill=s2_green)
    _s4_cell(ws4, sum_row, 5, "企业编人员工资合计", font=s4_data_bold)
    _s4_cell(ws4, sum_row, 8, round(sum(p.total for p in qiye_list), 2), fill=s2_green)
    _s4_cell(ws4, sum_row, 9, "全部在职人员合计", font=s4_data_bold)
    _s4_cell(ws4, sum_row, 11, round(sum(p.work_months for p in personnel_list), 2), fill=s2_green)
    _s4_cell(ws4, sum_row, 12, round(sum(p.field_months for p in personnel_list), 2), fill=s2_green)
    _s4_cell(ws4, sum_row, 13, round(salary_total, 2), font=s4_data_bold, fill=s2_green)
    _s4_cell(ws4, sum_row, 14, round(welfare_total, 2), font=s4_data_bold, fill=s2_green)
    _s4_cell(ws4, sum_row, 15, round(coord_total, 2), font=s4_data_bold, fill=s2_green)
    _s4_cell(ws4, sum_row, 16, round(union_total, 2), font=s4_data_bold, fill=s2_green)
    _s4_cell(ws4, sum_row, 17, round(personnel_total, 2), font=s4_data_bold, fill=s2_green)

    for c in range(1, 20):
        ws4.cell(row=sum_row, column=c).border = thin_border
        if ws4.cell(row=sum_row, column=c).alignment.vertical is None:
            ws4.cell(row=sum_row, column=c).alignment = s4_center
    sum_row += 1

    # Note row 1 (A19:S19 merged)
    ws4.merge_cells(start_row=sum_row, start_column=1, end_row=sum_row, end_column=19)
    _s4_cell(ws4, sum_row, 1, "单位人工费（月）=施工人员合计人工费/施工人员计划工作时间（月）。",
             font=Font(name="宋体", size=12))
    sum_row += 1

    # Note row 2 (A20:S20 merged)
    ws4.merge_cells(start_row=sum_row, start_column=1, end_row=sum_row, end_column=19)
    _s4_cell(ws4, sum_row, 1, "注：人员工资数额按照每个人2024年发放的工资分类按月进行计算得出，野外津贴的数额按照施工地固定补贴数额乘以实际施工天数得出",
             font=Font(name="宋体", size=12, bold=True))

    # Set row heights for data rows
    for r in range(4, sum_row):
        ws4.row_dimensions[r].height = 27.95

    # =====================================================================
    # Sheet 5: 2.1材料费
    # =====================================================================
    ws5 = wb.create_sheet("2.1材料费")
    col_w5 = [9, 15.62, 6.62, 13, 12.88, 6.5, 10.62, 6.38, 12.75, 31.5, 14.38]
    for i, w in enumerate(col_w5, 1):
        ws5.column_dimensions[get_column_letter(i)].width = w
    ws5.row_dimensions[1].height = 31.15
    ws5.row_dimensions[2].height = 27.95

    s5_title = Font(name="宋体", size=16, bold=True)
    s5_hdr = Font(name="宋体", size=12, bold=True)
    s5_data = Font(name="宋体", size=11)
    s5_bold = Font(name="宋体", size=11, bold=True)
    s5_center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def _s5(ws, r, c, val, font=None, fill=None):
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = font or s5_data
        cell.alignment = s5_center
        cell.border = thin_border
        if fill: cell.fill = fill

    ws5.merge_cells("B1:K1")
    _s5(ws5, 1, 2, "2.1 材料费", font=s5_title)

    h5 = {1: "序号", 2: "科目", 3: "名称", 5: "型号", 6: "单位", 7: "单价", 8: "数量", 9: "金额", 10: "预算说明", 11: "归集"}
    for c, v in h5.items():
        _s5(ws5, 2, c, v, font=s5_hdr)
    ws5.merge_cells("C2:D2")

    # Group materials by category
    mat_groups = [
        ("2.1.1", "原材料", [m for m in mat_list if m.category in ("原材料",)]),
        ("2.1.2", "专用材料费", [m for m in mat_list if m.category in ("专用材料费", "专用材料")]),
        ("2.1.3", "燃油费", [m for m in mat_list if m.category in ("燃油", "燃油费")]),
        ("2.1.4", "技术资料费", [m for m in mat_list if m.category in ("技术资料费", "技术资料")]),
    ]

    row5 = 3
    for code, cat_name, items in mat_groups:
        start_r = row5
        for m in items:
            _s5(ws5, row5, 1, code, font=s5_bold)
            _s5(ws5, row5, 2, cat_name, font=s5_bold)
            _s5(ws5, row5, 3, m.name or "")
            _s5(ws5, row5, 4, "")
            _s5(ws5, row5, 5, m.model or "")
            _s5(ws5, row5, 6, m.unit or "")
            _s5(ws5, row5, 7, m.unit_price)
            _s5(ws5, row5, 8, m.quantity)
            _s5(ws5, row5, 9, m.amount, fill=s2_green)
            _s5(ws5, row5, 10, m.remark or "")
            _s5(ws5, row5, 11, "")
            row5 += 1

        # Merge category columns for this group
        if row5 > start_r + 1:
            ws5.merge_cells(start_row=start_r, start_column=1, end_row=row5 - 1, end_column=1)
            ws5.merge_cells(start_row=start_r, start_column=2, end_row=row5 - 1, end_column=2)

        # Merge 名称 columns for each row
        for r in range(start_r, row5):
            ws5.merge_cells(start_row=r, start_column=3, end_row=r, end_column=4)

        # Subtotal row
        cat_total = round(sum(m.amount for m in items), 2)
        _s5(ws5, row5, 3, "小计", font=s5_bold)
        ws5.merge_cells(start_row=row5, start_column=3, end_row=row5, end_column=4)
        _s5(ws5, row5, 9, cat_total, font=s5_bold, fill=s2_green)
        row5 += 1

    # Grand total row
    ws5.merge_cells("A{0}:H{0}".format(row5))
    _s5(ws5, row5, 1, "合      计", font=s5_bold)
    _s5(ws5, row5, 9, round(mat_total, 2), font=s5_bold, fill=s2_green)
    row5 += 1

    # Sub-engineering total
    ws5.merge_cells("A{0}:H{0}".format(row5))
    _s5(ws5, row5, 1, "分部分项工程材料费合计", font=s5_bold)
    _s5(ws5, row5, 9, round(mat_total - mat_tech, 2), font=s5_bold, fill=s2_green)
    row5 += 1

    # Note row
    ws5.merge_cells("A{0}:J{0}".format(row5))
    _s5(ws5, row5, 1, "技术资料费计入管理费，其他材料费均计入相应分部分项工程的材料费", font=s5_bold,
        fill=None)
    ws5.cell(row=row5, column=1).alignment = Alignment(horizontal="left", vertical="center")
    for c in range(1, 11):
        ws5.cell(row=row5, column=c).border = thin_border

    for r in range(3, row5 + 1):
        ws5.row_dimensions[r].height = 27.95

    # =====================================================================
    # Sheet 6: 3.1机械费
    # =====================================================================
    ws6 = wb.create_sheet("3.1机械费")
    col_w6 = [13, 13.12, 11.5, 22.75, 13.38, 12.75, 5.5, 12.62, 13.25, 21.25, 22.25]
    for i, w in enumerate(col_w6, 1):
        ws6.column_dimensions[get_column_letter(i)].width = w
    ws6.row_dimensions[1].height = 36
    ws6.row_dimensions[2].height = 27.95

    s6_hdr = Font(name="宋体", size=12, bold=True)
    s6_sub = Font(name="宋体", size=11, bold=True)
    s6_data = Font(name="宋体", size=11)
    s6_center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def _s6(ws, r, c, val, font=None, fill=None):
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = font or s6_data
        cell.alignment = s6_center
        cell.border = thin_border
        if fill: cell.fill = fill

    ws6.merge_cells("A1:K1")
    _s6(ws6, 1, 1, "3.1机械使用费", font=s5_title)

    h6_map = {1: "3.1.1", 2: "租赁设备", 3: "分类", 4: "内容", 5: "对方单位名称",
              6: "型号", 7: "单价", 8: "数量", 9: "金额", 10: "预算说明", 11: "归集"}
    for c, v in h6_map.items():
        _s6(ws6, 2, c, v, font=s6_hdr)

    for r in range(3, 20):
        ws6.row_dimensions[r].height = 27.95

    row6 = 3
    for e in equip_list:
        _s6(ws6, row6, 3, e.classification or "工程施工用")
        _s6(ws6, row6, 4, e.content or "")
        _s6(ws6, row6, 5, e.counterparty or "")
        _s6(ws6, row6, 6, e.model or "")
        _s6(ws6, row6, 7, e.unit_price)
        _s6(ws6, row6, 8, e.quantity)
        _s6(ws6, row6, 9, e.amount, fill=s2_green)
        row6 += 1

    if not equip_list:
        row6 += 1  # at least one empty data row

    # Merge A+B for category
    ws6.merge_cells(start_row=3, start_column=1, end_row=row6 - 1, end_column=1)
    ws6.merge_cells(start_row=3, start_column=2, end_row=row6 - 1, end_column=2)

    # 合计 row
    ws6.merge_cells("A{0}:D{0}".format(row6))
    _s6(ws6, row6, 1, "合       计", font=Font(name="宋体", size=12, bold=True))
    _s6(ws6, row6, 9, round(equip_total, 2), font=Font(name="宋体", size=12, bold=True), fill=s2_green)
    ws6.merge_cells("E{0}:H{0}".format(row6))
    row6 += 1

    # 分部分项工程机械费合计
    ws6.merge_cells("A{0}:D{0}".format(row6))
    _s6(ws6, row6, 1, "分部分项工程机械费合计", font=Font(name="宋体", size=12, bold=True))
    _s6(ws6, row6, 9, round(equip_total, 2), font=Font(name="宋体", size=12, bold=True), fill=s2_green)
    ws6.merge_cells("E{0}:H{0}".format(row6))
    row6 += 1

    # =====================================================================
    # Sheet 7: 4.1.其他直接费
    # =====================================================================
    ws7 = wb.create_sheet("4.1.其他直接费")
    col_w7 = [8.75, 11.88, 20.25, 12.25, 11.88, 13.88, 15.38, 28.12, 28.25]
    for i, w in enumerate(col_w7, 1):
        ws7.column_dimensions[get_column_letter(i)].width = w

    s7_hdr = Font(name="宋体", size=12, bold=True)
    s7_data = Font(name="宋体", size=11)
    s7_bold = Font(name="宋体", size=12, bold=True)
    s7_center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def _s7(ws, r, c, val, font=None, fill=None, align=None):
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = font or s7_data
        cell.alignment = align or s7_center
        cell.border = thin_border
        if fill: cell.fill = fill

    ws7.merge_cells("A1:I1")
    _s7(ws7, 1, 1, "4.1其他直接费", font=s5_title)
    ws7.row_dimensions[1].height = 27.95
    ws7.row_dimensions[2].height = 27.95

    h7_map = {1: "序号", 2: "科目", 3: "内容", 4: "单位", 5: "单价", 6: "数量", 7: "金额", 8: "预算说明", 9: "归集"}
    for c, v in h7_map.items():
        _s7(ws7, 2, c, v, font=s7_hdr)

    # DC categories with reference numbering
    dc_cats = [
        ("4.1.1", "运输费", dc_by_cat.get("运输费", [])),
        ("4.1.2", "装卸费", dc_by_cat.get("装卸费", [])),
        ("4.1.3", "试验检测费", dc_by_cat.get("试验检测费", [])),
        ("4.1.4", "维修（护）费", dc_by_cat.get("维修(护)费", []) + dc_by_cat.get("维修费", [])),
        ("4.1.8", "办公费", dc_by_cat.get("办公费", [])),
        ("4.1.9", "出版印刷费", dc_by_cat.get("出版印刷费", [])),
        ("4.1.10", "水电费", dc_by_cat.get("水电费", [])),
        ("4.1.11", "邮电费", dc_by_cat.get("邮电费", [])),
        ("4.1.12", "取暖费", dc_by_cat.get("取暖费", [])),
        ("4.1.13", "交通费", dc_by_cat.get("交通费", [])),
    ]

    row7 = 3
    for code, cat_name, items in dc_cats:
        start_r = row7
        if not items:
            _s7(ws7, row7, 1, code, font=s7_bold)
            _s7(ws7, row7, 2, cat_name)
            _s7(ws7, row7, 7, 0, fill=s2_green)
            row7 += 1
        else:
            for d in items:
                _s7(ws7, row7, 1, code, font=s7_bold)
                _s7(ws7, row7, 2, cat_name)
                _s7(ws7, row7, 3, d.content or "")
                _s7(ws7, row7, 4, d.unit or "")
                _s7(ws7, row7, 5, d.unit_price)
                _s7(ws7, row7, 6, d.quantity)
                _s7(ws7, row7, 7, d.amount, fill=s2_green)
                _s7(ws7, row7, 8, d.remark or "")
                _s7(ws7, row7, 9, "")
                row7 += 1

        # Merge seq + category columns
        if row7 > start_r + 1:
            ws7.merge_cells(start_row=start_r, start_column=1, end_row=start_r, end_column=1)
            ws7.merge_cells(start_row=start_r, start_column=2, end_row=start_r, end_column=2)

        # Subtotal
        cat_sum_val = round(sum(d.amount for d in items), 2)
        _s7(ws7, row7, 3, "小计", font=s7_bold)
        _s7(ws7, row7, 7, cat_sum_val, font=s7_bold, fill=s2_green)
        row7 += 1

    for r in range(3, row7):
        ws7.row_dimensions[r].height = 27.95

    # =====================================================================
    # Sheet 8: 4.1.5劳务费
    # =====================================================================
    ws8 = wb.create_sheet("4.1.5劳务费")
    col_w8 = [13, 5.38, 9, 13, 13, 13, 13, 11.5, 19.25, 13]
    for i, w in enumerate(col_w8, 1):
        ws8.column_dimensions[get_column_letter(i)].width = w

    s8_hdr = Font(name="宋体", size=12, bold=True)
    s8_cat = Font(name="宋体", size=14, bold=True)
    s8_data = Font(name="宋体", size=11)
    s8_center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def _s8(ws, r, c, val, font=None, fill=None):
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = font or s8_data
        cell.alignment = s8_center
        cell.border = thin_border
        if fill: cell.fill = fill

    ws8.merge_cells("A1:J1")
    _s8(ws8, 1, 1, "4.1.5外聘人工费用", font=s5_title)
    ws8.row_dimensions[1].height = 30
    ws8.row_dimensions[2].height = 27.95

    h8_map = {1: "序号", 2: "类别", 3: "岗位", 4: "姓名", 5: "单位", 6: "数量", 7: "单价", 8: "金额", 9: "预算说明", 10: "归集"}
    for c, v in h8_map.items():
        _s8(ws8, 2, c, v, font=s8_hdr)

    # Group labor by category
    labor_groups = {}
    for l in labor_list:
        labor_groups.setdefault(l.category or "临时聘用人员", []).append(l)

    row8 = 3
    seq = 0
    for cat_name, items in labor_groups.items():
        start_r = row8
        for l in items:
            seq += 1
            _s8(ws8, row8, 1, f"4.1.5.{seq}", font=s8_bold)
            _s8(ws8, row8, 2, cat_name, font=s8_cat)
            _s8(ws8, row8, 3, l.position or "")
            _s8(ws8, row8, 4, l.employee_name or "")
            _s8(ws8, row8, 5, l.unit or "人·天数")
            _s8(ws8, row8, 6, l.quantity)
            _s8(ws8, row8, 7, l.unit_price)
            _s8(ws8, row8, 8, l.amount, fill=s2_green)
            _s8(ws8, row8, 9, l.remark or "")
            _s8(ws8, row8, 10, "")
            row8 += 1

        # Merge category columns
        if row8 > start_r + 1:
            ws8.merge_cells(start_row=start_r, start_column=1, end_row=row8 - 1, end_column=1)
            ws8.merge_cells(start_row=start_r, start_column=2, end_row=row8 - 1, end_column=2)

        # Subtotal
        cat_sum = round(sum(l.amount for l in items), 2)
        ws8.merge_cells(start_row=row8, start_column=3, end_row=row8, end_column=5)
        _s8(ws8, row8, 3, "小     计")
        _s8(ws8, row8, 8, cat_sum, fill=s2_green)
        row8 += 1

    if labor_list:
        # Grand total
        ws8.merge_cells(start_row=row8, start_column=3, end_row=row8, end_column=5)
        _s8(ws8, row8, 3, "合     计", font=Font(name="宋体", size=12))
        _s8(ws8, row8, 8, round(labor_total, 2), fill=s2_green)
        row8 += 1

        # Note
        ws8.merge_cells(start_row=row8, start_column=1, end_row=row8, end_column=7)
        _s8(ws8, row8, 1, "分部分项工程材料费合计", font=Font(name="宋体", size=12, bold=True))
        _s8(ws8, row8, 8, round(labor_total, 2), fill=s2_green)
        row8 += 1

        ws8.merge_cells(start_row=row8, start_column=1, end_row=row8 + 1, end_column=10)
        _s8(ws8, row8, 1, "注：临时聘用人员（外聘管理人员）指贯穿于工程始终或与全部分部分项工程都相关的，从事管理、后勤、技术指导工作的人员，野外雇工（外聘生产人员）指从事某项具体分部分项工程的技术、生产、生产管理人员",
            font=Font(name="宋体", size=10))

    for r in range(3, row8 + 1):
        ws8.row_dimensions[r].height = 21.95

    # =====================================================================
    # Sheet 9: 4.1.7分包工程款
    # =====================================================================
    ws9 = wb.create_sheet("4.1.7分包工程款")
    col_w9 = [5.5, 19.38, 14.62, 10.38, 15.88, 15, 17.75, 13.38]
    for i, w in enumerate(col_w9, 1):
        ws9.column_dimensions[get_column_letter(i)].width = w

    s9_hdr = Font(name="宋体", size=12, bold=True)
    s9_data = Font(name="宋体", size=11)
    s9_bold = Font(name="宋体", size=11, bold=True)
    s9_center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def _s9(ws, r, c, val, font=None, fill=None):
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = font or s9_data
        cell.alignment = s9_center
        cell.border = thin_border
        if fill: cell.fill = fill

    ws9.merge_cells("A1:H1")
    _s9(ws9, 1, 1, "4.1.7分包工程款", font=s5_title)
    ws9.row_dimensions[1].height = 42
    ws9.row_dimensions[2].height = 27.95

    h9_map = {1: "序号", 2: "项目", 3: "对方单位名称", 4: "工作量", 5: "单价（元/m）", 6: "合计", 7: "预算说明", 8: "归集"}
    for c, v in h9_map.items():
        _s9(ws9, 2, c, v, font=s9_hdr)

    # Group subcontracts by type
    sub_groups = [
        ("工程分包费", [s for s in sub_list if s.item_name and "工程分包" in (s.item_name or "")]),
        ("劳务分包费", [s for s in sub_list if s.item_name and "劳务分包" in (s.item_name or "")]),
        ("委托技术服务费", [s for s in sub_list if s.item_name and "技术服务" in (s.item_name or "")]),
        ("委托试验费", [s for s in sub_list if s.item_name and "试验" in (s.item_name or "")]),
    ]
    # If no category grouping, treat all as individual items
    if all(len(items) == 0 for _, items in sub_groups):
        sub_groups = [("", sub_list)]

    row9 = 3
    idx = 0
    for gname, items in sub_groups:
        if not items:
            continue
        start_r = row9
        for s in items:
            idx += 1
            _s9(ws9, row9, 1, idx)
            _s9(ws9, row9, 2, gname or s.item_name or "", font=s9_bold)
            _s9(ws9, row9, 3, s.counterparty or "")
            _s9(ws9, row9, 4, s.workload)
            _s9(ws9, row9, 5, s.unit_price)
            _s9(ws9, row9, 6, s.amount, fill=s2_green)
            _s9(ws9, row9, 7, s.remark or "")
            _s9(ws9, row9, 8, "")
            row9 += 1
        if gname:
            ws9.merge_cells(start_row=start_r, start_column=2, end_row=row9 - 1, end_column=2)

        # Subtotal
        _s9(ws9, row9, 1, "小   计", font=s9_bold)
        _s9(ws9, row9, 2, "")
        _s9(ws9, row9, 6, round(sum(s.amount for s in items), 2), font=s9_bold, fill=s2_green)
        ws9.merge_cells(start_row=row9, start_column=1, end_row=row9, end_column=2)
        row9 += 1

    if sub_list:
        # Grand total
        _s9(ws9, row9, 1, "合计", font=s9_bold)
        _s9(ws9, row9, 6, round(sub_total, 2), font=s9_bold, fill=s2_green)
        ws9.merge_cells(start_row=row9, start_column=1, end_row=row9, end_column=5)
        row9 += 1

        # Note
        ws9.merge_cells(start_row=row9, start_column=1, end_row=row9, end_column=8)
        _s9(ws9, row9, 1, "注：分包工程款全部计入分部分项工程费-外委", font=Font(name="宋体", size=12))
        ws9.cell(row=row9, column=1).alignment = s9_center

    for r in range(3, row9 + 1):
        ws9.row_dimensions[r].height = 27.95

    # =====================================================================
    # Sheet 10: 4.1.19.1研发费用
    # =====================================================================
    ws10 = wb.create_sheet("4.1.19.1研发费用")
    col_w10 = [13, 17.38, 13, 13.25, 13, 13.38, 13.25]
    for i, w in enumerate(col_w10, 1):
        ws10.column_dimensions[get_column_letter(i)].width = w

    s10_hdr = Font(name="宋体", size=12, bold=True)
    s10_data = Font(name="宋体", size=12)
    s10_center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def _s10(ws, r, c, val, font=None, fill=None, align=None):
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = font or s10_data
        cell.alignment = align or s10_center
        cell.border = thin_border
        if fill: cell.fill = fill

    ws10.merge_cells("A1:G1")
    _s10(ws10, 1, 1, "4.1.19.1 研发费用", font=s5_title)
    ws10.row_dimensions[1].height = 20.25
    ws10.row_dimensions[2].height = 18

    h10_map = {1: "序号", 2: "项目", 3: "单位", 4: "基价（元）", 5: "数量", 6: "金额（元）", 7: "备注"}
    for c, v in h10_map.items():
        _s10(ws10, 2, c, v, font=s10_hdr)

    row10 = 3
    for i, r in enumerate(rd_list, 1):
        _s10(ws10, row10, 1, i)
        _s10(ws10, row10, 2, r.item or "", align=Alignment(horizontal="left", vertical="center"))
        _s10(ws10, row10, 3, r.unit or "")
        _s10(ws10, row10, 4, r.base_price)
        _s10(ws10, row10, 5, r.quantity)
        _s10(ws10, row10, 6, r.amount, fill=s2_green)
        _s10(ws10, row10, 7, r.remark or "")
        ws10.row_dimensions[row10].height = 22.9
        row10 += 1

    # Subtotal
    _s10(ws10, row10, 1, "小计", font=s10_data)
    _s10(ws10, row10, 6, round(rd_total, 2), font=Font(name="宋体", size=11, bold=True), fill=s2_green)

    # =====================================================================
    # Sheet 11: 4.1.19.2其他费用
    # =====================================================================
    ws11 = wb.create_sheet("4.1.19.2其他费用")
    col_w11 = [4.88, 8.38, 18.62, 8.5, 11.62, 9.75, 11.38, 13, 24.5]
    for i, w in enumerate(col_w11, 1):
        ws11.column_dimensions[get_column_letter(i)].width = w

    s11_hdr = Font(name="宋体", size=12, bold=True)
    s11_cat = Font(name="宋体", size=14, bold=True)
    s11_data = Font(name="宋体", size=12)
    s11_center = Alignment(horizontal="center", vertical="center", wrap_text=True)

    def _s11(ws, r, c, val, font=None, fill=None):
        cell = ws.cell(row=r, column=c, value=val)
        cell.font = font or s11_data
        cell.alignment = s11_center
        cell.border = thin_border
        if fill: cell.fill = fill

    ws11.merge_cells("A1:I1")
    _s11(ws11, 1, 1, "4.1.19.2其他费用", font=s5_title)
    ws11.row_dimensions[1].height = 28.15
    ws11.row_dimensions[2].height = 22.15

    h11_map = {1: "类别", 2: "序号", 3: "项目", 4: "单位", 5: "基价（元）", 6: "数量", 7: "金额（元）", 8: "备注", 9: "备注"}
    for c, v in h11_map.items():
        _s11(ws11, 2, c, v, font=s11_hdr)

    # Group by cost_group
    other_groups = {}
    for o in other_list:
        other_groups.setdefault(o.cost_group or "其他管理费", []).append(o)

    row11 = 3
    for gname, items in other_groups.items():
        start_r = row11
        for i, o in enumerate(items, 1):
            _s11(ws11, row11, 1, gname, font=s11_cat)
            _s11(ws11, row11, 2, i)
            _s11(ws11, row11, 3, o.item or "")
            _s11(ws11, row11, 4, o.unit or "")
            _s11(ws11, row11, 5, o.base_price)
            _s11(ws11, row11, 6, o.quantity)
            _s11(ws11, row11, 7, o.amount, fill=s2_green)
            _s11(ws11, row11, 8, o.remark or "")
            _s11(ws11, row11, 9, "")
            ws11.row_dimensions[row11].height = 30
            row11 += 1

        # Merge category column
        if row11 > start_r + 1:
            ws11.merge_cells(start_row=start_r, start_column=1, end_row=row11 - 1, end_column=1)

        # Subtotal
        _s11(ws11, row11, 2, "小计", font=s11_data)
        _s11(ws11, row11, 7, round(sum(o.amount for o in items), 2), font=Font(name="宋体", size=11, bold=True), fill=s2_green)
        row11 += 1

    # Grand total
    if other_list:
        ws11.merge_cells(start_row=row11, start_column=1, end_row=row11, end_column=2)
        _s11(ws11, row11, 1, "合计", font=Font(name="宋体", size=11, bold=True))
        _s11(ws11, row11, 7, round(other_total, 2), font=Font(name="宋体", size=11, bold=True), fill=s2_green)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output
