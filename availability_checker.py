import asyncio
import aiohttp
from bs4 import BeautifulSoup
from pymongo import MongoClient


class AvailabilityChecker:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @staticmethod
    async def check_item_availability(url):
        async with aiohttp.ClientSession(cookies=cookies) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    if 'immowelt' in url:
                        error_message = soup.find_all('sd-alertbox', class_='alertbox--is-shown')
                        if error_message:
                            print(f"Item with URL '{url}' is no longer available.")
                            return False
                    elif 'wg-gesucht' in url:
                        error_message = soup.find_all('div', class_='alert alert-with-icon alert-danger')
                        if error_message:
                            print(error_message)
                            print(f"Item with URL '{url}' is no longer available.")
                            return False
                        return 'wtf fdoghubkihudfijergjo -----------'
                    else:
                        print(f"Unsupported website for URL '{url}'.")
                else:
                    print(f"Error accessing URL '{url}'.")
        return True

    async def start_checking_availability(self):
        db_client = MongoClient(self.mongo_uri)
        db = db_client[self.mongo_db]

        items = db.listings.find({})
        tasks = []
        for item in items:
            url = item['url']
            tasks.append(asyncio.create_task(self.check_item_availability(url=url)))

        results = await asyncio.gather(*tasks)

        for item, is_available in zip(items, results):
            url = item['url']
            if not is_available:
                # Item is no longer available, remove it from the collection
                db.listings.delete_one({'url': url})
                print(f"Item with URL '{url}' has been removed from the collection.")

        db_client.close()


cookies = {
    "X-Client-Id":"wg_desktop_website",
    "sync_favourites":"False",
    "get_favourites":"False",
    "__cmpcpcx15144": "__1__",
    "__cmpcpc": "__1__",
    "__cmpconsentx15144": "CPsutDAPsutDAAfR4BDEDHCsAP_AAH_AAAYgG7pV9W5WTWFBOHp7arsEKYUX13TNQ2AiCgCAE6AAiHKAYIQGkmAYJASAIAACIBAgIBYBIQFAAEFEAAAAIIARAAFIAAAAIAAIIAIECAEQUkAAAAAIAAAAAAAAAAAEABAAgADAABIAAEAAAIAAAAAAAAgbulX1blZNYUE4entquwQphRfXdM1DYCIKAIAToACIcoBghAaSYBgkBIAgAAIgECAgFgEhAUAAQUQAAAAggBEAAUgAAAAgAAggAgQIARBSQAAAAAgAAAAAAAAAAAQAEACAAMAAEgAAQAAAgAAAAAAACAAA",
    "__cmpcvcx15144": "__s1227_s87_s343_s94_s40_s1052_s64_s335_s914_s762_s640_s102_s1469_s405_s1932_s65_s23_s209_s116_s25_s56_s123_s127_s570_s128_s7_s573_s482_s312_s1_s26_s2612_s135_s1409_s905_s10_s139_s161_s1442_s2_s974_s1049_s11_s322_s2386_s885_s879_s36_s1358_s267_s883_s1097_s2589_s76_c4566_s1341_s268_s460_s271_c13455_s292_s358_s190_s19_s653_s800_s12_s196_s1216_s52_s199_s34_s525_s32_s882_s739_s60_s21_c5169_s35_s30_s217_s574_s356_U__",
    "__cmpcvc": "__s1227_s87_s343_s94_s40_s1052_s64_s335_s914_s762_s640_s102_s1469_s405_s1932_s65_s23_s209_s116_s25_s56_s123_s127_s570_s128_s7_s573_s482_s312_s1_s26_s2612_s135_s1409_s905_s10_s139_s161_s1442_s2_s974_s1049_s11_s322_s2386_s885_s879_s36_s1358_s267_s883_s1097_s2589_s76_c4566_s1341_s268_s460_s271_c13455_s292_s358_s190_s19_s653_s800_s12_s196_s1216_s52_s199_s34_s525_s32_s882_s739_s60_s21_c5169_s35_s30_s217_s574_s356_U__",
    "__cmpiab": "_58_272_40_231_147_44_50_790_39_14_93_511_612_264_565_6_410_211_195_259_793_23_728_394_742_63_771_273_156_12_87_128_185_30_94_620_315_243_285_77_138_591_85_91_541_440_209_397_122_144_126_434_584_402_8_213_141_183_24_312_1_120_78_755_98_61_206_131_365_606_253_10_278_428_436_129_252_294_62_325_148_97_109_95_508_486_52_614_142_79_152_358_151_20_130_812_373_304_241_617_602_69_227_349_385_772_559_164_412_384_140_490_177_236_887_76_81_835_11_71_4_16_506_84_33_111_73_68_82_161_45_115_134_295_104_13_655_165_238_137_136_114_275_42_89_475_132_345_577_382_21_28_36_162_237_284_18_281_32_25_70_173_154_210_301_469_",
    "__cmpiabc": "__1_2_3_4_5_6_7_8_9_10_r1_r2_",
    "__cmpiabli": "_58_272_40_231_147_44_50_790_39_14_93_511_612_264_565_6_410_211_195_259_793_23_728_394_742_63_771_273_156_12_87_128_185_30_94_620_315_243_285_77_138_591_85_91_541_440_209_397_122_144_126_434_584_402_8_213_141_183_24_312_1_120_78_755_98_61_206_131_365_606_253_10_278_428_436_129_252_294_62_325_148_97_109_95_508_486_52_614_142_79_152_358_151_20_130_812_373_304_241_617_602_69_227_349_385_772_559_164_412_384_140_490_177_236_887_76_81_835_11_71_4_16_506_84_33_111_73_68_82_161_45_115_134_295_104_13_655_165_238_137_136_114_275_42_89_475_132_345_577_382_21_28_36_162_237_284_18_281_32_25_70_173_154_210_301_469_772_",
    "__cmpiabcli": "__2_3_4_5_6_7_8_9_10_"
}


mongo_uri = 'mongodb+srv://sunilh05:9rOjkTfQFdIDLgiH@cluster0.ddk23zz.mongodb.net/?retryWrites=true&w=majority'
mongo_db = 'EstateItems'
availability_checker = AvailabilityChecker(mongo_uri, mongo_db)


async def main():
    await availability_checker.start_checking_availability()

asyncio.run(main())
