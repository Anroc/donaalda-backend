# -*- coding: utf-8 -*-
"""
from django.utils.encoding import smart_str
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate, \
    _doNothing
from reportlab.platypus.frames import Frame
from reportlab.platypus.paragraph import Paragraph
import copy
import re
from reportlab.platypus.flowables import KeepTogether, Image, PageBreak
from htmlentitydefs import name2codepoint
from atom.http_core import HttpResponse
import tempfile

def htmlentitydecode(s):
    return re.sub('&(%s);' % '|'.join(name2codepoint), lambda m: smart_str(unichr(name2codepoint[m.group(1)])), s)

PS = ParagraphStyle
stylesheet = StyleSheet1()

stylesheet.add(PS(name='Normal',
                  leading=15))
stylesheet.add(PS(name='Bullet',
                  parent=stylesheet['Normal'],
                  bulletFontName = 'Symbol',
                  bulletIndent = 0,
                  bulletFontSize = 13,
                  bulletColor = Color(0.93,0,0),
                  bulletOffsetY = -1.5,
                  leftIndent = 15.8,
                  firstLineIndent = 0,
                ), alias='bu')
stylesheet.add(PS(name='Heading1',
                  parent=stylesheet['Normal'],
                  fontSize=18,
                  spaceAfter=23.5), alias='h1')
stylesheet.add(PS(name='Heading2',
                  parent=stylesheet['Normal'],
                  fontSize=14,
                  spaceAfter=4), alias='h2')
stylesheet.add(PS(name='Heading3',
                  parent=stylesheet['Normal'],
                  textColor=Color(0.93,0,0)
                  ), alias='h3')
stylesheet.add(PS(name='Heading4',
                  parent=stylesheet['Heading3'],
                  textColor='black'), alias='h4')

BulletStyle = copy.deepcopy(stylesheet["Bullet"])
H1Style = copy.deepcopy(stylesheet["Heading1"])
H2Style = copy.deepcopy(stylesheet["Heading2"])
H3Style = copy.deepcopy(stylesheet["Heading3"])
H4Style = copy.deepcopy(stylesheet["Heading4"])
NormalStyle = copy.deepcopy(stylesheet["Normal"])

top_margin = A4[1] - 1.22*cm
bottom_margin = 1.5*cm
left_margin = 2.8*cm
frame_width = 17.02*cm

right_margin = left_margin + frame_width
frame_height = 22.7*cm

letter_top_margin = 25.0*cm
letter_bottom_margin = 3.0*cm
letter_left_margin = 2.5*cm
letter_right_margin = A4[0] - 2.5*cm
letter_frame_width = A4[0] - 5.0*cm
letter_frame_height = letter_top_margin - letter_bottom_margin


class LetterTemplate(BaseDocTemplate):
    _invalidInitArgs = ('pageTemplates',)

    def handle_pageBegin(self):
        self._handle_pageBegin()
        self._handle_nextPageTemplate('First')

    def build(self, flowables, onFirstPage=_doNothing, canvasmaker=canvas.Canvas):
        self._calc()

        frameT = Frame(letter_left_margin, letter_bottom_margin, letter_frame_width, letter_frame_height,
                       leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0,
                       id='normal')

        self.addPageTemplates([PageTemplate(id='First',frames=frameT, onPage=onFirstPage, pagesize=self.pagesize)])

        if onFirstPage is _doNothing and hasattr(self,'onFirstPage'):
            self.pageTemplates[0].beforeDrawPage = self.onFirstPage

        BaseDocTemplate.build(self, flowables, canvasmaker=canvasmaker)


class PdfA4Letter(object):

    def __init__(self, filename):
        self.title = filename
        self._keep_together = False
        self.elements = []
        self._keep_together_elements = []
        self.doc = LetterTemplate(filename,showBoundary=False)
        self.elements = []

    def _process_text(self, txt):
        text_elems = []

        # avoid us from user added html.
        txt = txt.replace('&lt;','&lang;').replace('&gt;','&rang;')
        txt = htmlentitydecode(smart_str(txt).replace('<p>', '').replace('</p>', '<br />'))

        # @todo: in some case the reegxp does not work -> hack
        txt = txt.replace('target="_blank"', '')
        # process text
        for part in re.split('<ul>|</ul>|<ol>|</ol>', txt):
            part = part.strip()
            if part.count('<li>') > 0:
                for item in re.split('<li>|</li>', part):
                    item = item.strip()
                    if len(item) > 0:
                        text_elems.append(Paragraph(item, BulletStyle, bulletText=u'•'))
            else:
                text_elems.append(Paragraph(part, NormalStyle))
        return text_elems

    def _store_flowable(self, flowable):
        if self._keep_together == False:
            self.elements.append(flowable)
        else:
            self._keep_together_elements.append(flowable)

    def start_keep_together(self):
        self.end_keep_together()
        self._keep_together = True

    def end_keep_together(self):
        self._keep_together = False
        if len(self._keep_together_elements) > 0:
            e = self._keep_together_elements
            self.elements.append(KeepTogether(e))
            self._keep_together_elements = []

    def newPage(self):
        self._store_flowable(PageBreak())

    def blankline(self, cnt=1):
        self.text(cnt*'<br/>')

    def text(self, txt):
        for e in self._process_text(txt):
            self._store_flowable(e)

    def image(self, name, width, height, halign='CENTER'):
        im = Image(name, width=width, height=height)
        im.hAlign = halign
        self._store_flowable(im)

    def h1(self, txt, add_to_toc=True):
        self.newPage()
        self._store_flowable(Paragraph(txt, H1Style))

    def h2(self, txt, add_to_toc=True):
        self._store_flowable(Paragraph(txt, H2Style))

    def h3(self, txt, add_to_toc=False):
        self._store_flowable(Paragraph(txt, H3Style))

    def h4(self, txt, add_to_toc=False):
        self._store_flowable(Paragraph(txt, H4Style))

    def _drawPage(self, canvas, doc):
        canvas.setSubject('Letter Subject')
        canvas.setTitle('Letter Title')
        canvas.setAuthor('Me')

    def build(self):
        # flush elems
        self.end_keep_together()
        self.doc.build(self.elements, self._drawPage)
"""
