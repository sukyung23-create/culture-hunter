import csv

files = [
    "서울시 문화행사 정보.csv",
    "전국공연행사정보표준데이터.csv",
    "전국문화축제표준데이터.csv"
]

encodings = ["utf-8", "cp949", "euc-kr", "utf-8-sig"]

with open("inspect_result.txt", "w", encoding="utf-8") as out:
    for f in files:
        out.write(f"=== File: {f} ===\n")
        success = False
        for enc in encodings:
            try:
                with open(f, mode="r", encoding=enc) as file:
                    reader = csv.reader(file)
                    headers = next(reader)
                    row1 = next(reader, None)
                    out.write(f"Successfully read with encoding: {enc}\n")
                    out.write(f"Headers: {headers}\n")
                    if row1:
                        out.write(f"Sample Row: {row1}\n")
                    out.write(f"Total columns: {len(headers)}\n")
                    success = True
                    break
            except Exception as e:
                continue
        if not success:
            out.write(f"Failed to read file {f} with standard encodings\n")
        out.write("-" * 50 + "\n")

