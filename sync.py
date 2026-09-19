"""Read public itinerary pages, build a static snapshot. No credentials required."""
import json,re,time,urllib.request,urllib.parse,datetime,pathlib,os,html
ROOT=pathlib.Path(__file__).resolve().parents[1]

def decode(html):
    result=[]
    for m in re.finditer(r'self\.__next_f\.push\((\[.*?\])\)</script>',html,re.S):
        try:
            text=json.loads(m[1])[1]
            if isinstance(text,str): result.append(json.loads(text.split(':',1)[1]))
        except (ValueError,TypeError,IndexError): pass
    return result

def find(value,key):
    if isinstance(value,dict):
        if key in value:return value[key]
        for child in value.values():
            result=find(child,key)
            if result is not None:return result
    if isinstance(value,list):
        for child in value:
            result=find(child,key)
            if result is not None:return result

def patterns(value):
    if isinstance(value,dict):
        if value.get('Pattern_No') and value.get('Tour_Title'):yield value
        else:
            for child in value.values():yield from patterns(child)
    elif isinstance(value,list):
        for child in value:yield from patterns(child)

def rows_from_detail(data,pattern,destination,updated):
    info=find(data,'itineraryData')
    by=find(data,'itineraryByTourCode')
    if not isinstance(info,dict) or not isinstance(by,dict):raise ValueError('官網行程格式變動')
    months=by.get('Tour_Goday',{}).get('TourMonthList')
    if not isinstance(months,list):raise ValueError('缺少出發日期清單')
    sights='、'.join(str(s.get('Sight_Name','')) for d in info.get('Itinerary_Info',{}).get('Itinerary_Info_list',[]) for s in d.get('SightInfoList',[]))
    rows=[]
    for month in months:
        for d in month.get('Tour_Goday_list',[]):
            seat=re.fullmatch(r'可售\s*(\d+)',str(d.get('Available_Pax','')))
            if not seat or d.get('SignUp_Mark') is not True or d.get('App_Product_Mark'):continue
            date=str(d.get('Tour_Date','')).replace('/','-')
            datetime.date.fromisoformat(date)
            if date<updated:continue
            price=d.get('Retail_Price')
            rows.append(dict(title=info.get('Tour_Name') or pattern['Tour_Title'],destination=destination,date=date,days=int(info['Tour_Days']),seats=int(seat[1]),price=('NT$ '+str(price)+' 起／人') if price is not None else '',url='https://tour.colatour.com.tw/itinerary?PatternNo='+str(pattern['Pattern_No']),code=str(d.get('Tour_Code') or ''),departure=str(info.get('Departure_City') or ''),updated=updated,sights=sights))
    return rows

def main():
    cfg=json.loads((ROOT/'sync-config.json').read_text())
    if not 1<=cfg['maxPatternsPerDestination']<=40:raise ValueError('每個目的地上限需為 1–40')
    if not 1<=len(cfg['destinations'])<=12:raise ValueError('目的地數量需為 1–12')
    delay=max(1,float(cfg['requestDelaySeconds']))
    def page(url):
        time.sleep(delay)
        req=urllib.request.Request(url,headers={'User-Agent':'TravelAdvisorSnapshot/1.0','Accept':'text/html'})
        with urllib.request.urlopen(req,timeout=cfg['timeoutSeconds']) as response:
            raw=response.read(12_000_001)
            if len(raw)>12_000_000:raise ValueError('官網回應過大')
        return decode(raw.decode('utf-8'))
    now=datetime.datetime.now(datetime.timezone.utc)
    today=now.astimezone(datetime.timezone(datetime.timedelta(hours=8))).date().isoformat()
    collected={};checked=0;found=0;details={}
    # Any failure aborts publication. Previous successful Pages deployment remains online.
    for dest in cfg['destinations']:
        print('同步目的地：'+str(dest),flush=True)
        data=page('https://tour.colatour.com.tw/search?'+urllib.parse.urlencode({'KeyWord':dest}))
        groups=find(data,'Tour_Data')
        if not isinstance(groups,list):raise ValueError('搜尋資料格式變動：'+dest)
        unique={str(p['Pattern_No']):p for p in patterns(groups)}
        if not unique:raise ValueError('未取得任何候選行程：'+dest)
        found+=len(unique)
        for pid,p in list(unique.items())[:cfg['maxPatternsPerDestination']]:
            if pid not in details:
                details[pid]=page('https://tour.colatour.com.tw/itinerary?'+urllib.parse.urlencode({'PatternNo':pid}));checked+=1
            for row in rows_from_detail(details[pid],p,dest,today):
                key=(pid,row['date'],row['code'])
                if key in collected:
                    if dest not in collected[key]['destination'].split(' / '):collected[key]['destination']+=' / '+dest
                else:collected[key]=row
    rows=list(collected.values())
    if not rows:raise ValueError('沒有可用行程；保留上次已發布版本，請人工檢查')
    meta={'syncedAt':now.isoformat(),'destinations':cfg['destinations'],'checked':checked,'candidates':found,'rows':len(rows)}
    template=(ROOT/'web/template.html').read_text()
    payload=json.dumps(rows,ensure_ascii=False).replace('<','\\u003c')
    template=template.replace('<script id="embedded-data" type="application/json">[]</script>','<script id="embedded-data" type="application/json">'+payload+'</script>')
    template=template.replace('<!--SYNC_INFO-->', '官網同步時間（UTC）：'+meta['syncedAt']+'｜共 '+str(len(rows))+' 個出發團｜已核對 '+str(checked)+' 個行程。範圍：'+html.escape('、'.join(cfg['destinations'])))
    out=ROOT/'site';out.mkdir(exist_ok=True)
    (out/'index.html').write_text(template)
    (out/'snapshot.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
    sw=(ROOT/'web/sw.js').read_text().replace('__BUILD__',now.strftime('%Y%m%d%H%M%S'))
    (out/'sw.js').write_text(sw)
    (out/'.nojekyll').write_text('')
    print(json.dumps(meta,ensure_ascii=False))
if __name__=='__main__':main()
