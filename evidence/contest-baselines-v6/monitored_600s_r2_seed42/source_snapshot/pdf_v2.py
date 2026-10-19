"""Render the final report from the same content model as Markdown (ReportLab)."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,KeepTogether

ROOT=Path(__file__).resolve().parents[2]
EV=ROOT/'evidence/contest-baselines-v2'
DEST=ROOT/'docs/current-project/contest-baselines-v2'
INK=colors.HexColor('#172c40');MUTED=colors.HexColor('#526477');ACCENT=colors.HexColor('#126f78')
FONT='STSong-Light'

def main():
    data=json.loads((EV/'report_content.json').read_text(encoding='utf-8'))
    pdfmetrics.registerFont(UnicodeCIDFont(FONT))
    styles={
        'title':ParagraphStyle('title',fontName=FONT,fontSize=22,leading=30,textColor=INK,spaceAfter=12),
        'h1':ParagraphStyle('h1',fontName=FONT,fontSize=17,leading=24,textColor=INK,spaceAfter=10),
        'h2':ParagraphStyle('h2',fontName=FONT,fontSize=11.5,leading=17,textColor=ACCENT,spaceBefore=9,spaceAfter=5),
        'body':ParagraphStyle('body',fontName=FONT,fontSize=9.5,leading=15,textColor=INK,spaceAfter=7,wordWrap='CJK'),
        'small':ParagraphStyle('small',fontName=FONT,fontSize=8,leading=12,textColor=MUTED,spaceAfter=6,wordWrap='CJK'),
        'cell':ParagraphStyle('cell',fontName=FONT,fontSize=8.5,leading=12,textColor=INK,wordWrap='CJK'),
        'head':ParagraphStyle('head',fontName=FONT,fontSize=8.5,leading=12,textColor=colors.white,wordWrap='CJK')}
    story=[]
    def p(s,kind='body'):return Paragraph(escape(s),styles[kind])
    def add(s,kind='body'):story.append(p(s,kind))
    def tab(headers,rows,widths):
        cells=[[p(str(v),'head') for v in headers]]+[[p(str(v),'cell') for v in row] for row in rows]
        t=Table(cells,colWidths=[x*mm for x in widths],repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),ACCENT),('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f0f5f8'),colors.white]),
            ('LINEBELOW',(0,0),(-1,0),.5,ACCENT),('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#ccd8e1'))]))
        story.extend([t,Spacer(1,10)])
    add('援航 · 十分钟基线对比实验','title')
    add('原题第二问 / 第三问  |  时间与总能耗  |  2026年10月19日','small')
    add(data['intro'])
    add('相同版本的3分钟与10分钟结果','h2')
    tab(['任务 / 目标','180秒最佳','600秒最佳','目标降低','论文参考'],[x['display'] for x in data['summaries']],[35,34,34,24,41])
    add('时间行单位为秒，能耗行单位为kWh。每列最佳可来自不同方法；论文是历史参考，预算与候选空间未匹配，节能备选的全部返航上限也未与本轮对齐。','small')
    add('统一口径','h2')
    for i in [0,1,2,3,4]:add(data['protocol'][i],'small')
    add(data['timing'],'small')
    for g in data['groups']:
        story.append(PageBreak());add(g['title'],'h1')
        add('每方法一次600秒连续搜索；下表分别读取180秒与600秒检查点。','small')
        tab(g['headers'],g['rows'],[47,18,29,27,29,18])
        add(g['comparison'])
        add(g['cp_note'],'small')
        add('如何读这张表','h2')
        add('“预算”表示方案发现时间的检查点；“全部返航”和“总能耗”来自同一完整方案。主目标改善时，另一指标可能变差。全部有数值的基线均已通过完整核验。')
        if g['question']=='Q3':
            add('Q3的前三类方法均与CP排程组合。总能耗包括运输与中继，完成时间也包含中继返航；核验覆盖连续通信全过程，缺口与未确定区间均为零。')
        if g['objective']=='energy':
            add('本轮能耗组没有额外返航时间上限，论文Q2/Q3节能参考是有短时域要求的备选。整站零延期不等于全部返航同样快；同条件节能比较需要统一返航上限后重跑。')
        add('本组实际搜索墙钟','h2')
        records=json.loads((EV/'main_600s_seed42/results.json').read_text(encoding='utf-8'))
        names={'greedy':'多起点贪心','aco':'ACO','alns':'ALNS','cp_sat':'CP-SAT'}
        add('；'.join(f"{names[r['method']]} {r['search_wall_s']:.3f}秒" for r in records if r['question']==g['question'] and r['objective']==g['objective'])+'。最终独立核验另计。','small')
        add('证据定位','h2')
        add(f"evidence/contest-baselines-v2/main_600s_seed42/{g['question']}_{g['objective']}_方法名/：run.json、两个checkpoint方案及各自validation.json。完整精度见随附32行CSV。",'small')
    story.append(PageBreak());add('方法、核验与适用边界','h1')
    for a,b in data['methods']:add(a+'：'+b,'small')
    add('预算与检查点','h2')
    for i in [5,6,7]:add(data['protocol'][i],'small')
    add(data['unchanged'],'small')
    add('结论范围','h2')
    for text in data['limits']:add(text,'small')
    story.append(PageBreak());add('已知方案交叉检查与复现','h1')
    add('为避免遗漏较强对照，本页在每题全部目标组中取最小值，同时保留旧版已知成绩。这张表累计使用多次运行，不是单次600秒算法成绩。')
    tab(['指标','v1全部目标最小','v2全部目标最小','两版本最低值来源'],data['strongest'],[27,35,35,71])
    add('时间实测','h2');add(data['timing'],'small')
    add('证据与复现','h2')
    add(data['evidence'],'small')
    add('代码：scripts/contest_baselines/benchmark_v2.py、matrix_v2.py、check_v2.py。复现命令与项目文档建议表述见随附Markdown。','small')
    add('项目文档建议表述','h2');add(data['project_prose'],'small')
    def footer(c,doc):
        c.saveState();w,h=A4;c.setStrokeColor(colors.HexColor('#d6e0e8'));c.line(21*mm,17*mm,w-21*mm,17*mm)
        c.setFont(FONT,8);c.setFillColor(MUTED);c.drawString(21*mm,12*mm,'援航 | EXP-C02 | seed 42 | 600s / configuration')
        c.drawRightString(w-21*mm,12*mm,str(doc.page));c.restoreState()
    path=DEST/'援航十分钟基线对比实验报告.pdf'
    SimpleDocTemplate(str(path),pagesize=A4,rightMargin=21*mm,leftMargin=21*mm,
        topMargin=20*mm,bottomMargin=23*mm,title='援航Q2/Q3十分钟基线对比实验',author='援航项目').build(story,onFirstPage=footer,onLaterPages=footer)
    print(path)

if __name__=='__main__':main()
