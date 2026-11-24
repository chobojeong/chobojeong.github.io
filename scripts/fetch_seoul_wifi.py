import os
import csv
import time
import urllib.request
import urllib.parse
import json

API_KEY = os.environ.get("SEOUL_API_KEY", "").strip()
SERVICE_NAME = "TbPublicWifiInfo"
BATCH_SIZE = 1000
OUTPUT_FILE = "seoul_wifi.csv"

COLUMNS = [
    ("X_SWIFI_MGR_NO", "관리번호"),
    ("X_SWIFI_WRDOFC", "자치구"),
    ("X_SWIFI_MAIN_NM", "와이파이명"),
    ("X_SWIFI_ADRES1", "도로명주소"),
    ("X_SWIFI_ADRES2", "상세주소"),
    ("X_SWIFI_INSTL_FLOOR", "설치위치(층)"),
    ("X_SWIFI_INSTL_TY", "설치유형"),
    ("X_SWIFI_INSTL_MBY", "설치기관"),
    ("X_SWIFI_SVC_SE", "서비스구분"),
    ("X_SWIFI_CMCWR", "망종류"),
    ("X_SWIFI_CNSTC_YEAR", "설치년도"),
    ("X_SWIFI_INOUT_DOOR", "실내외구분"),
    ("X_SWIFI_REMARS3", "WIFI접속환경"),
    ("LAT", "Y좌표"),
    ("LNT", "X좌표"),
    ("WORK_DTTM", "작업일자"),
]


def fetch_batch(start_idx: int, end_idx: int) -> dict:
    encoded_key = urllib.parse.quote(API_KEY)
    url = f"http://openapi.seoul.go.kr:8088/{encoded_key}/json/{SERVICE_NAME}/{start_idx}/{end_idx}/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw)


def main():
    if not API_KEY:
        raise RuntimeError("환경변수 SEOUL_API_KEY가 설정되지 않았습니다.")

    first_data = fetch_batch(1, 5)
    if SERVICE_NAME not in first_data:
        raise RuntimeError(f"API 응답 오류: {first_data}")

    total_count = int(first_data[SERVICE_NAME]["list_total_count"])
    print(f"전체 데이터 건수: {total_count:,}건")

    all_rows = []
    for start in range(1, total_count + 1, BATCH_SIZE):
        end = min(start + BATCH_SIZE - 1, total_count)
        for attempt in range(3):
            try:
                data = fetch_batch(start, end)
                rows = data.get(SERVICE_NAME, {}).get("row", [])
                all_rows.extend(rows)
                print(f"수집 완료: {start:,} ~ {end:,} ({len(all_rows):,}/{total_count:,})")
                break
            except Exception as e:
                print(f"재시도 ({attempt + 1}/3) [{start}~{end}]: {e}")
                time.sleep(2)
        else:
            raise RuntimeError(f"구간 [{start}~{end}] 수집 실패")

    if len(all_rows) == 0:
        raise RuntimeError("수집된 데이터가 0건입니다. 기존 파일을 덮어쓰지 않고 종료합니다.")

    # UTF-8 BOM 형식으로 저장 (엑셀 및 웹 브라우저 모두 호환)
    with open(OUTPUT_FILE, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([col[1] for col in COLUMNS])
        for row in all_rows:
            writer.writerow([str(row.get(col[0], "")).strip() for col in COLUMNS])

    print(f"저장 완료: {OUTPUT_FILE} (총 {len(all_rows):,}행)")


if __name__ == "__main__":
    main()
