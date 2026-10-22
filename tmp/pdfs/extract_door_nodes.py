import pymupdf as f

source=f.open('output/pdf/Двери В РАБОТУ.pdf')
# Remove an unrelated adjacent section from the reference fragment in memory.
source[1].add_redact_annot(f.Rect(715,640,890,805),fill=(1,1,1))
source[1].apply_redactions()
out=f.open()
W,H=1190.55,841.89
def add(title,subtitle,index,clip,foot):
    p=out.new_page(width=W,height=H)
    p.insert_font(fontname='AR',fontfile='C:/Windows/Fonts/arial.ttf')
    p.draw_rect(f.Rect(20,20,W-20,H-20),color=(.2,.2,.2),width=.6)
    p.insert_text((40,48),title,fontname='AR',fontsize=18)
    p.insert_text((40,70),subtitle,fontname='AR',fontsize=10)
    p.show_pdf_page(f.Rect(45,90,W-45,H-85),source,index,clip=clip,keep_proportion=True)
    p.draw_line((40,H-69),(W-40,H-69),color=(.3,.3,.3),width=.5)
    p.insert_text((40,H-48),foot,fontname='AR',fontsize=10)
    p.insert_text((40,H-31),'Фрагменты исходного проекта. Размеры сохранены; перед применением к нашему проёму требуется адаптация.',fontname='AR',fontsize=9)

add('ОБРАЗЕЦ 1 / СБОРНЫЙ УЗЕЛ ДВЕРНОЙ КОРОБКИ',
    'Источник: «Двери В РАБОТУ.pdf», печатный лист 1 (страница PDF 2), разрез B-B.',
    1,f.Rect(720,45,1110,781),
    'Пример детализации: коробка, добор, наличники, притвор, уплотнение и состав дверного полотна.')
add('ОБРАЗЕЦ 2 / ТИПОВЫЕ РАЗРЕЗЫ',
    'Источник: «Двери В РАБОТУ.pdf», печатный лист 14 (страница PDF 15).',
    14,f.Rect(55,10,1125,815),
    'За основу принимаем показ состава деталей и сопряжений: МДФ, фанера, сосна, филёнка / стекло.')
add('ОБРАЗЕЦ 3 / ПРОФИЛИ ДЕТАЛЕЙ',
    'Источник: «Двери В РАБОТУ.pdf», печатный лист 17 (страница PDF 18).',
    17,f.Rect(100,70,815,650),
    'За основу принимаем профили с пазами и четвертями, размеры сечений и размерные цепочки.')

out.save('output/pdf/door_nodes_reference.pdf',garbage=4,deflate=True)
out.close()
check=f.open('output/pdf/door_nodes_reference.pdf')
for i,p in enumerate(check):
    p.get_pixmap(matrix=f.Matrix(1.1,1.1)).save(f'tmp/pdfs/door_nodes_reference_{i+1}.png')
print('Created 3 vector reference sheets')
