import zipfile,re,json,datetime,csv
import os; P=os.path.dirname(os.path.abspath(__file__))+"/"
s=zipfile.ZipFile(P+"dataset.xlsx").read("xl/worksheets/sheet1.xml").decode()
def un(v): return v.replace('&lt;','<').replace('&gt;','>').replace('&quot;','"').replace('&apos;',"'").replace('&amp;','&')
def cells(r):
    out={}
    for m in re.finditer(r'<c r="([A-Z]+)\d+"[^>]*?(?:/>|>(.*?)</c>)',r,re.S):
        out[m.group(1)]=un(re.sub('<[^>]+>','',m.group(2) or ''))
    return out
rows=re.findall(r'<row[^>]*>(.*?)</row>',s,re.S)
hdr=cells(rows[0])
base=datetime.date(1899,12,30)
def hm(x): return round(float(x)*1440) if x else None
orders={}
for r in rows[1:]:
    c={hdr[k]:v for k,v in cells(r).items()}
    oid=c['Номер заказа']
    if oid not in orders:
        orders[oid]={'id':oid,'d':str(base+datetime.timedelta(int(float(c['Дата заказа'])))),
          's':1 if c['Статус']=='доставлен' else 0,'c':hm(c.get('Создан, время')),'t':hm(c.get('Доставлен, время')),'i':[]}
    q=int(float(c['Количество товаров']))
    orders[oid]['i'].append([c['Название позиции'],c['Категория'],float(c['Цена без скидки']),float(c['Цена со скидкой']),q])
pos=list(csv.reader(open(P+"items/positions.csv",encoding='utf-8-sig'),delimiter=';'))[1:]
img={p[1]:p[3] for p in pos}
o=sorted(orders.values(),key=lambda x:(x['d'],x['c'] or 0))
print(len(o), sum(1 for x in o if x['t'] is None and x['s']), sum(1 for x in o if x['t'] is not None and not x['s']))
open(P+"data.js","w").write("window.ORDERS="+json.dumps(o,ensure_ascii=False,separators=(',',':'))+";\nwindow.ITEM_IMAGES="+json.dumps(img,ensure_ascii=False,separators=(',',':'))+";\n")
