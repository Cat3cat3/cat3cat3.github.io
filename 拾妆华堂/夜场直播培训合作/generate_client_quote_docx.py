from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUT_FILE = "夜场直播化妆培训合作报价函（客户版）.docx"
FONT = "Microsoft YaHei"


def set_run_font(run, size=10.5, bold=False, color="000000"):
    run.font.name = FONT
    run._element.rPr.rFonts.set(qn("w:ascii"), FONT)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
    run._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    run.font.size = Pt(size)
    run.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)


def set_para(paragraph, before=0, after=6, line=1.15, align=None):
    paragraph.paragraph_format.space_before = Pt(before)
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = line
    if align is not None:
        paragraph.alignment = align


def shade_cell(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_width(cell, width_inch):
    cell.width = Inches(width_inch)
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.first_child_found_in("w:tcW")
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(int(width_inch * 1440)))
    tc_w.set(qn("w:type"), "dxa")


def set_table_geometry(table, widths):
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    tbl_w = tbl_pr.first_child_found_in("w:tblW")
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(int(sum(widths) * 1440)))
    tbl_w.set(qn("w:type"), "dxa")

    tbl_grid = table._tbl.tblGrid
    for child in list(tbl_grid):
        tbl_grid.remove(child)
    for width in widths:
        grid_col = OxmlElement("w:gridCol")
        grid_col.set(qn("w:w"), str(int(width * 1440)))
        tbl_grid.append(grid_col)

    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            set_cell_width(cell, widths[idx])
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_mar = tc_pr.first_child_found_in("w:tcMar")
            if tc_mar is None:
                tc_mar = OxmlElement("w:tcMar")
                tc_pr.append(tc_mar)
            for side in ("top", "bottom", "start", "end"):
                side_el = tc_mar.find(qn(f"w:{side}"))
                if side_el is None:
                    side_el = OxmlElement(f"w:{side}")
                    tc_mar.append(side_el)
                side_el.set(qn("w:w"), "90" if side in ("top", "bottom") else "120")
                side_el.set(qn("w:type"), "dxa")


def style_doc(doc):
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.85)
    section.bottom_margin = Inches(0.85)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal._element.rPr.rFonts.set(qn("w:ascii"), FONT)
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    normal.font.size = Pt(10.5)

    for style_name, size in [("Heading 1", 14), ("Heading 2", 12)]:
        style = doc.styles[style_name]
        style.font.name = FONT
        style._element.rPr.rFonts.set(qn("w:ascii"), FONT)
        style._element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
        style._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string("000000")
        style.paragraph_format.space_before = Pt(12)
        style.paragraph_format.space_after = Pt(5)
        style.paragraph_format.line_spacing = 1.12


def add_text(doc, text, size=10.5, bold=False, color="000000", after=6, align=None):
    p = doc.add_paragraph()
    set_para(p, after=after, align=align)
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, color=color)
    return p


def add_heading(doc, text):
    p = doc.add_paragraph(style="Heading 1")
    set_para(p, before=12, after=5)
    run = p.add_run(text)
    set_run_font(run, size=14, bold=True)


def fill_table(table, rows, header=True):
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            cell = table.cell(i, j)
            cell.text = ""
            shade_cell(cell, "E8EEF5" if header and i == 0 else ("F2F4F7" if str(row[0]) in ("合计", "整期合计") else "FFFFFF"))
            p = cell.paragraphs[0]
            align = WD_ALIGN_PARAGRAPH.CENTER if j != len(row) - 1 else WD_ALIGN_PARAGRAPH.LEFT
            if len(row) <= 3:
                align = WD_ALIGN_PARAGRAPH.LEFT if j == len(row) - 1 else WD_ALIGN_PARAGRAPH.CENTER
            set_para(p, before=0, after=0, line=1.05, align=align)
            run = p.add_run(str(value))
            set_run_font(run, size=10, bold=(header and i == 0) or str(row[0]) in ("合计", "整期合计"))


def build_doc():
    doc = Document()
    style_doc(doc)

    add_text(doc, "夜场妆 + 直播妆化妆培训合作报价函", size=23, align=WD_ALIGN_PARAGRAPH.CENTER, after=3)
    add_text(doc, "对外合作报价文件 | 仅含教学服务 | 供合作洽谈与签约确认使用", size=10.5, color="555555", align=WD_ALIGN_PARAGRAPH.CENTER, after=10)

    table = doc.add_table(rows=5, cols=2)
    set_table_geometry(table, [1.35, 5.45])
    fill_table(table, [
        ("合作模式", "合作方负责招生、收款、学员管理及就业岗位对接；我方负责课程教学交付与教学质量把控。"),
        ("课程周期", "45天系统培训，按天计费；1天包含上午授课与下午实操辅导。"),
        ("课程顺序", "基础妆模块15天 -> 直播妆模块15天 -> 夜场妆模块15天。"),
        ("班型人数", "最低8人开班，最高15人满班。"),
        ("付款方式", "开班前支付合作执行价的95%，结业验收后支付5%尾款。"),
    ], header=False)

    add_heading(doc, "一、合作定位")
    add_text(doc, "本项目面向合作方的人力资源招生体系，课程目标是让学员完成从基础化妆能力到直播妆、夜场妆专项能力的系统训练。我方提供教学服务、实操辅导、课堂纠错、阶段点评及结业支持，不对就业结果作承诺。")

    add_heading(doc, "二、价格口径")
    price_table = doc.add_table(rows=4, cols=3)
    set_table_geometry(price_table, [1.25, 1.75, 3.8])
    fill_table(price_table, [
        ("价格类型", "金额", "说明"),
        ("标准价", "108,000元 / 期", "我方45天完整课程的对外基准报价。"),
        ("合作执行价", "90,000元起 / 期", "针对本次合作项目给予的执行价格，按实际班型人数确认。"),
        ("最终签约价", "以合同为准", "结合招生规模、排期安排及合作深度最终确认。"),
    ])

    add_heading(doc, "三、课程模块报价")
    module_table = doc.add_table(rows=5, cols=5)
    set_table_geometry(module_table, [1.35, 0.75, 1.35, 1.35, 2.0])
    fill_table(module_table, [
        ("模块", "天数", "标准价", "合作执行价", "交付重点"),
        ("基础妆模块", "15天", "36,000元", "30,000元", "工具认知、底妆、眼妆、修容、全妆基础能力。"),
        ("直播妆模块", "15天", "36,000元", "30,000元", "镜头适配、灯光适配、上镜妆容与速度训练。"),
        ("夜场妆模块", "15天", "36,000元", "30,000元", "高持妆、强立体、暗光适配与夜场风格训练。"),
        ("整期合计", "45天", "108,000元", "90,000元", "完整一期教学服务。"),
    ])

    add_heading(doc, "四、班型梯度合作价")
    tier_table = doc.add_table(rows=4, cols=4)
    set_table_geometry(tier_table, [1.3, 1.0, 1.55, 2.95])
    fill_table(tier_table, [
        ("班型", "人数", "合作执行价", "说明"),
        ("标准班", "8-10人", "90,000元 / 期", "适合首次合作开班，教学密度较高。"),
        ("进阶班", "11-13人", "102,000元 / 期", "适合稳定招生后的规模化开班。"),
        ("满班", "14-15人", "114,000元 / 期", "满班执行价，需提前确认排期与教学安排。"),
    ])

    add_heading(doc, "五、费用包含与不包含")
    terms_table = doc.add_table(rows=4, cols=2)
    set_table_geometry(terms_table, [1.45, 5.35])
    fill_table(terms_table, [
        ("费用包含", "课程设计、现场授课、实操辅导、当天纠错、阶段点评、结业点评及群内答疑支持。"),
        ("费用不含", "材料费、耗材费、学员个人工具包、场地费、老师交通费不包含在本报价内。"),
        ("材料说明", "我方可提供采购清单及购买渠道建议，实际采购与费用承担由合作方或学员自行确认。"),
        ("后续支持", "结业后如需进阶提升、补课或复训，可按合作内部优惠价另行安排。"),
    ], header=False)

    add_heading(doc, "六、合作边界")
    add_text(doc, "合作方负责招生宣传、学员收费、学员日常管理、场地安排及就业岗位对接；我方负责教学交付与教学质量。双方可在正式合同中进一步明确开班人数、排期、验收方式、付款节点及违约责任。")

    add_text(doc, "本报价函为合作洽谈及签约确认使用，具体执行以双方最终签署的合作协议为准。", bold=True, after=0)
    return doc


if __name__ == "__main__":
    document = build_doc()
    document.save(OUT_FILE)
    print(OUT_FILE)
