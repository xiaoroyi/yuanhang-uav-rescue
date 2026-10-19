"""Final comparison PDF authored only from verified saved result content."""
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

ROOT=Path(__file__).resolve().parents[2];EV=ROOT/'evidence/contest-baselines-v4';DEST=ROOT/'docs/current-project/contest-baselines-v4'

def main():
    data=json.loads((EV/'report_content.json').read_text(encoding='utf-8'));font='STSong-Light';pdfmetrics.registerFont(UnicodeCIDFont(font))
    ink=colors.HexColor('#172c40');accent=colors.HexColor('#126f78')
    styles={name:ParagraphStyle(name,fontName=font,fontSize=size,leading=leading,textColor=color,spaceAfter=after,wordWrap='CJK')
        for name,size,leading,color,after in [('title',21,29,ink,13),('h1',17,24,ink,11),('h2',11.5,17,accent,8),
            ('body',9.5,15,ink,8),('small',8,12,colors.HexColor('#526477'),7),('cell',8,12,ink,0),('head',8,12,colors.white,0)]}
    story=[]
    def para(t,s='body'):return Paragraph(escape(str(t)),styles[s])
    def add(t,s='body'):story.append(para(t,s))
    def table(headers,rows,widths):
        t=Table([[para(x,'head') for x in headers]]+[[para(x,'cell') for x in r] for r in rows],colWidths=[x*mm for x in widths],repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),accent),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),
            ('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#eef4f7'),colors.white]),('LINEBELOW',(0,-1),(-1,-1),.4,colors.HexColor('#d1dee6'))]))
        story.append(t);story.append(Spacer(1,11))
    add('援航 修正后的十分钟能耗对照','title');add('Q2 / Q3 | EXP-C05 | 单种子42 | 600秒追加搜索预算','small')
    add('8个配置、16个检查点全部通过独立物理与时限核验；Q3另通过完整连续通信核验。四种方法从同题的同一公共可行初解出发。结果表示共同可行性支持后的改进表现，论文方法仅引用历史结果。')
    add('统一约束','h2')
    for text in data['rules'][:3]:add(text)
    add('600秒预算内的最低已得能耗','h2')
    table(['问题','公共初解 kWh','本轮最低 kWh','论文历史 kWh'],[[s['question'],f"{s['initial']['energy_kwh']:.6f}",f"{s['best_600']['energy_kwh']:.6f}",f"{s['paper_E']:.6f}"] for s in data['summaries']],[19,49,50,50])
    add('论文历史计算预算与候选空间不同。表中数值可描述已得方案的差异，不能单独证明某算法在同预算、同候选条件下更优。','small')
    add(data['timing_text'],'small')
    for group in data['groups']:
        story.append(PageBreak());add(group['question']+' 能耗对照','h1');add('四种方法共用独立可行初解；180秒和600秒来自同一次连续搜索。','small')
        add(group['common_note'])
        table(group['headers'],group['rows'],[41,25,25,26,24,27])
        add('历史方案参考','h2');add(group['historical_note']);add(group['comparison'])
        add('如何读取这些结果','h2');add('“较初解节能”为公共初解能耗减去该方法600秒检查点能耗。数值为0时表示保留了共同初解；它是有效的完整方案，但不能据此称该方法从零完成了独立可行构造。')
        add('此处架次是任务执行次数，和实体飞机/能源库存不同；通过指方案核验通过，不代表证明原题全局最优。','small')
        if group['question']=='Q2':add(data['solver_note'],'small')
    story.append(PageBreak());add('相同能耗的原因与时间目标记录','h1')
    add('三个66.134是否正确','h2');add(data['stagnation_text'])
    add('时间最短实验已完成，但版本不同','h2');add(data['time_note'])
    table(data['time_headers'],data['time_rows'],[68,50,50])
    add('时间单位为秒；旧版8组均运行600秒。Q3启发式采用CP排程支持。论文行是原有历史方案，未重新计算。','small')
    story.append(PageBreak());add('实现、计时与结论范围','h1')
    for text in data['rules'][3:]:add(text,'small')
    add(data['repairs'],'small')
    add('适用范围','h2')
    for text in data['limitations']:add(text,'small')
    add('复现与核验','h2')
    add('scripts/contest_baselines/matrix_v4.py 为正式入口；使用新的输出名称重跑。正式协议、源码快照、候选指纹、日志、16份方案及独立核验位于 evidence/contest-baselines-v4/corrected_600s_seed42/。公共初解和失败预检保留在同级 preparation/。CSV提供完整数值精度。','small')
    add('本轮保留旧实验、原题输入、历史论文与方案，不将短预演或历史答案混入正式搜索成绩。','small')
    pdf=DEST/'援航修正后十分钟能耗对照报告.pdf'
    def footer(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#d1dee6'));canvas.line(21*mm,17*mm,189*mm,17*mm)
        canvas.setFont(font,8);canvas.setFillColor(colors.HexColor('#526477'));canvas.drawString(21*mm,12*mm,'援航 | EXP-C05 | 共享初始化后最多600秒');canvas.drawRightString(189*mm,12*mm,str(doc.page));canvas.restoreState()
    SimpleDocTemplate(str(pdf),pagesize=A4,leftMargin=21*mm,rightMargin=21*mm,topMargin=20*mm,bottomMargin=23*mm,
        title=data['title'],author='援航项目').build(story,onFirstPage=footer,onLaterPages=footer)
    print(pdf)

if __name__=='__main__':main()
