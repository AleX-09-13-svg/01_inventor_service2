from pathlib import Path
import pymupdf as pdf

OUT = Path('output/pdf/shelving_concept.pdf')
doc = pdf.open()
p = doc.new_page(width=1190.55, height=841.89)  # A3 landscape
p.insert_font(fontname='Arial', fontfile='C:/Windows/Fonts/arial.ttf')
BLACK = (0.12, 0.15, 0.18)
GRAY = (0.45, 0.48, 0.5)
BLUE = (0.1, 0.29, 0.45)

def text(x, y, s, size=10, color=BLACK):
    p.insert_text((x, y), s, fontname='Arial', fontsize=size, color=color)

def line(x1, y1, x2, y2, width=.6, color=BLACK):
    p.draw_line((x1, y1), (x2, y2), width=width, color=color)

def rect(x, y, w, h, fill=None, width=.7):
    p.draw_rect(pdf.Rect(x,y,x+w,y+h), color=BLACK, fill=fill, width=width)

def dh(x1, x2, y, edge, label):
    for x in (x1,x2):
        line(x,edge,x,y+5,.35,GRAY)
        line(x-3,y+3,x+3,y-3,.6)
    line(x1,y,x2,y,.35)
    text((x1+x2)/2-len(label)*2.5,y-5,label,9)

def dv(y1,y2,x,edge,label):
    for y in (y1,y2):
        line(edge,y,x+5,y,.35,GRAY)
        line(x-3,y+3,x+3,y-3,.6)
    line(x,y1,x,y2,.35)
    text(x+6,(y1+y2)/2,label,9)

rect(18,18,1154,806)
text(36,47,'СТЕЛЛАЖ С ТВ-НИШЕЙ / ПРЕДВАРИТЕЛЬНАЯ СХЕМА',19,BLUE)
text(36,68,'Этап 1 из 3: стеллаж. Дверной блок и стеновые панели в этот лист не входят.',10)
text(36,90,'Размеры в мм. Схема новой конструкции по мотивам исходного листа; не является деталировкой для изготовления.',10)

# General elevation, nominal scale 1:10.
s=72/25.4/10
x,y=70,153
W,H,D=4210,3000,450
w,h=W*s,H*s
# Fit overview at 1:20 instead, allowing all notes on the same sheet.
s=72/25.4/20
w,h=W*s,H*s
t=22*s
text(x,y-15,'1. Общий вид / М 1:20',12,BLUE)
rect(x,y,w,h)
plinth=150*s
cornice=300*s
bottom=y+h-plinth
top=y+cornice
rect(x,y,w,cornice,(.94,.94,.94))
rect(x,bottom,w,plinth,(.94,.94,.94))
rect(x,top,t,bottom-top)
rect(x+w-t,top,t,bottom-top)
# Side fields of 827 mm are preliminary module widths.
a=x+827*s
b=x+w-827*s
rect(a-t/2,top,t,bottom-top)
rect(b-t/2,top,t,bottom-top)
low=bottom-700*s
rect(x+t,low,w-2*t,t)
for yy in [low-400*s,low-800*s,low-1200*s,low-1600*s]:
    rect(x+t,yy,a-x-t*1.5,t)
    rect(b+t/2,yy,x+w-t-b-t/2,t)
for xx in [x+w*.25,x+w*.5,x+w*.75]:
    line(xx,low+t,xx,bottom)
text(a+35,top+45,'ТВ-НИША',14)
text(a+20,top+64,'Размер ТВ и кабельные выводы уточнить',9)
text(a+15,low-12,'Нижняя секция: высота 700, предварительно',10)
dh(x,x+w,y+h+25,y+h,'4210')
dv(y,y+h,x-30,x,'3000*')
dh(x,a,y+h+49,y+h,'827*')
dh(a,b,y+h+49,y+h,'2556*')
dh(b,x+w,y+h+49,y+h,'827*')

# Side section.
sx,sy=790,153
text(sx-12,sy-15,'2. Разрез по полке / М 1:20',12,BLUE)
depth=D*s
rect(sx,sy,depth,h)
rect(sx,sy,6*s,h-plinth,(.88,.88,.88))
for yy in [top,low,low-400*s,low-800*s,low-1200*s,low-1600*s,bottom-t]:
    rect(sx+6*s,yy,depth-6*s,t,(.92,.92,.92))
dh(sx,sx+depth,sy+h+25,sy+h,'450*')
text(890,175,'Принятые решения',12,BLUE)
notes=[
    'Корпус и полки: МДФ со шпоном.',
    'Итоговая толщина: 22 мм*.',
    'Задняя стенка: 6 мм*, в паз.',
    'Полки боковых секций: съёмные.',
    'Низ: регулируемые опоры,',
    'закрытые съёмным цоколем.',
    'Карниз: отдельный декоративный',
    'элемент на монтажной рейке.',
    '',
    '* Предварительные значения.',
    'Высота 3000 взята как габарит',
    'композиции из исходного листа.',
    'Рабочую высоту корпуса уточнить',
    'по обмеру и профилю карниза.',
]
for i,n in enumerate(notes): text(890,197+i*16,n,10)

# Enlarged support detail, schematic with no drilling coordinates.
text(55,692,'3. Принцип опирания съёмной полки / без масштаба',12,BLUE)
rect(70,710,22,70,(.89,.89,.89))
rect(94,724,170,22,(.96,.96,.96))
rect(92,746,27,6,(.5,.55,.6))
line(82,749,108,749,3)
line(128,749,162,779)
text(70,808,'Полкодержатель со штифтом Ø5*',10)
text(288,730,'Зазор полки у боковины: 1 мм* с каждой стороны.',10)
text(288,748,'Крепёж: 4 опоры на полку, с фиксацией от сдвига.',10)
text(288,766,'Модель опоры, присадку и нагрузку уточнить до выпуска деталей.',10)
text(288,784,'Стационарные связи: мебельные стяжки и шканты, тип уточнить.',10)

text(895,590,'Перед деталировкой',12,BLUE)
for i,n in enumerate([
    '1. Проверить размеры помещения.',
    '2. Согласовать толщину со шпоном.',
    '3. Уточнить ТВ и нагрузку полок.',
    '4. Выбрать конкретную фурнитуру.',
    '5. Проработать крепление к стене',
    '   по материалу основания.',
]): text(895,613+i*16,n,10)
line(870,730,1153,730)
text(890,752,'СТАДИЯ: ЭСКИЗ / Лист 1 из 1',11,BLUE)
text(890,773,'Дата: 16.10.2026',10)
text(890,794,'Исходник: redirect.pdf, лист 1',10)
doc.save(OUT, garbage=4, deflate=True)
doc.close()
check=pdf.open(OUT)
assert len(check)==1
assert '4210' in check[0].get_text()
check[0].get_pixmap(matrix=pdf.Matrix(1.4,1.4)).save('tmp/pdfs/shelving_concept.png')
print(OUT.resolve())
