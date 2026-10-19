"""Four-page aligned comparison report, using the verified content model."""
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

ROOT=Path(__file__).resolve().parents[2];EV=ROOT/'evidence/contest-baselines-v3';DEST=ROOT/'docs/current-project/contest-baselines-v3'

def main():
    data=json.loads((EV/'report_content.json').read_text(encoding='utf-8'))
    font='STSong-Light';pdfmetrics.registerFont(UnicodeCIDFont(font));ink=colors.HexColor('#172c40');accent=colors.HexColor('#126f78')
    styles={name:ParagraphStyle(name,fontName=font,fontSize=size,leading=leading,textColor=color,spaceAfter=after,wordWrap='CJK')
        for name,size,leading,color,after in [('title',21,29,ink,12),('h1',17,24,ink,10),('h2',11.5,17,accent,7),
            ('body',9.5,15,ink,8),('small',8,12,colors.HexColor('#526477'),6),('cell',8.3,12,ink,0),('head',8.3,12,colors.white,0)]}
    story=[]
    def para(t,s='body'):return Paragraph(escape(str(t)),styles[s])
    def add(t,s='body'):story.append(para(t,s))
    def table(headers,rows,widths):
        t=Table([[para(x,'head') for x in headers]]+[[para(x,'cell') for x in row] for row in rows],colWidths=[v*mm for v in widths],repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),accent),('VALIGN',(0,0),(-1,-1),'TOP'),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f0f5f8'),colors.white]),
            ('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),
            ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
            ('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#ccd8e1'))]))
        story.extend([t,Spacer(1,10)])
    add('援航 · 对齐上限后的能耗对照','title')
    add('Q2 / Q3 | EXP-C03 | 600秒 / 配置 | seed 42','small');add(data['intro'])
    add('本轮明确采用的条件','h2')
    for t in data['rules'][:4]:add(t)
    add('合规方案获取情况','h2')
    table(['问题','180秒检查点','600秒检查点','分母'],[[g['question'],str(g['feasible180']),str(g['feasible']),4] for g in data['groups']],[35,45,45,43])
    add('数值为本次获得合规方案的方法数，不是跨种子成功概率。未获得方案的单元格在详细表中留空，不用0kWh代替。','small')
    add(data['timing'],'small')
    for g in data['groups']:
        story.append(PageBreak());add(g['question']+' · 对齐上限的能耗结果','h1')
        add('每方法一次600秒连续搜索，分别保留180秒与600秒检查点。','small')
        table(g['headers'],g['rows'],[44,17,28,26,25,28]);add(g['summary'])
        add('约束与内部求解状态','h2')
        add(data['rules'][0 if g['question']=='Q2' else 1],'small')
        state=next(r for r in data['solver_status'] if r[0]==g['question'])
        add(f'完整池CP-SAT：{state[1]}；实际搜索墙钟{state[2]}秒。当前有限模型能耗下界{state[3]}kWh，仅限本轮路线/驻点/网格，不是原题下界。状态与合规方案指标分开报告。','small')
        add('读取方法','h2');add('“—”表示在该检查点之前没有获得满足全部上限并通过独立核验的完整解。它不是能耗为零，也不证明原题无解。论文行是历史方案，未重跑；其搜索总预算和候选空间仍不同。')
        add('本轮不读论文路线、分组、时刻和中继驻点作初解；普通贪心参考若超限，仅用于可行性搜索，不能作为正式成果。','small')
    story.append(PageBreak());add('实现、核验与结论范围','h1')
    for t in data['rules'][4:]:add(t,'small')
    add('适用范围','h2')
    for t in data['caveats']:add(t,'small')
    add('复核与复现','h2');add(data['evidence'],'small')
    add('代码入口：scripts/contest_baselines/matrix_v3.py。复现请使用新输出目录，保留既有协议和日志。完整精度与运行状态见随附CSV及Markdown。','small')
    def footer(c,d):
        c.saveState();c.setStrokeColor(colors.HexColor('#d6e0e8'));c.line(21*mm,17*mm,A4[0]-21*mm,17*mm)
        c.setFont(font,8);c.setFillColor(colors.HexColor('#526477'));c.drawString(21*mm,12*mm,'援航 | EXP-C03 | aligned horizons | 600s / configuration');c.drawRightString(A4[0]-21*mm,12*mm,str(d.page));c.restoreState()
    path=DEST/'援航对齐上限能耗对照报告.pdf'
    SimpleDocTemplate(str(path),pagesize=A4,leftMargin=21*mm,rightMargin=21*mm,topMargin=20*mm,bottomMargin=23*mm,
        title='援航Q2/Q3对齐上限能耗对照',author='援航项目').build(story,onFirstPage=footer,onLaterPages=footer)
    print(path)

if __name__=='__main__':main()
