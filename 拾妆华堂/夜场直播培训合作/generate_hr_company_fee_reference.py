from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUT_FILE = "成都个人化妆培训费用市场对比说明（给人力公司版）.docx"
FONT = "Microsoft YaHei"


def set_run_font(run, size=10, bold=False, color="000000"):
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
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal._element.rPr.rFonts.set(qn("w:ascii"), FONT)
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    normal.font.size = Pt(10)

    for style_name, size in [("Heading 1", 13.5), ("Heading 2", 11.5)]:
        style = doc.styles[style_name]
        style.font.name = FONT
        style._element.rPr.rFonts.set(qn("w:ascii"), FONT)
        style._element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
        style._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string("000000")
        style.paragraph_format.space_before = Pt(11)
        style.paragraph_format.space_after = Pt(4)


def add_text(doc, text, size=10, bold=False, color="000000", after=6, align=None):
    p = doc.add_paragraph()
    set_para(p, after=after, align=align)
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, color=color)
    return p


def add_heading(doc, text):
    p = doc.add_paragraph(style="Heading 1")
    set_para(p, before=11, after=4)
    run = p.add_run(text)
    set_run_font(run, size=13.5, bold=True)


def fill_table(table, rows, header=True):
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            cell = table.cell(i, j)
            cell.text = ""
            is_header = header and i == 0
            is_key = str(row[0]) in ("本合作课程折算", "建议结论")
            shade_cell(cell, "E8EEF5" if is_header else ("F2F4F7" if is_key else "FFFFFF"))
            p = cell.paragraphs[0]
            align = WD_ALIGN_PARAGRAPH.CENTER if j in (1, 2, 3) else WD_ALIGN_PARAGRAPH.LEFT
            set_para(p, before=0, after=0, line=1.05, align=align)
            run = p.add_run(str(value))
            set_run_font(run, size=9.3, bold=is_header or is_key)


def build_doc():
    doc = Document()
    style_doc(doc)

    add_text(doc, "成都个人化妆培训费用市场对比说明", size=22, align=WD_ALIGN_PARAGRAPH.CENTER, after=3)
    add_text(doc, "供人力资源合作方评估招生定价、培训价值与合作报价合理性使用", size=10, color="555555", align=WD_ALIGN_PARAGRAPH.CENTER, after=9)

    add_text(doc, "说明：本文件用于协助合作方判断“个人自行报名化妆培训”与“定向岗位培训合作课”的价格差异。以下区间综合公开招生信息、行业常见报价口径及成都本地化妆培训课程类型整理，实际价格会因品牌、师资、课程周期、是否含耗材工具、是否含考证或就业推荐而变化。", size=9.5, color="555555", after=8)

    add_heading(doc, "一、个人报名常见课程费用区间")
    market_table = doc.add_table(rows=8, cols=5)
    set_table_geometry(market_table, [1.3, 1.15, 1.05, 1.25, 2.75])
    fill_table(market_table, [
        ("课程类型", "常见周期", "常见费用", "适合人群", "说明"),
        ("个人形象妆/生活妆", "1-5天", "499-1,980元", "兴趣学习", "偏日常妆容，不以就业为主要目标。"),
        ("零基础基础妆班", "5-15天", "1,980-4,980元", "零基础入门", "学习工具、底妆、眉眼唇、基础全妆。"),
        ("新娘跟妆基础班", "15-30天", "3,980-8,800元", "兼职接单", "偏婚礼跟妆、伴娘妆、妈妈妆等。"),
        ("影楼/职业彩妆班", "1-3个月", "6,800-12,800元", "职业转型", "课程更系统，通常包含多风格妆容。"),
        ("美业综合班", "3-6个月", "9,800-19,800元", "长期从业", "常见组合为化妆、美甲、美睫、纹绣等。"),
        ("直播上镜妆专项", "3-15天", "1,980-6,800元", "主播/运营", "偏镜头、灯光、上镜效果和快速出妆。"),
        ("夜场/浓妆专项", "7-15天", "3,000-8,000元", "专项就业", "公开标准课较少，多见于私教或工作室专项训练。"),
    ])

    add_heading(doc, "二、个人完整就业学习成本估算")
    cost_table = doc.add_table(rows=5, cols=4)
    set_table_geometry(cost_table, [1.6, 1.35, 1.35, 3.1])
    fill_table(cost_table, [
        ("学习路径", "课程组合", "预计费用", "判断"),
        ("基础入门路径", "基础妆", "1,980-4,980元", "只能完成入门，不足以支撑直播/夜场专项就业。"),
        ("兼职接单路径", "基础妆 + 新娘/影楼", "5,980-12,800元", "可覆盖部分接单场景，但与直播、夜场岗位不完全匹配。"),
        ("专项就业路径", "基础妆 + 直播妆 + 夜场妆", "8,000-18,000元", "更接近本合作项目的就业方向。"),
        ("综合长期路径", "全科/综合美业", "12,000-30,000元以上", "周期长、学习面广，但不一定针对合作方岗位。"),
    ])

    add_heading(doc, "三、本合作课程折算对比")
    compare_table = doc.add_table(rows=5, cols=5)
    set_table_geometry(compare_table, [1.35, 1.1, 1.4, 1.5, 2.45])
    fill_table(compare_table, [
        ("班型", "周期", "合作总价", "单人折算", "说明"),
        ("标准班", "45天", "80,000元/期", "约8,000-10,000元/人", "按8-10人计算，适合首次合作开班。"),
        ("进阶班", "45天", "88,000元/期", "约6,769-8,000元/人", "按11-13人计算，单人成本下降。"),
        ("满班", "45天", "96,000元/期", "约6,400-6,857元/人", "按14-15人计算，接近市场专项就业路径的中低位价格。"),
        ("本合作课程折算", "45天", "80,000元起/期", "约6,400-10,000元/人", "处在个人报名基础妆+直播妆+夜场妆专项的常见价格区间内。"),
    ])

    add_heading(doc, "四、给合作方的判断口径")
    judge_table = doc.add_table(rows=5, cols=2)
    set_table_geometry(judge_table, [1.55, 5.65])
    fill_table(judge_table, [
        ("判断点", "参考结论"),
        ("价格合理性", "本合作课按单人折算后，处在成都个人专项就业化妆培训的常见价格区间内。"),
        ("岗位匹配度", "普通化妆学校多以生活妆、新娘妆、影楼妆为主；本课程直接围绕直播妆、夜场妆，和合作方岗位更贴近。"),
        ("合作优势", "合作方统一招生、统一管理、统一就业对接，我方统一教学交付，有助于降低学员自行找课、找机构、找就业渠道的不确定性。"),
        ("建议结论", "建议合作方将本课程包装为“定向就业技能培训”，而不是普通兴趣化妆班。"),
    ])

    add_heading(doc, "五、对外招生沟通建议")
    add_text(doc, "对学员沟通时，建议强调“45天专项就业方向训练”“基础妆+直播妆+夜场妆三阶段”“岗位资源由合作方负责对接”。不建议承诺包就业，也不建议将培训费与材料耗材混为一项。")

    add_heading(doc, "六、资料口径说明")
    source_table = doc.add_table(rows=5, cols=2)
    set_table_geometry(source_table, [1.65, 5.55])
    fill_table(source_table, [
        ("资料类型", "参考内容"),
        ("品牌学校价格", "成都东田造型官网公开展示的长期课程价格约22,980-27,980元，周期4-6个月。"),
        ("行业价格区间", "毛戈平形象设计艺术学校相关文章提到，化妆学习费用会因课程、师资、课时不同，从几千到几万元不等。"),
        ("线上课程区间", "公开行业文章显示，线上化妆培训常见为几百元到几千元不等，通常与线下就业型课程不可直接等同。"),
        ("文件用途", "本文件为合作报价解释和招生定价辅助，不作为任何具体机构的官方报价。"),
    ])

    add_text(doc, "本参考说明供合作洽谈、招生定价与课程价值说明使用，具体合作金额与交付责任以双方正式合作协议为准。", bold=True, after=0)
    return doc


if __name__ == "__main__":
    document = build_doc()
    document.save(OUT_FILE)
    print(OUT_FILE)
