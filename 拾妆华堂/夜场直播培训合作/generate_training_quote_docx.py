from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Inches, RGBColor


OUT_FILE = "夜场直播化妆培训合作报价建议稿.docx"


def set_run_font(run, font_name="Microsoft YaHei", size=None, bold=None, color=None):
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn("w:ascii"), font_name)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), font_name)
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = RGBColor.from_string(color)


def set_paragraph_format(paragraph, before=0, after=6, line=1.15, align=None):
    pf = paragraph.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if align is not None:
        paragraph.alignment = align


def shade_cell(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def set_cell_width(cell, width_inch):
    cell.width = Inches(width_inch)
    tcPr = cell._tc.get_or_add_tcPr()
    tcW = tcPr.first_child_found_in("w:tcW")
    if tcW is None:
        tcW = OxmlElement("w:tcW")
        tcPr.append(tcW)
    tcW.set(qn("w:w"), str(int(width_inch * 1440)))
    tcW.set(qn("w:type"), "dxa")


def set_table_geometry(table, widths_inch):
    table.autofit = False
    tblPr = table._tbl.tblPr
    tblW = tblPr.first_child_found_in("w:tblW")
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.append(tblW)
    tblW.set(qn("w:w"), str(int(sum(widths_inch) * 1440)))
    tblW.set(qn("w:type"), "dxa")

    tblInd = tblPr.first_child_found_in("w:tblInd")
    if tblInd is None:
        tblInd = OxmlElement("w:tblInd")
        tblPr.append(tblInd)
    tblInd.set(qn("w:w"), "0")
    tblInd.set(qn("w:type"), "dxa")

    tblGrid = table._tbl.tblGrid
    for child in list(tblGrid):
        tblGrid.remove(child)
    for width in widths_inch:
        gc = OxmlElement("w:gridCol")
        gc.set(qn("w:w"), str(int(width * 1440)))
        tblGrid.append(gc)

    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            set_cell_width(cell, widths_inch[idx])
            tcPr = cell._tc.get_or_add_tcPr()
            mar = tcPr.first_child_found_in("w:tcMar")
            if mar is None:
                mar = OxmlElement("w:tcMar")
                tcPr.append(mar)
            for side in ("top", "bottom", "start", "end"):
                side_el = mar.find(qn(f"w:{side}"))
                if side_el is None:
                    side_el = OxmlElement(f"w:{side}")
                    mar.append(side_el)
                side_el.set(qn("w:w"), "80" if side in ("top", "bottom") else "120")
                side_el.set(qn("w:type"), "dxa")


def style_doc(doc):
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    normal = doc.styles["Normal"]
    normal.font.name = "Microsoft YaHei"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Microsoft YaHei")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Microsoft YaHei")
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    normal.font.size = Pt(11)

    for name, size, bold, color, before, after in [
        ("Heading 1", 14, True, "000000", 16, 6),
        ("Heading 2", 12, True, "000000", 12, 4),
    ]:
        style = doc.styles[name]
        style.font.name = "Microsoft YaHei"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Microsoft YaHei")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Microsoft YaHei")
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
        style.font.size = Pt(size)
        style.font.bold = bold
        style.font.color.rgb = RGBColor.from_string(color)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.line_spacing = 1.15


def add_title_block(doc):
    p = doc.add_paragraph()
    set_paragraph_format(p, before=0, after=3, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p.add_run("夜场妆 + 直播妆化妆培训合作报价建议稿")
    set_run_font(r, size=24, bold=False, color="000000")

    p = doc.add_paragraph()
    set_paragraph_format(p, before=0, after=10, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r = p.add_run("对外合作基准报价 | 供洽谈锁单使用 | 仅含教学服务")
    set_run_font(r, size=10.5, color="555555")


def add_para(doc, text, size=10.5, color="000000", bold=False, after=6, align=None):
    p = doc.add_paragraph()
    set_paragraph_format(p, before=0, after=after, line=1.15, align=align)
    r = p.add_run(text)
    set_run_font(r, size=size, bold=bold, color=color)
    return p


def add_heading(doc, text):
    p = doc.add_paragraph(style="Heading 1")
    set_paragraph_format(p, before=16, after=6, line=1.1)
    r = p.add_run(text)
    set_run_font(r, size=14, bold=True, color="000000")
    return p


def add_intro_table(doc):
    table = doc.add_table(rows=5, cols=2)
    set_table_geometry(table, [1.3, 5.2])
    rows = [
        ("合作模式", "由合作方负责招生、收款、学员管理及就业岗位对接，我方仅提供课程教学服务。"),
        ("课程周期", "45天系统培训，按天计费；1天包含上午授课与下午辅导。"),
        ("班型人数", "最低8人，最高15人。"),
        ("报价结构", "采用标准价、合作价、底价三层结构，便于统一对外口径与内部审批。"),
        ("付款方式", "开班前支付95%服务费，结业后支付尾款5%。"),
    ]
    for i, (label, value) in enumerate(rows):
        c0 = table.cell(i, 0)
        c1 = table.cell(i, 1)
        c0.text = ""
        c1.text = ""
        shade_cell(c0, "F2F4F7")
        shade_cell(c1, "FFFFFF")
        p0 = c0.paragraphs[0]
        set_paragraph_format(p0, before=0, after=0, line=1.05)
        r0 = p0.add_run(label)
        set_run_font(r0, size=10.5, bold=True)
        p1 = c1.paragraphs[0]
        set_paragraph_format(p1, before=0, after=0, line=1.05)
        r1 = p1.add_run(value)
        set_run_font(r1, size=10.5)


def add_module_pricing_table(doc):
    table = doc.add_table(rows=5, cols=5)
    set_table_geometry(table, [1.35, 0.9, 1.25, 1.35, 1.75])
    headers = ["模块", "天数", "标准价", "合作价", "说明"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = ""
        shade_cell(cell, "E8EEF5")
        p = cell.paragraphs[0]
        set_paragraph_format(p, before=0, after=0, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
        r = p.add_run(h)
        set_run_font(r, size=10.5, bold=True)

    rows = [
        ("基础妆模块", "15天", "36,000元", "30,000元", "首阶段打底与基础手法建立"),
        ("直播妆模块", "15天", "36,000元", "30,000元", "镜头适配与上镜妆容训练"),
        ("夜场妆模块", "15天", "36,000元", "30,000元", "高持妆、强立体、暗光适配"),
        ("总计", "45天", "108,000元 / 期", "90,000元 / 期", "整期合作执行基准"),
    ]
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.text = ""
            shade_cell(cell, "FFFFFF" if i < 4 else "F2F4F7")
            p = cell.paragraphs[0]
            set_paragraph_format(p, before=0, after=0, line=1.05, align=WD_ALIGN_PARAGRAPH.CENTER if j not in (0, 4) else WD_ALIGN_PARAGRAPH.LEFT)
            r = p.add_run(val)
            set_run_font(r, size=10.5, bold=(i == 4))


def add_tier_table(doc):
    table = doc.add_table(rows=4, cols=5)
    set_table_geometry(table, [1.25, 1.0, 1.25, 1.25, 1.75])
    headers = ["班型", "人数", "标准价", "合作价", "说明"]
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = ""
        shade_cell(cell, "E8EEF5")
        p = cell.paragraphs[0]
        set_paragraph_format(p, before=0, after=0, line=1.0, align=WD_ALIGN_PARAGRAPH.CENTER)
        r = p.add_run(h)
        set_run_font(r, size=10.5, bold=True)

    rows = [
        ("标准班", "8-10人", "108,000元 / 期", "90,000元 / 期", "适合作为首次合作执行价。"),
        ("进阶班", "11-13人", "108,000元 / 期", "90,000元 / 期", "人数提升后，单人成本下降，适合规模化招生。"),
        ("满班", "14-15人", "108,000元 / 期", "90,000元 / 期", "满班执行价格，建议作为报价上限。"),
    ]
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.text = ""
            shade_cell(cell, "FFFFFF")
            p = cell.paragraphs[0]
            set_paragraph_format(p, before=0, after=0, line=1.05, align=WD_ALIGN_PARAGRAPH.CENTER if j not in (4,) else WD_ALIGN_PARAGRAPH.LEFT)
            r = p.add_run(val)
            set_run_font(r, size=10.5)


def add_terms_table(doc):
    table = doc.add_table(rows=5, cols=2)
    set_table_geometry(table, [1.5, 5.0])
    rows = [
        ("不含费用", "材料费、耗材费、个人工具包、场地费、老师交通费均不包含在报价内。"),
        ("服务内容", "提供课程设计、现场授课、实操辅导、当天纠错、结业点评及群内答疑支持。"),
        ("复训支持", "结业后如需进阶提升、补课或内部加训，可按合作内部价另行安排。"),
        ("底价说明", "底价为内部执行底线，不作为对外公开报价；实际签约以合作价为准。"),
        ("合作说明", "本报价为我方对外合作基准价，实际执行价格可根据招生规模、排期与合作深度再行协商。"),
    ]
    for i, (label, value) in enumerate(rows):
        c0 = table.cell(i, 0)
        c1 = table.cell(i, 1)
        c0.text = ""
        c1.text = ""
        shade_cell(c0, "F2F4F7")
        shade_cell(c1, "FFFFFF")
        p0 = c0.paragraphs[0]
        set_paragraph_format(p0, before=0, after=0, line=1.05)
        r0 = p0.add_run(label)
        set_run_font(r0, size=10.5, bold=True)
        p1 = c1.paragraphs[0]
        set_paragraph_format(p1, before=0, after=0, line=1.05)
        r1 = p1.add_run(value)
        set_run_font(r1, size=10.5)


def build_doc():
    doc = Document()
    style_doc(doc)

    add_title_block(doc)
    add_intro_table(doc)

    add_heading(doc, "一、合作定位")
    add_para(
        doc,
        "本项目面向合作方的人力资源招生体系，聚焦基础妆、直播妆与夜场妆三大实际交付模块。我方仅承担教学交付与质量把控，不承诺就业结果；合作方负责招生、收款、学员管理及岗位对接。本方案为我方对外合作基准报价，适用于稳定排期的整期合作执行。",
    )

    add_heading(doc, "二、报价方式")
    add_para(doc, "本次报价采用两种口径，便于合作方根据招生节奏与班型规模灵活选择；原则上以整期合作为优先，模块拆分可作为补充方案。", after=4)
    add_para(doc, "1. 按天计费：以45天完整课程为一个交付周期，1天包含上午授课与下午辅导。", after=4)
    add_para(doc, "2. 按班型计费：以8-15人的班型梯度确定总报价，适用于合作招生后的统一结算。", after=8)

    add_heading(doc, "三、按天计费报价")
    add_para(doc, "以下为45天整期课程的建议报价结构，适用于标准交付节奏。标准价用于对外锚定价值，合作价用于本次执行签约，底价仅作内部审批控制。", after=4)
    add_module_pricing_table(doc)

    add_heading(doc, "四、班型梯度报价")
    add_para(doc, "以下为按学员人数形成的班型报价，适合合作方按招生规模选择执行。", after=4)
    add_tier_table(doc)

    add_heading(doc, "五、付款与结算")
    add_para(doc, "建议采用“开班前结清95%，结业后支付5%尾款”的方式，以便双方对课程交付与教学质量形成一致约束。", after=4)
    add_para(doc, "如后续涉及拆分模块、增开进阶班或复训班，可在本报价基础上另行确认内部合作价。", after=8)

    add_heading(doc, "六、合作边界与补充说明")
    add_terms_table(doc)

    add_para(doc, "本报价建议稿可直接用于合作洽谈；如需，我方可继续补充甲乙双方信息、签章页与正式合作协议条款。", after=0)
    return doc


if __name__ == "__main__":
    doc = build_doc()
    doc.save(OUT_FILE)
    print(OUT_FILE)
