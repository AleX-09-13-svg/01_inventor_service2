"""Transfer artifact-authored fills while preserving Excel views and legacy notes.

Mixed-category strings need OOXML rich-text runs, absent from the documented
artifact range API. Only the affected cells and style records are patched.
"""
import pathlib,json,zipfile,xml.etree.ElementTree as E,re,copy,html,shutil
root=pathlib.Path(__file__).parent
src=next(p for p in (root/'../infa').glob('*.xlsx') if not p.name.startswith('~'))
out=root/'../outputs/method_layers'
spec=json.loads((root/'method_layers.json').read_text(encoding='utf-8'))
ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
n={'s':ns}; E.register_namespace('',ns)
def tag(s): return '{'+ns+'}'+s
with zipfile.ZipFile(src) as z: parts={i.filename:z.read(i.filename) for i in z.infolist()}
original=dict(parts)
styles=E.fromstring(parts['xl/styles.xml']); fills=styles.find('s:fills',n); xfs=styles.find('s:cellXfs',n)
with zipfile.ZipFile(out/'styled.xlsx') as z:
 ast=E.fromstring(z.read('xl/styles.xml')); af=ast.find('s:fills',n); ax=ast.find('s:cellXfs',n)
 styled={name:E.fromstring(z.read(name)) for name in ['xl/worksheets/sheet1.xml','xl/worksheets/sheet2.xml']}
paths={'Структура папок':'xl/worksheets/sheet1.xml','Лист1':'xl/worksheets/sheet2.xml'}
cache={}
def style(old,fill):
 key=(old,fill)
 if key not in cache:
  fid=len(fills); fills.append(copy.deepcopy(fill)); xf=copy.deepcopy(xfs[int(old)]); xf.set('fillId',str(fid)); xf.set('applyFill','1'); cache[key]=len(xfs); xfs.append(xf)
 return str(cache[key])
def replace_cell(path,addr,fn):
 text=parts[path].decode('utf-8')
 pattern=rf'<c\b[^>]*\br="{addr}"[^>]*(?:/>|>.*?</c>)'
 text,count=re.subn(pattern,lambda m:fn(m.group()),text,count=1,flags=re.S)
 assert count==1,(path,addr)
 parts[path]=text.encode('utf-8')
for item in spec['cells']:
 path=paths[item['sheet']]; addr=item['cell']
 ac=styled[path].find(f'.//s:c[@r="{addr}"]',n)
 fill=af[int(ax[int(ac.get('s','0'))].get('fillId','0'))]
 def patch(raw):
  old=re.search(r'\bs="(\d+)"',raw); sid=style(old.group(1) if old else '0',fill)
  return re.sub(r'\bs="\d+"',f's="{sid}"',raw,count=1) if old else raw.replace('<c ',f'<c s="{sid}" ',1)
 replace_cell(path,addr,patch)
for item in spec['mixed']:
 def patch(raw):
  head=raw[:raw.index('>')+1]; head=re.sub(r'\bt="[^"]*"','t="inlineStr"',head)
  if 't="inlineStr"' not in head: head=head[:-1]+' t="inlineStr">'
  runs=[]; cursor=0
  for m in item['methods']:
   if m['start']>cursor: runs.append('<r><t xml:space="preserve">'+html.escape(item['text'][cursor:m['start']])+'</t></r>')
   color=spec['fonts'][m['category']][1:]
   runs.append(f'<r><rPr><color rgb="FF{color}"/><b/></rPr><t xml:space="preserve">'+html.escape(item['text'][m['start']:m['end']])+'</t></r>'); cursor=m['end']
  if cursor<len(item['text']): runs.append('<r><t xml:space="preserve">'+html.escape(item['text'][cursor:])+'</t></r>')
  return head+'<is>'+''.join(runs)+'</is></c>'
 replace_cell(paths[item['sheet']],item['cell'],patch)
# Legend in existing empty cells of the explanatory sheet.
path=paths['Лист1']; xml=parts[path].decode('utf-8')
for row,cat,label in [(5,'api','Базовые обёртки API'),(6,'helper','Вспомогательные методы'),(7,'app','Прикладные методы')]:
 fill=E.Element(tag('fill')); pat=E.SubElement(fill,tag('patternFill'),patternType='solid'); E.SubElement(pat,tag('fgColor'),rgb='FF'+spec['colors'][cat][1:]); E.SubElement(pat,tag('bgColor'),indexed='64')
 sid=style('0',fill)
 cell=f'<c r="H{row}" s="{sid}" t="inlineStr"><is><t>{label}</t></is></c>'
 pattern=rf'(<row\b[^>]*\br="{row}"[^>]*>)(.*?)(</row>)'
 if re.search(pattern,xml,re.S):
  def insert(m):
   body=re.sub(rf'<c\b[^>]*r="H{row}"[^>]*(?:/>|>.*?</c>)','',m.group(2),flags=re.S)
   return m.group(1)+body+cell+m.group(3)
  xml=re.sub(pattern,insert,xml,count=1,flags=re.S)
 else:
  xml=re.sub(rf'(<row\b[^>]*r="(?:{row+1}|{row+2})"[^>]*>)',f'<row r="{row}">{cell}</row>'+r'\1',xml,count=1)
parts[path]=xml.encode('utf-8')
fills.set('count',str(len(fills))); xfs.set('count',str(len(xfs)))
# Preserve original namespace declarations and all unmodified styles XML sections.
stext=original['xl/styles.xml'].decode('utf-8')
for name,node in [('fills',fills),('cellXfs',xfs)]:
 fragment=E.tostring(node,encoding='unicode').replace(' xmlns="'+ns+'"','')
 stext=re.sub(rf'<{name}\b.*?</{name}>',lambda _:fragment,stext,count=1,flags=re.S)
parts['xl/styles.xml']=stext.encode('utf-8')
dest=out/src.name
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
 for name,data in parts.items(): z.writestr(name,data)
# Verify every existing cell text/formula and all unrelated package parts.
def content(data,ss):
 result={}
 for c in E.fromstring(data).findall('.//s:sheetData/s:row/s:c',n):
  if c.get('t')=='s': val=ss[int(c.find('s:v',n).text)]
  elif c.get('t')=='inlineStr': val=''.join(c.find('s:is',n).itertext())
  else: val=E.tostring(c.find('s:v',n)) if c.find('s:v',n) is not None else None
  formula=c.find('s:f',n)
  result[c.get('r')]=(val,E.tostring(formula) if formula is not None else None)
 return result
ss=[''.join(si.itertext()) for si in E.fromstring(original['xl/sharedStrings.xml']).findall('s:si',n)]
for path in paths.values():
 before=content(original[path],ss); after=content(parts[path],ss)
 for addr,value in before.items():
  if path==paths['Лист1'] and addr in ['H5','H6','H7']:
   assert value[0] in (None,''),(path,addr,'legend overwrites content')
  else: assert after[addr]==value,(path,addr)
for name in original:
 if name not in {*paths.values(),'xl/styles.xml'}: assert original[name]==parts[name],name
shutil.copy2(src,out/'source_before.xlsx')
try:
 shutil.copyfile(dest,src)
 print('UPDATED SOURCE:',src.resolve())
except PermissionError:
 print('SOURCE LOCKED; DELIVER:',dest.resolve())
print('Verified: existing values, formulas and unrelated workbook parts unchanged.')
