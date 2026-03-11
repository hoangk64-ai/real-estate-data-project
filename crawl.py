import requests
import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import time
import random

# ==========================================
# 1. HÀM HỖ TRỢ
# ==========================================

def clean_text(text):
    if text:
        return text.replace("\n"," ").replace("\r","").strip()
    return ""

def export_to_sqlite(df, db_name="real_estate_dn_qn.db"):

    conn = sqlite3.connect(db_name)

    df.to_sql(
        "real_estate",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    print(f" Đã lưu {len(df)} bản ghi vào database: {db_name}")

# ==========================================
# 2. CRAWL BATDONGSAN.COM.VN
# ==========================================

def crawl_batdongsan(url, province, pages=5):

    data = []

    print(f"\n[*] Crawl Batdongsan {province}")

    scraper = cloudscraper.create_scraper()

    for page in range(1,pages+1):

        if page==1:
            page_url = url
        else:
            page_url = f"{url}/p{page}"

        print("Trang",page)

        try:

            r = scraper.get(page_url)

            soup = BeautifulSoup(r.text,"html.parser")

            listings = soup.select(".js__card")

            for item in listings:

                try:

                    title = item.select_one(".js__card-title")

                    price = item.select_one(".re__card-config-price")

                    area = item.select_one(".re__card-config-area")

                    location = item.select_one(".re__card-location")

                    link = item.find("a")

                    url_detail = "https://batdongsan.com.vn"+link["href"]

                    data.append({

                        "nguon":"Batdongsan",

                        "tinh_thanh":province,

                        "tieu_de":clean_text(title.text if title else ""),

                        "gia":clean_text(price.text if price else ""),

                        "dien_tich":clean_text(area.text if area else ""),

                        "vi_tri":clean_text(location.text if location else ""),

                        "url":url_detail

                    })

                except:
                    pass

        except:
            pass

        time.sleep(random.uniform(2,4))

    print("Thu thập:",len(data))

    return data


# ==========================================
# 3. CRAWL CHOTOT API
# ==========================================

def crawl_chotot(region_code, province, pages=5):

    data=[]

    print(f"\n[*] Crawl Chotot {province}")

    headers={
        "User-Agent":"Mozilla/5.0"
    }

    for page in range(pages):

        offset = page*20

        url="https://gateway.chotot.com/v1/public/ad-listing"

        params={
            "region_v2":region_code,
            "cg":1000,
            "limit":20,
            "o":offset
        }

        try:

            r=requests.get(url,params=params,headers=headers)

            ads=r.json()["ads"]

            for ad in ads:

                title=ad.get("subject","")

                price=ad.get("price_string","")

                area=ad.get("size","")

                list_id=str(ad.get("list_id",""))

                link="https://www.chotot.com/"+list_id

                data.append({

                    "nguon":"Chotot",

                    "tinh_thanh":province,

                    "tieu_de":title,

                    "gia":price,

                    "dien_tich":area,

                    "vi_tri":province,

                    "url":link

                })

        except:
            pass

        time.sleep(random.uniform(2,4))

    print("Thu thập:",len(data))

    return data


# ==========================================
# 4. CHẠY CHƯƠNG TRÌNH
# ==========================================

if __name__=="__main__":

    print("START CRAWLING")

    # Batdongsan
    bds_dn = crawl_batdongsan(
        "https://batdongsan.com.vn/nha-dat-ban-da-nang",
        "Đà Nẵng",
        pages=20
    )

    bds_qn = crawl_batdongsan(
        "https://batdongsan.com.vn/nha-dat-ban-quang-nam",
        "Quảng Nam",
        pages=20
    )


    # Chotot
    chotot_dn = crawl_chotot(
        "13000",
        "Đà Nẵng",
        pages=20
    )

    chotot_qn = crawl_chotot(
        "13000",
        "Quảng Nam",
        pages=20
    )


    # Gộp dữ liệu
    all_data = bds_dn + bds_qn + chotot_dn + chotot_qn


    df = pd.DataFrame(all_data)

    df = df.drop_duplicates(subset=["tieu_de","url"])

    print("\nTổng dữ liệu:",len(df))


    # Xuất database
    export_to_sqlite(df)


    print(" DONE")
