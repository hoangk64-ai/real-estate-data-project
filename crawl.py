import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import time
import random

# --- CÁC HÀM HỖ TRỢ ---
def clean_text(text):
    """Làm sạch khoảng trắng thừa trong chuỗi. Thay N/A thành Không có."""
    if text:
        # Xóa dấu xuống dòng để dữ liệu DB trên một hàng đẹp mắt hơn
        return text.replace('\n', ' ').replace('\r', '').strip()
    return 'Không có'

def get_fresh_scraper():
    """Khởi tạo scraper mới để thay đổi nhân dạng, tránh bị block."""
    return cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )

# --- HÀM CRAWL CHÍNH ---
def crawl_batdongsan_pro(location_url, province_name, max_pages=15):
    data_collected = []
    print(f"\n[*] BẮT ĐẦU THU THẬP TẠI {province_name.upper()} (Tối đa {max_pages} trang)")
    scraper = get_fresh_scraper()

    for page in range(1, max_pages + 1):
        print(f"  -> Đang xử lý trang {page}/{max_pages}...")
        url = f"{location_url}/p{page}" if page > 1 else location_url
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"     [!] Thử lại lần {attempt}/{max_retries - 1}...")
                    scraper = get_fresh_scraper()
                    time.sleep(random.uniform(5, 10))

                response = scraper.get(url, timeout=20)
                
                if response.status_code != 200:
                    if response.status_code == 403 and attempt < max_retries - 1:
                        continue 
                    else:
                        break 
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Quét rộng hơn để tóm được mọi cấu trúc thẻ chứa bài đăng
                listings = soup.select('.re__card-info, .re__card-info-content, .js__card')
                
                if not listings:
                    break
                
                for item in listings:
                    try:
                        # 1. Lấy Tiêu đề
                        title = item.find(lambda tag: tag.name in ['h3', 'span'] and tag.get('class') and any('title' in c.lower() for c in tag.get('class')))
                        if not title:
                            continue # Nếu không có tiêu đề, bỏ qua vì đây có thể là thẻ quảng cáo rác
                        
                        # 2. Lấy Giá & Diện tích & Vị trí
                        price = item.find('span', class_=lambda c: c and 'price' in str(c).lower())
                        area = item.find('span', class_=lambda c: c and 'area' in str(c).lower())
                        location = item.find('div', class_=lambda c: c and 'location' in str(c).lower())
                        
                        # 3. [FIX LỖI MÔ TẢ]: Quét siêu rộng mọi thẻ có chứa từ khóa mô tả
                        desc = item.find(lambda tag: tag.name in ['div', 'span', 'p'] and tag.get('class') and any(keyword in str(c).lower() for c in tag.get('class') for keyword in ['description', 'summary']))
                        
                        # 4. [FIX LỖI URL]: Lấy đúng link gốc của từng bài đăng
                        link_tag = item.find('a', href=True)
                        specific_url = "https://batdongsan.com.vn" + link_tag['href'] if link_tag and link_tag['href'].startswith('/') else url

                        data_collected.append({
                            'tinh_thanh': province_name,
                            'tieu_de': clean_text(title.text),
                            'muc_gia': clean_text(price.text if price else ''),
                            'dien_tich': clean_text(area.text if area else ''),
                            'vi_tri': clean_text(location.text if location else ''),
                            'mo_ta': clean_text(desc.text if desc else ''),
                            'url': specific_url
                        })
                    except Exception:
                        pass
                
                break # Thành công thì thoát vòng lặp retry
            except Exception:
                pass
        
        time.sleep(random.uniform(3, 6))

    print(f"[*] Đã thu thập {len(data_collected)} bản ghi tại {province_name}.")
    return data_collected


# --- HÀM XUẤT DATABASE SQLITE DUY NHẤT ---
def export_to_sql_only(df, db_name="real_estate_danang_quangnam.db", table_name="bds_data"):
    """Lưu DataFrame trực tiếp vào file SQLite database."""
    try:
        conn = sqlite3.connect(db_name)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        print(f"  [+] Đã tạo và lưu dữ liệu vào DB SQL: {db_name} (Bảng: {table_name})")
    except Exception as e:
        print(f"  [!] Lỗi khi xuất ra SQL Database: {e}")


# --- KHỐI LỆNH THỰC THI CHÍNH ---
if __name__ == "__main__":
    url_dn = "https://batdongsan.com.vn/nha-dat-ban-da-nang"
    url_qn = "https://batdongsan.com.vn/nha-dat-ban-quang-nam"
    
    SO_TRANG = 15
    
    data_da_nang = crawl_batdongsan_pro(url_dn, "Đà Nẵng", max_pages=SO_TRANG)
    
    print("\n[Zzz] Đang nghỉ ngơi 15 giây để tránh bị chặn IP...")
    time.sleep(15)
    
    data_quang_nam = crawl_batdongsan_pro(url_qn, "Quảng Nam", max_pages=SO_TRANG)
    
    all_data = data_da_nang + data_quang_nam
    
    if all_data:
        # Lọc bỏ các dòng trùng lặp (nếu web đẩy tin lên nhiều lần)
        df = pd.DataFrame(all_data).drop_duplicates(subset=['tinh_thanh', 'tieu_de', 'muc_gia', 'dien_tich', 'vi_tri', 'mo_ta', 'url'])
        
        print("\n" + "=" * 60)
        print("HOÀN THÀNH THU THẬP - CHỈ XUẤT FILE DB...")
        
        db_filename = "real_estate_danang_quangnam.db"
        export_to_sql_only(df, db_name=db_filename, table_name="bds_data")
        
        print("\n=> TẤT CẢ ĐÃ HOÀN TẤT TRỌN VẸN!")
        print("=" * 60)
    else:
        print("\nKhông có dữ liệu nào được thu thập.")
