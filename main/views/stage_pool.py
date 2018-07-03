from django.http import HttpResponse
from django.shortcuts import render
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import Table, SimpleDocTemplate, TableStyle, PageBreak, Paragraph, Spacer
from reportlab.lib import colors, styles
from main.models import Pool, Stage, Entry


headerStyle = styles.ParagraphStyle('header',
                                        fontSize=15,
                                        alignment=styles.TA_CENTER)


def pools(request, stage: Stage):
    context = {}
    pool_list = []
    for p in stage.pool_set.order_by('number').all():
        pools.append(gen_pool_data(p))
    context['pools'] = pools
    return render(request, 'main/pool/pools.html')


def pools_pdf(request, stage: Stage):
    """Generates a PDF with one pool sheet to every page"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}-{}.pdf"'.format(stage.competition.name, stage.number)
    p = SimpleDocTemplate(response, pagesize=landscape(A4))

    basestyle = [('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                 ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                 ('BOX', (0, 0), (-1, -1), 0.5, colors.black)]

    header = Paragraph("<u>{} - Round {}</u>".format(stage.competition.name,stage.number), headerStyle)

    doc = []
    # iterating over each pool in the stage to make results sheets for them
    for pool in stage.pool_set.order_by('number').all():
        table = Table(gen_pool_data(pool))
        # blanking cells where fencers would fight themselves
        style = list(basestyle)
        for index in range(pool.poolentry_set.count()):
            cell = (2+index, 1+index)
            style.append(('BACKGROUND', cell, cell, colors.gray))
        table.setStyle(TableStyle(style))

        sub_heading = Paragraph("Pool {}".format(pool.number), headerStyle)

        doc.extend([header, Spacer(0, 10), sub_heading, Spacer(0, 10), table, PageBreak()])

    p.build(doc)
    return response


def results(request, stage: Stage):
    context = {}
    fencer_details = stage.ordered_competitors()
    competitors = map(lambda x: (Entry.objects.get(pk=x.ID).competitor, x), fencer_details)
    context['competitors'] = enumerate(list(competitors))
    return render(request, 'main/pool/seeding.html', context)


def results_pdf(request, stage: Stage):
    data = [['Pl', 'Name', 'Club', 'V/M', 'TS', 'TR', 'Ind']]
    for index, f in enumerate(stage.ordered_competitors()):
        entry = Entry.objects.get(pk=f.ID)
        data.append([index + 1,
                     entry.competitor.name,
                     entry.competitor.club.name,
                     "{:.2}".format(f.win_percentage),
                     f.TS,
                     f.TR,
                     f.ind()])
    basestyle = [('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                 ('BACKGROUND', (0, 0), (-1, 0), colors.lightslategray),
                 ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                 ('BOX', (0, 0), (-1, -1), 0.5, colors.black)]
    table = Table(data, repeatRows=1)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}-{}-results.pdf"'.format(stage.competition.name, stage.number)
    p = SimpleDocTemplate(response, pagesize=A4)
    p.build([Paragraph("<u>{} - Round {}</u>".format(stage.competition.name, stage.number), headerStyle),
             Spacer(0, 10),
             table])
    return response



def gen_pool_data(pool: Pool):
    """generates a list of lists representing each row in a pool and the column headings"""
    fencers = pool.poolentry_set.order_by('number').all()
    out = []

    # column headings
    line = []
    line.extend(['name', '#'])
    for f in fencers:
        line.append(f.number)
    line.extend(['', 'V', 'TS', 'TR', 'Ind'])
    out.append(line)

    # rows with fencers bouts in them
    for index, f in enumerate(fencers):
        line = [f.entry.competitor.name, index+1]
        for ind, b in enumerate(f.fencerA_bout_set.all()):
            if b.victoryA:
                line.append('V' + str(b.scoreA))
            else:
                line.append('D' + str(b.scoreA))
        line.insert(index + 2, '')  # the blank space where the fencer can't fight themselves
        line.append('')
        line.append(f.victories())
        ts = f.ts()
        tr = f.tr()
        line.append(ts)
        line.append(tr)
        line.append(ts-tr)
        out.append(line)

    return out

