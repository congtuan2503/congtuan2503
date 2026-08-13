# Hướng dẫn setup

## 1. Tạo repo "profile README" (bắt buộc phải đúng tên)

1. Vào GitHub, tạo repo mới tên **chính xác** là `congtuan2503` (trùng username) — GitHub sẽ tự nhận đây là repo đặc biệt và hiển thị `README.md` của nó ngay trên trang profile.
2. Repo phải để **Public**.
3. Copy toàn bộ các file trong thư mục này vào repo đó, giữ nguyên cấu trúc:

```
congtuan2503/
├── README.md
├── activity_log.json
├── activity_log.example.json
├── generate_heatmap.py
├── log_activity.py
├── assets/
│   └── activity_heatmap.svg
└── .github/workflows/
    ├── update-heatmap.yml
    └── log-activity.yml
```

4. Commit + push. Sau vài phút, vào lại `github.com/congtuan2503` để xem kết quả (một số badge như stats card, streak stats cần vài giây load).

## 2. Cách log hoạt động KC7 / LetsDefend

### Cách nhanh nhất: bấm nút trên GitHub (kể cả trên điện thoại)

Không cần mở file, không cần gõ JSON:

1. Vào repo trên GitHub (web hoặc app) → tab **Actions** → chọn workflow **"Log activity"** → **Run workflow**.
2. Chọn `platform` (`kc7` hoặc `letsdefend`), điền `count` (mấy case/alert hôm đó), `note` nếu muốn.
3. Ô `date`: để trống nếu log cho hôm nay, hoặc điền `YYYY-MM-DD` (vd `2026-08-01`) nếu muốn **thêm bù cho ngày trước đó**.
4. Bấm **Run workflow**. Xong — nó tự thêm dòng vào `activity_log.json`, tự vẽ lại heatmap, tự commit. Mất khoảng 10-15 giây để chạy xong, F5 lại trang profile là thấy.

Muốn bù nhiều ngày liền thì chạy lại workflow nhiều lần, mỗi lần đổi `date` khác nhau.

Đây là cách mình khuyên dùng hằng ngày vì gần như 1-chạm, làm được cả trên điện thoại qua app GitHub, và **không cần đăng nhập hộ vào KC7/LetsDefend** nên không có rủi ro lộ tài khoản.

### Cách 2: chạy lệnh khi đang ở máy tính

```bash
python3 log_activity.py kc7
python3 log_activity.py letsdefend 2 "SOC101 alert triage"
python3 log_activity.py kc7 1 "backfill" --date 2026-08-01
git add activity_log.json && git commit -m "log activity" && git push
```
Push xong thì workflow `update-heatmap.yml` sẽ tự vẽ lại heatmap.

### Cách 3: sửa tay `activity_log.json`

Vẫn dùng được khi cần thêm nhiều dòng cùng lúc (vd nhập bù cả tuần), theo mẫu trong `activity_log.example.json`:

```json
{"date": "2026-08-13", "platform": "kc7", "count": 1, "note": "Solved: ..."}
```

- `date`: `YYYY-MM-DD` · `platform`: `"kc7"` hoặc `"letsdefend"` · `count`: số case (mặc định 1, không bắt buộc) · `note`: ghi chú riêng, không bắt buộc, không hiển thị lên ảnh.

Dù dùng cách nào, `update-heatmap.yml` cũng tự chạy lại mỗi thứ Hai kể cả không có commit mới, để "current streak" không bị lỗi thời.

### Vì sao không auto 100% được?

KC7 chặn crawl tự động qua robots.txt, còn LetsDefend không có API công khai — để "tự lấy dữ liệu" thật sự sẽ cần lưu mật khẩu/session của bạn làm secret trên GitHub Action, chạy định kỳ đăng nhập hộ. Rủi ro lộ tài khoản và dễ hỏng khi họ đổi giao diện, nên mình không build phần đó. Nút bấm ở Cách 1 là điểm cân bằng tốt nhất: không cần thêm bước "mở file, gõ JSON, tự nhớ cú pháp", nhưng vẫn không đụng đến tài khoản của 2 platform kia.

## 3. Vì sao không tự động kéo dữ liệu từ KC7/LetsDefend?

Cả hai đều không có API hay badge công khai để nhúng, và trang KC7 chặn truy cập tự động (robots.txt) nên việc viết script tự đăng nhập/scrape sẽ vi phạm điều khoản sử dụng — mình không làm hộ phần đó. Cách log tay tuy tốn 10 giây mỗi lần nhưng chắc chắn, không phụ thuộc vào việc các trang đó thay đổi giao diện hay chặn bot.

## 4. Tuỳ chỉnh thêm

- Đổi tông màu banner/heatmap: sửa `color=` trong link `capsule-render` (README) và các mã màu trong `LEVEL_COLORS` (`generate_heatmap.py`).
- Đổi nội dung giới thiệu, tech stack: sửa trực tiếp trong `README.md`.
- Muốn thêm nền tảng thứ 3 (vd TryHackMe): chỉ cần dùng `platform` mới trong log, sửa `PLATFORM_COLORS` và dòng thống kê trong `generate_heatmap.py`.
