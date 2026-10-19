"""Four-page reading copy of verified independent-search evidence."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,PageBreak,Spacer

ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'docs/current-project/contest-baselines-v5'

def main():
    data=json.loads((ROOT/'evidence/contest-baselines-v5/report_content.json').read_text(encoding='utf-8'))
    font='STSong-Light';pdfmetrics.registerFont(UnicodeCIDFont(font));ink=colors.HexColor('#173144');accent=colors.HexColor('#146f79')
    styles={name:ParagraphStyle(name,fontName=font,fontSize=size,leading=leading,textColor=color,spaceAfter=after,wordWrap='CJK')
        for name,size,leading,color,after in [('title',21,29,ink,12),('h1',17,24,ink,11),('h2',12,18,accent,9),
            ('body',9.5,15,ink,9),('small',8.5,13,colors.HexColor('#526477'),8),('cell',8,12,ink,0),('head',8,12,colors.white,0)]}
    story=[]
    def para(text,style='body'):return Paragraph(escape(str(text)),styles[style])
    def add(text,style='body'):story.append(para(text,style))
    def table(headers,rows,widths):
        t=Table([[para(x,'head') for x in headers]]+[[para(x,'cell') for x in row] for row in rows],colWidths=[w*mm for w in widths],repeatRows=1)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),accent),('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#eef4f7'),colors.white])]))
        story.append(t);story.append(Spacer(1,12))
    add(data['title'],'title');add('Q2 / Q3 | 最短时间 / 最低能耗 | EXP-C06','small')
    add('每种方法独立从头搜索最多600秒。没有公共可行初解，没有导入历史方案或外部暖启动；未找到完整合规解时，保留失败事实。')
    table(data['headers'],data['rows'],[38,32.5,32.5,32.5,32.5])
    add('表内时间为方案最后返航时间，单位秒；能耗单位kWh。Q3的贪心、ACO、ALNS包含CP排程支持。“预算内未找到”不代表已证明问题无解。论文历史预算和候选空间与基线不同。','small')
    add(data['timing'],'small');add('共同硬约束','h2')
    for rule in data['rules'][1:3]:add(rule,'small')
    labels={'greedy':'Greedy / EDF','aco':'ACO','alns':'ALNS','cp_sat':'CP-SAT'}
    for q in ['Q2','Q3']:
        story.append(PageBreak());add(q+' 独立搜索明细','h1')
        for objective in ['time','energy']:
            add('最短时间' if objective=='time' else '最低能耗','h2');rows=[]
            for method in ['greedy','aco','alns','cp_sat']:
                r=next(r for r in data['details'] if (r['question'],r['objective'],r['method'])==(q,objective,method));v=r['metrics']
                rows.append([labels[method],f"{v['completion_s']:.3f}" if v else '未找到',f"{v['energy_kwh']:.6f}" if v else '未找到',
                    f"{v['transport_sorties']} + {v['relay_sorties']}" if v else '/',
                    f"{r['first_feasible_s']:.3f}" if r['first_feasible_s'] is not None else '/',f"{r['search_wall_s']:.3f}"])
            table(['方法','返航 / s','能耗 / kWh','运输 + 中继','首解耗时 / s','搜索耗时 / s'],rows,[33,28,29,25,26,27])
        add('核验与状态','h2')
        add('有数值的方案均通过独立运输物理、机队/电池、整站零延期和31箱硬截止核验；Q3另通过连续通信及中继资源核验。没有求得完整解的配置不填入公共方案。')
        for r in data['solver_records']:
            if r['question']==q:
                add(r['objective']+' / CP-SAT: '+', '.join(str(e['stage'])+'='+str(e['status']) for e in r['evidence'])+'；最优性仅对应有限候选模型。','small')
    story.append(PageBreak());add('方法、计时与适用范围','h1')
    for i in [0,3,4,5,6]:add(data['rules'][i],'small')
    add('结论边界','h2')
    for rule in data['limitations']:add(rule,'small')
    add('复现与原始证据','h2');add('入口：scripts/contest_baselines/matrix_v5.py。冻结源码、输入哈希、16份运行记录、检查点方案和独立核验保存在 evidence/contest-baselines-v5/independent_600s_seed42/。CSV保留完整精度和未得解状态。','small')
    pdf=DEST/'援航四组无初解十分钟对比报告.pdf'
    def footer(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#d1dee6'));canvas.line(21*mm,17*mm,189*mm,17*mm)
        canvas.setFont(font,8);canvas.setFillColor(colors.HexColor('#526477'));canvas.drawString(21*mm,12*mm,'援航 | EXP-C06 | 各方法独立搜索，无公共初解');canvas.drawRightString(189*mm,12*mm,str(doc.page));canvas.restoreState()
    SimpleDocTemplate(str(pdf),pagesize=A4,leftMargin=21*mm,rightMargin=21*mm,topMargin=20*mm,bottomMargin=23*mm,
        title=data['title'],author='援航项目').build(story,onFirstPage=footer,onLaterPages=footer)
    print(pdf)

if __name__=='__main__':main()
