from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path('/Users/kevin/Desktop/cat3cat3.github.io/电脑')
OUTPUT = ROOT / 'output/pdf/成都市双流区酷虎科技培训学校有限公司_联想T460租赁技术服务合同_新增7台.pdf'
FONT = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'

pdfmetrics.registerFont(TTFont('CN', FONT))

PAGE_W, PAGE_H = A4
LEFT = 22 * mm
RIGHT = 22 * mm
TOP = 21 * mm
BOTTOM = 18 * mm
ACCENT = colors.HexColor('#17365D')
LIGHT = colors.HexColor('#EAF0F7')
MUTED = colors.HexColor('#5D6773')


class ContractDoc(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=LEFT,
            rightMargin=RIGHT,
            topMargin=TOP,
            bottomMargin=BOTTOM,
            title='租赁技术服务合同',
            author='成都猫匠极客科技有限公司',
            subject='7台联想ThinkPad T460固定一年租赁技术服务',
        )
        frame = Frame(LEFT, BOTTOM, PAGE_W - LEFT - RIGHT, PAGE_H - TOP - BOTTOM, id='main')
        self.addPageTemplates([PageTemplate(id='contract', frames=frame, onPage=self._header_footer)])

    def _header_footer(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor('#98A3AF'))
        canvas.setLineWidth(0.45)
        canvas.line(LEFT, PAGE_H - 14 * mm, PAGE_W - RIGHT, PAGE_H - 14 * mm)
        canvas.setFont('CN', 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(LEFT, PAGE_H - 11.2 * mm, '租赁技术服务合同')
        canvas.drawRightString(PAGE_W - RIGHT, PAGE_H - 11.2 * mm, '合同编号：________________')
        canvas.line(LEFT, 12 * mm, PAGE_W - RIGHT, 12 * mm)
        canvas.drawCentredString(PAGE_W / 2, 8 * mm, f'第 {doc.page} 页')
        canvas.restoreState()


styles = getSampleStyleSheet()
title = ParagraphStyle('title', fontName='CN', fontSize=22, leading=30, alignment=TA_CENTER, textColor=colors.black, spaceAfter=9 * mm)
subtitle = ParagraphStyle('subtitle', fontName='CN', fontSize=9.5, leading=15, alignment=TA_CENTER, textColor=MUTED, spaceAfter=7 * mm)
h1 = ParagraphStyle('h1', fontName='CN', fontSize=13, leading=20, textColor=ACCENT, spaceBefore=4 * mm, spaceAfter=2.5 * mm)
h2 = ParagraphStyle('h2', fontName='CN', fontSize=10.5, leading=17, textColor=ACCENT, spaceBefore=2 * mm, spaceAfter=1.5 * mm)
body = ParagraphStyle('body', fontName='CN', fontSize=9.7, leading=17.5, alignment=TA_LEFT, textColor=colors.HexColor('#20252B'), spaceAfter=1.7 * mm)
small = ParagraphStyle('small', parent=body, fontSize=8.5, leading=14)
table_head = ParagraphStyle('table_head', parent=small, alignment=TA_CENTER, textColor=colors.white)
center = ParagraphStyle('center', parent=body, alignment=TA_CENTER)
notice = ParagraphStyle('notice', parent=body, fontSize=10, leading=18, textColor=colors.HexColor('#7A1F1F'))
sig = ParagraphStyle('sig', parent=body, fontSize=10, leading=20)


def P(text, style=body):
    return Paragraph(text, style)


def section(name):
    return P(name, h1)


def clause(number, text, style=body):
    return P(f'{number}、{text}', style)


def party_table():
    rows = [
        [P('<b>甲方（承租方）</b>', small), P('成都市双流区酷虎科技培训学校有限公司', small)],
        [P('统一社会信用代码', small), P('91510116MACQB3XL2A', small)],
        [P('联系人 / 电话', small), P('高靖 / 13438285818', small)],
        [P('联系地址', small), P('四川省成都市双流区东升街道万达广场2楼', small)],
        [P('<b>乙方（出租及服务方）</b>', small), P('成都猫匠极客科技有限公司', small)],
        [P('统一社会信用代码', small), P('91510100MAEPK5XC6E', small)],
        [P('联系人 / 电话', small), P('吴文凯 / 18200456012', small)],
        [P('联系地址', small), P('四川省成都市双流区鲢鱼社区11幢2单元 CATmaker', small)],
    ]
    t = Table(rows, colWidths=[38 * mm, 125 * mm], repeatRows=0)
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'CN'),
        ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#B9C3CE')),
        ('BACKGROUND', (0, 0), (0, -1), LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('RIGHTPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def equipment_table():
    headers = ['设备名称', '配置', '数量', '单价\n（元/台/月）', '月合计\n（元/月）', '租期', '单台价值\n（元）', '总价值\n（元）']
    row = [
        '联想 ThinkPad T460',
        'Intel Core i5-6200\n内存 8GB\n固态硬盘 256GB',
        '7台', '50', '350', '固定12个月', '1,500', '10,500',
    ]
    data = [[P(x.replace('\n', '<br/>'), table_head) for x in headers], [P(x.replace('\n', '<br/>'), small) for x in row]]
    widths = [28, 40, 13, 21, 19, 22, 20, 20]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'CN'),
        ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.45, colors.HexColor('#7E8A97')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
    ]))
    return t


story = []
story += [Spacer(1, 7 * mm), P('租赁技术服务合同', title), P('（固定一年期）', subtitle)]
story += [party_table(), Spacer(1, 5 * mm)]
story += [P('甲乙双方在平等、自愿、诚实信用的基础上，就乙方向甲方提供电子设备租赁及配套技术服务事宜，经充分协商达成本合同。双方确认，本合同独立签订；除本合同另有明确约定外，不追溯变更双方此前已经履行完毕的合同。', body)]
story += [section('第一条  租赁设备、费用与价值'), equipment_table(), Spacer(1, 3 * mm)]
story += [
    clause('1', '设备共 <b>7台</b>，实际序列号、外观及配件状态以本合同附件《设备交付验收清单》为准。'),
    clause('2', '租赁技术服务费为每台每月人民币 <b>50元</b>，月合计人民币 <b>350元</b>。'),
    clause('3', '设备单台约定价值为人民币 <b>1,500元</b>，设备总价值为人民币 <b>10,500元（大写：壹万零伍佰元整）</b>。该价值用于设备毁损、灭失且无法修复时的赔偿核算，不表示设备所有权发生转移。'),
    clause('4', '押金：人民币 <b>0元</b>。服务费用构成为50%设备租赁费与50%技术服务费。'),
]
story += [section('第二条  固定租期与付款'),
    clause('1', '租期为固定12个月，自双方签署《设备交付验收清单》所载交付验收之日起计算，起止日期为：____年__月__日至____年__月__日。租期届满后，双方如需继续合作，应另行书面续签；本合同不自动续期。'),
    clause('2', '甲方采用先用后付方式。第1期租赁技术服务费350元于设备交付验收之日起满一个月后支付；此后每届满一个租赁月支付当期350元。付款日以乙方账户实际到账日为准。'),
    clause('3', '乙方收款账户：户名吴文凯；账号6214 8328 1098 3531；开户行招商银行成都龙湖三千支行。乙方根据约定向甲方提供电子发票。'),
]

story += [section('第三条  固定期限及提前退还特别约定')]
special_data = [[P('<b>重要提示：以下条款涉及甲方固定租期、提前退还及剩余租金支付义务，请甲方重点阅读。</b>', notice)], [P('<b>1、双方明确约定本合同为固定12个月租期。除乙方严重违约导致合同目的不能实现、法律另有强制性规定或双方另行书面一致同意外，甲方不得在租期届满前单方退租或解除合同。</b>', notice)], [P('<b>2、甲方在租期届满前提前退还全部或部分设备的，不视为本合同提前解除，也不免除甲方支付剩余租金的义务。甲方应在设备实际退还之日起3个工作日内，一次性补齐该等设备自退还次日起至固定租期届满之日的全部剩余租赁技术服务费。</b>', notice)], [P('<b>3、甲方提前退还设备产生的包装、运输、保险等费用由甲方承担。乙方接收提前退还设备，仅代表保管及验收设备，不代表乙方放弃剩余租金请求权。</b>', notice)]]
special = Table(special_data, colWidths=[163 * mm])
special.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 1.1, colors.HexColor('#9D2A2A')),
    ('INNERGRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#D8A2A2')),
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF5F5')),
    ('LEFTPADDING', (0, 0), (-1, -1), 9),
    ('RIGHTPADDING', (0, 0), (-1, -1), 9),
    ('TOPPADDING', (0, 0), (-1, -1), 8),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
]))
story += [special, Spacer(1, 4 * mm), clause('4', '双方确认：上述固定租期及提前退还条款已经逐条协商，乙方已以加粗、边框和醒目颜色作出提示，并按照甲方要求说明其内容及法律后果；甲方已经充分阅读、理解并接受。')]
story += [section('第四条  交付、验收与风险转移'),
    clause('1', '交付方式为物流、快递或乙方送货上门，具体以双方确认的实际方式为准。交付地点为甲方指定地址。'),
    clause('2', '甲方指定高靖（身份证号码：511324199104181811，手机：13438285818）或甲方另行书面授权人员签收设备。签收人员在《设备交付验收清单》上签字、盖章或通过可核验的电子方式确认，均视为甲方验收。'),
    clause('3', '甲方应在设备交付之日起7日内完成数量、型号、配置、外观及基本功能验收并提出书面异议；逾期未提出书面异议的，视为验收合格。可合理发现但未在验收期提出的外观或数量异议，甲方不得以此延迟付款。'),
    clause('4', '设备交付甲方并经签收后，其保管、使用及非正常损耗风险由甲方承担。设备所有权始终归乙方。'),
    clause('5', '租期届满，甲方应在3个工作日内配合乙方完成设备归还。甲方承担归还运输费用，并应妥善包装。乙方验收完成且甲方结清全部款项后，本合同终止。'),
]
story += [section('第五条  设备使用与保管'),
    clause('1', '甲方仅可将设备用于合法的培训、办公及与其经营范围相关的用途，不得用于任何违法活动。'),
    clause('2', '未经乙方书面同意，甲方不得擅自拆机、改装、添改部件，不得出售、抵押、质押、转租、转借或以其他方式处分设备。'),
    clause('3', '甲方应妥善保管并保持设备清洁。正常合理损耗不计入赔偿；因人为损坏、保管不善、超频、病毒或不当操作造成的维修、配件或其他直接损失由甲方承担。'),
]

story.append(PageBreak())
story += [section('第六条  技术服务与维修'),
    clause('1', '乙方在租期内提供7×9小时（9:00-18:00）技术支持。甲方报障后，乙方优先通过电话、网络或远程方式排查；确需维修或更换的，由乙方通过物流、快递或上门方式处理。'),
    clause('2', '正常使用产生的合理硬件故障，由乙方免费维修或更换。因乙方原因导致单台设备连续5个工作日无法正常使用且未提供同等或更高配置替代设备的，甲方可要求暂停计算该台设备对应期间的费用；持续无法实现合同目的的，双方就受影响设备另行协商处理。'),
    clause('3', '下列情形不属于免费保修范围：不可抗力；战争、骚乱或核事故；火灾、水浸、雷击；人为故意或过失、明显碰撞；被盗、被抢或遗失；软件原因；未经授权的拆机、维修或改装。'),
    clause('4', '特殊情况下甲方要求额外上门服务的，双方应事先确认服务内容以及人工、交通等费用。'),
]
story += [section('第七条  甲方权利与义务'),
    clause('1', '甲方有权在本合同约定范围内使用设备并获得技术支持；应按时足额支付租赁技术服务费及其他应付款项。'),
    clause('2', '甲方应保证其提供的主体、联系人、地址及验收信息真实有效；信息变更应及时书面通知乙方。'),
    clause('3', '甲方应配合乙方进行合理的设备状态检查、维修、更换和回收，并在租期内对设备持续承担保管责任。'),
    clause('4', '设备毁损或灭失时，甲方应立即通知乙方。经双方确认无法修复或无法返还的，甲方应按附件所载设备价值赔偿；已支付租金不冲抵设备赔偿款，但同一损失不得重复计算。'),
]
story += [section('第八条  乙方权利与义务'),
    clause('1', '乙方拥有设备所有权，有权依约收取费用，并在合理时间内检查设备状态。'),
    clause('2', '乙方应按约交付符合约定型号、配置和数量的设备，并在租期内提供约定的技术支持及合理维修服务。'),
    clause('3', '甲方经营状况严重恶化、转移财产逃避债务、丧失商业信誉或出现明显丧失履约能力的情形时，乙方可要求甲方提供合理担保；甲方未在合理期限内提供的，乙方可暂停服务或依法解除合同并收回设备。'),
]
story += [section('第九条  违约责任'),
    clause('1', '甲方逾期付款的，每逾期一日，应按逾期未付金额的0.065%向乙方支付违约金。逾期超过10日，经乙方催告后仍未支付的，乙方有权暂停技术服务、限制设备使用或解除合同并收回设备。'),
    clause('2', '因甲方违约导致合同解除的，甲方仍应结清截至解除日的应付款、违约金和设备损失，并按照第三条约定支付固定租期内尚未到期的剩余租赁技术服务费；乙方应采取合理措施避免损失扩大。'),
    clause('3', '甲方拒不配合回收设备的，除应支付全部应付款外，还应赔偿乙方因此产生的合理催收、运输、诉讼、保全及律师费用。'),
]

story.append(PageBreak())
story += [section('第十条  数据、系统与软件'),
    clause('1', '乙方仅提供设备硬件及约定的技术支持，不当然提供操作系统或商业软件授权。甲方需要使用正版软件的，应自行购买或另行委托乙方代购，费用另计。'),
    clause('2', '甲方应自行备份设备内的数据并在归还前完成必要的退出账号、删除和清理。因设备故障或甲方未备份导致的数据损失，乙方不承担间接损失；因乙方故意或重大过失造成的除外。'),
    clause('3', '甲方应遵守网络安全、数据安全、个人信息保护及知识产权相关法律法规。因甲方存储、处理或传播内容引起的责任由甲方依法承担。'),
]
story += [section('第十一条  合同解除与不可抗力'),
    clause('1', '一方严重违反本合同，经守约方书面催告后在合理期限内仍未改正，致使合同目的不能实现的，守约方可依法解除合同并要求违约方承担责任。'),
    clause('2', '因不可抗力导致全部或部分不能履行的，受影响方应及时通知并在合理期限内提供证明。双方根据影响程度协商部分或全部免除责任，但法律另有规定的除外。'),
    clause('3', '合同解除或终止不影响结算、保密、数据清理、设备返还、违约责任及争议解决条款的效力。'),
]
story += [section('第十二条  通知与争议解决'),
    clause('1', '双方在合同首页列明的地址、电话及双方另行确认的电子联系方式均可用于业务通知。任何一方信息变更应在3个工作日内书面通知对方；未通知导致送达不能的，由未通知方承担相应后果。'),
    clause('2', '本合同适用中华人民共和国法律。因本合同引起或与本合同有关的争议，双方应先友好协商；协商不成的，任一方可向被告住所地、合同签订地、合同履行地或依法有管辖权的人民法院提起诉讼。'),
    clause('3', '双方确认本合同签订地和主要履行地为四川省成都市双流区。'),
]
story += [section('第十三条  生效与其他'),
    clause('1', '本合同及附件构成双方完整约定。未尽事宜由双方签订书面补充协议，补充协议与本合同具有同等法律效力。'),
    clause('2', '本合同自双方盖章或授权代表签字之日起生效，一式两份，甲乙双方各执一份，具有同等法律效力。依法可验证的电子签署文本与纸质签署文本具有同等效力。'),
    clause('3', '本合同正文及签署页共5页，附件《设备交付验收清单》共1页。双方应在签署前核对所有空白处并完成填写；未填写内容以实际履行及双方可核验的书面记录为准。'),
]

story.append(PageBreak())
story += [P('签署页', title), P('（以下无正文，为《租赁技术服务合同》签署页）', center), Spacer(1, 8 * mm)]
sig_table = Table([
    [P('<b>甲方（盖章）</b><br/>成都市双流区酷虎科技培训学校有限公司', sig), P('<b>乙方（盖章）</b><br/>成都猫匠极客科技有限公司', sig)],
    [P('授权代表（签字/手印）：<br/><br/>____________________________', sig), P('授权代表（签字/手印）：<br/><br/>____________________________', sig)],
    [P('签署日期：____年__月__日', sig), P('签署日期：____年__月__日', sig)],
], colWidths=[81.5 * mm, 81.5 * mm], rowHeights=[30 * mm, 36 * mm, 22 * mm])
sig_table.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#8995A2')),
    ('INNERGRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#C2CAD2')),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ('TOPPADDING', (0, 0), (-1, -1), 9),
]))
story += [sig_table, Spacer(1, 8 * mm)]
ack = Table([[P('<b>甲方对固定租期及提前退还条款的单独确认</b><br/><br/>甲方确认已重点阅读并充分理解本合同第三条。甲方明确知悉：租期固定为12个月，不得无正当理由提前退租；即使提前退还设备，也应在约定期限内一次性补齐剩余全部租赁技术服务费。<br/><br/>甲方盖章或授权代表签字/手印：________________________　日期：____年__月__日', notice)]], colWidths=[163 * mm])
ack.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 1.2, colors.HexColor('#9D2A2A')),
    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF5F5')),
    ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ('TOPPADDING', (0, 0), (-1, -1), 10),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
]))
story.append(ack)

story.append(PageBreak())
story += [P('附件：设备交付验收清单', title), P('本清单为《租赁技术服务合同》不可分割的组成部分。', center)]
inv_headers = [P(x, table_head) for x in ['序号', '设备名称', '主要配置', '设备序列号', '外观/配件状态', '验收结果']]
inv_rows = [inv_headers]
for i in range(1, 8):
    inv_rows.append([P(str(i), center), P('联想 ThinkPad T460', small), P('Intel Core i5-6200<br/>8GB / 256GB SSD', small), P('________________', small), P('________________', small), P('□合格<br/>□异议', small)])
inv = Table(inv_rows, colWidths=[10 * mm, 30 * mm, 37 * mm, 31 * mm, 32 * mm, 23 * mm], rowHeights=[12 * mm] + [18 * mm] * 7, repeatRows=1)
inv.setStyle(TableStyle([
    ('FONTNAME', (0, 0), (-1, -1), 'CN'),
    ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('GRID', (0, 0), (-1, -1), 0.45, colors.HexColor('#7E8A97')),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('LEFTPADDING', (0, 0), (-1, -1), 3),
    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
]))
story += [inv]
story += [P('交付日期：____年__月__日　　租期：____年__月__日至____年__月__日（固定12个月）', body), P('交付地点：____________________________________________________________', body), P('配件及备注：__________________________________________________________<br/>____________________________________________________________________', body), Spacer(1, 5 * mm)]
accept = Table([
    [P('<b>甲方验收确认</b><br/>经核对，除上述已注明异议外，甲方确认设备数量、型号、配置、外观和配件状态符合约定，并同意自本清单所载交付日期起计算固定12个月租期。<br/>签收人：________________<br/>甲方盖章：______________<br/>日期：____年__月__日', small),
     P('<b>乙方交付确认</b><br/>乙方确认已按照本清单向甲方交付7台设备，并已向甲方说明基本使用、保管、报修及归还要求。<br/><br/>交付人：________________<br/>乙方盖章：______________<br/>日期：____年__月__日', small)]
], colWidths=[81.5 * mm, 81.5 * mm], rowHeights=[50 * mm])
accept.setStyle(TableStyle([
    ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#8995A2')),
    ('INNERGRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#C2CAD2')),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LEFTPADDING', (0, 0), (-1, -1), 9),
    ('RIGHTPADDING', (0, 0), (-1, -1), 9),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
]))
story.append(accept)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
doc = ContractDoc(str(OUTPUT))
doc.build(story)
print(OUTPUT)
