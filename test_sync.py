import unittest,sys,pathlib,json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from sync import decode,rows_from_detail
class SyncTests(unittest.TestCase):
    def test_decode(self):
        payload={'Tour_Data':[{'Pattern_No':1}]}
        html='<script>self.__next_f.push('+json.dumps([1,'b:'+json.dumps(payload)])+')</script>'
        self.assertEqual(decode(html),[payload])
    def test_only_bookable_and_preserve_price(self):
        base={'Tour_Date':'2026/10/01','SignUp_Mark':True,'Available_Pax':'可售7','Retail_Price':'30888','Tour_Code':'TEST'}
        data={'itineraryData':{'Tour_Name':'測試','Tour_Days':'5','Itinerary_Info':{'Itinerary_Info_list':[{'SightInfoList':[{'Sight_Name':'景點（車經）'}]}]}},'itineraryByTourCode':{'Tour_Goday':{'TourMonthList':[{'Tour_Goday_list':[base,{**base,'Available_Pax':'候補2'},{**base,'SignUp_Mark':False},{**base,'App_Product_Mark':True}]}]}}}
        rows=rows_from_detail(data,{'Pattern_No':1,'Tour_Title':'測試'},'測試目的地','2026-09-19')
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['seats'],7);self.assertEqual(rows[0]['price'],'NT$ 30888 起／人');self.assertEqual(rows[0]['sights'],'景點（車經）')
    def test_schema_change_aborts(self):
        with self.assertRaises(ValueError):rows_from_detail({}, {'Pattern_No':1},'測試','2026-09-19')
if __name__=='__main__':unittest.main()
