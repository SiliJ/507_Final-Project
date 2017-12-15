import unittest
from SI507F17_finalproject.py import *

class Test1_datacaching(unittest.TestCase):
    def setUp(self):
        with open(CACHE_FNAME,'r') as cache_file:
                cache_json = cache_file.read()
                CACHE_DICTION = json.loads(cache_json)
        searchterm='sushi'
        yourplace='Chicago'
        foodfinder_url="https://api.yelp.com/v3/businesses/search"
        inquiry_param={}
        inquiry_param['term']=searchterm
        inquiry_param['location']=yourplace
        inquiry_param['limit']=50
        unique_ident=params_unique_combination(foodfinder_url,inquiry_param)
        business_list=CACHE_DICTION[unique_ident]['businesses']
        for item in business_list:
            Restaurants_object=Restaurant(item)
            idlist=Restaurants_object.get_restaurant_id()

    def test_01_uniqueident_Method(self):
        self.assertEqual(unique_ident,"https://api.yelp.com/v3/businesses/searchlocation-chicago_term-sushi")

    def test_02_Count_searchresults(self):
        self.assertEqual(len(business_list)>=20,True)

    def test_03_cachefile_type(self):
        self.assertEqual(type(item),type({"key":"answer"}))

    def test_04_class_getIDMethod(self):
        # idlist=Restaurants_object.get_restaurant_id()
        self.assertEqual("yuzu-sushi-and-robata-grill-chicago" in idlist,True)

    def test_05_class_containsmethod(self):
        self.assertEqual('sushi' in Restaurants_object.category,True)

    def test_06_class_locationverifer(self):
        addresslist=Restaurants_object.address()
        self.assertEqual("chicago" in addresslist,True)

    def test_07_calss_getdict_method(self):
        keylist=Restaurants_object.get_restaurant_dict().keys()
        self.assertEqual(keylist,['id','name','rating','review_count','distance','phone','address','category','transactions','price_range'])

    def test_08_hours_url(self):
        ID='yuzu-sushi-and-robata-grill-chicago'
        self.assertEqual(hoursURL,"https://api.yelp.com/v3/businesses/yuzu-sushi-and-robata-grill-chicago")

    def test_09_operationtimeDict(self):
        weekdaykeys=operation_time.keys()
        self.assertEqual(len(weekdaykeys),7)

    def tearDown(self):

# class Test2_database(unittest.TestCase):
#     def setUp(self):

        if __name__ == "__main__":
            unittest.main(verbosity=2)
