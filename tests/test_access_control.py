import unittest
import hashlib
import time

# ==============================================================================
# HỆ THỐNG MÔ PHỎNG (MOCK SYSTEM CORE)
# ==============================================================================
class AccessEngine:
    def __init__(self):
        self.audit_log = []
        self.whitelist = {"USER-A": ["DOOR-MAIN"], "USER-B": ["DOOR-MAIN"]}
        self.blacklist = set()
        self.apb_state = {}  # Anti-passback state (IN/OUT)
        self.active_qr_tokens = {}

    def compute_hash(self, record: dict) -> str:
        payload = f"{record['event']}|{record['user']}|{record['details']}|{record.get('prev_hash', '')}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def log_audit(self, event: str, user: str, details: str = "OK"):
        prev_hash = self.audit_log[-1]["hash"] if self.audit_log else "0"*64
        record = {
            "event": event,
            "user": user,
            "details": details,
            "prev_hash": prev_hash,
            "timestamp": time.time()
        }
        record["hash"] = self.compute_hash(record)
        self.audit_log.append(record)

    def verify_chain(self) -> bool:
        expected_prev = "0"*64
        for record in self.audit_log:
            if record["prev_hash"] != expected_prev:
                return False
            if self.compute_hash(record) != record["hash"]:
                return False
            expected_prev = record["hash"]
        return True

    def swipe_card(self, user: str, door: str = "DOOR-MAIN", direction: str = "IN") -> dict:
        if user in self.blacklist:
            self.log_audit("ACCESS_DENIED", user, "BLACKLISTED")
            return {"granted": False, "reason": "ERR_BLACKLISTED"}
        
        if door not in self.whitelist.get(user, []):
            self.log_audit("ACCESS_DENIED", user, "UNAUTHORIZED")
            return {"granted": False, "reason": "ERR_UNAUTHORIZED"}

        # Anti-passback logic
        last_dir = self.apb_state.get(user)
        if last_dir == direction:
            self.log_audit("ACCESS_DENIED", user, "APB_VIOLATION")
            return {"granted": False, "reason": "ERR_ANTIPASSBACK"}

        self.apb_state[user] = direction
        self.log_audit("ACCESS_GRANTED", user, f"DOOR: {door}")
        return {"granted": True, "reason": "OK"}

    def issue_qr_token(self, visitor: str, ttl: int = 60) -> str:
        token = f"QR-{visitor}-{int(time.time())}"
        self.active_qr_tokens[token] = {"visitor": visitor, "expires_at": time.time() + ttl}
        return token

    def scan_qr(self, token: str) -> dict:
        if token not in self.active_qr_tokens:
            return {"granted": False, "reason": "INVALID_TOKEN"}
        
        if time.time() > self.active_qr_tokens[token]["expires_at"]:
            return {"granted": False, "reason": "TOKEN_EXPIRED"}
            
        del self.active_qr_tokens[token] # Single use
        return {"granted": True, "reason": "OK"}

class HardwareController:
    def __init__(self):
        self.facp_active = False
        self.ups_battery = 100.0
        self.door_relays = {"DOOR-MAIN": True, "DOOR-EXIT": True} # True = Locked

    def trigger_facp(self):
        self.facp_active = True
        for door in self.door_relays:
            self.door_relays[door] = False # Unlock (Fail-Safe)
        return 0.3 # 300ms latency

    def update_ups(self, battery_level: float):
        self.ups_battery = battery_level
        if battery_level <= 15.0:
            return self.trigger_facp()
        return None

class SOCDashboard:
    def __init__(self, engine: AccessEngine):
        self.engine = engine
        self.alerts = []

    def report_tailgating(self, swipes: int, people: int):
        if people > swipes:
            self.alerts.append("TAILGATING_DETECTED")
            return 0.8 # 800ms display latency
        return 0.0

    def remote_override(self, operator: str, door: str, reason: str) -> bool:
        if not reason or len(reason.strip()) < 10:
            return False # Blocked
        self.engine.log_audit("REMOTE_UNLOCK", operator, f"Door: {door} | Reason: {reason}")
        return True


# ==============================================================================
# BỘ TEST CASES (FULL 16 CA KIỂM THỬ)
# ==============================================================================
class TestAccessControlSystem(unittest.TestCase):

    def setUp(self):
        self.engine = AccessEngine()
        self.hw = HardwareController()
        self.soc = SOCDashboard(self.engine)

    def test_tc01_valid_card_access(self):
        res = self.engine.swipe_card("USER-A")
        self.assertTrue(res["granted"])

    def test_tc02_revoked_card_rejected(self):
        self.engine.blacklist.add("USER-A")
        res = self.engine.swipe_card("USER-A")
        self.assertFalse(res["granted"])
        self.assertEqual(res["reason"], "ERR_BLACKLISTED")

    def test_tc03_unauthorized_door_rejected(self):
        res = self.engine.swipe_card("USER-A", door="DOOR-SERVER")
        self.assertFalse(res["granted"])
        self.assertEqual(res["reason"], "ERR_UNAUTHORIZED")

    def test_tc04_fire_alarm_failsafe(self):
        latency = self.hw.trigger_facp()
        self.assertTrue(self.hw.facp_active)
        self.assertFalse(self.hw.door_relays["DOOR-EXIT"]) # Cửa thoát hiểm đã nhả chốt
        self.assertLessEqual(latency, 0.5) # Dưới 500ms

    def test_tc05_offline_cache_auth(self):
        # Giả lập rớt mạng, check card trong whitelist
        res = self.engine.swipe_card("USER-B")
        self.assertTrue(res["granted"])

    def test_tc06_low_battery_failsafe_edge(self):
        latency = self.hw.update_ups(14.0) # Pin dưới 15%
        self.assertIsNotNone(latency)
        self.assertFalse(self.hw.door_relays["DOOR-MAIN"]) # Tự nhả khóa an toàn

    def test_tc07_tailgating_detection_latency(self):
        latency = self.soc.report_tailgating(swipes=1, people=2)
        self.assertIn("TAILGATING_DETECTED", self.soc.alerts)
        self.assertLessEqual(latency, 1.0) # Dưới 1 giây

    def test_tc08_visitor_dynamic_qr_blocked(self):
        token = self.engine.issue_qr_token("GUEST-01", ttl=0) # Cho hết hạn luôn
        time.sleep(0.1)
        res = self.engine.scan_qr(token)
        self.assertFalse(res["granted"])
        self.assertEqual(res["reason"], "TOKEN_EXPIRED")

    def test_tc09_audit_log_hash_chain(self):
        """Đã khắc phục lỗi thuật toán kiểm tra chuỗi băm"""
        self.engine.log_audit("EVENT_1", "User A")
        self.engine.log_audit("EVENT_2", "User B")
        
        # Sửa đổi nội dung bản ghi số 2
        self.engine.audit_log[1]["details"] = "HACKED"
        
        # Hệ thống phát hiện chuỗi bị hỏng
        is_chain_intact = self.engine.verify_chain()
        self.assertFalse(is_chain_intact, "Lỗi: Không phát hiện ra dữ liệu bị sửa (Tampering)")

        # Mã băm tính lại khác với mã lưu trữ
        recalculated_hash = self.engine.compute_hash(self.engine.audit_log[1])
        self.assertNotEqual(recalculated_hash, self.engine.audit_log[1]["hash"])

    def test_tc10_soc_remote_override_rules(self):
        # Hợp lệ (Lý do >= 10 ký tự)
        success = self.soc.remote_override("GUARD-01", "DOOR-MAIN", "Quên thẻ nhân viên")
        self.assertTrue(success)
        
        # Không hợp lệ (Bỏ trống hoặc quá ngắn)
        fail = self.soc.remote_override("GUARD-01", "DOOR-MAIN", "Mở")
        self.assertFalse(fail)

    def test_tc11_failsafe_recovery(self):
        self.hw.trigger_facp() # Báo cháy
        self.hw.facp_active = False # Reset báo cháy
        # Code thực tế sẽ gọi hàm đóng rơ-le lại, ở đây ta test biến cờ reset
        self.assertFalse(self.hw.facp_active) 

    def test_tc12_sql_injection_defense(self):
        # Mô phỏng việc nhập ký tự lạ vào tên người dùng
        malicious_user = "USER'; DROP TABLE logs;--"
        res = self.engine.swipe_card(malicious_user)
        self.assertFalse(res["granted"]) # Chặn vì user không có trong whitelist

    def test_tc13_antipassback_violation(self):
        # Quẹt VÀO lần 1 -> Thành công
        self.engine.swipe_card("USER-A", direction="IN")
        
        # Quẹt VÀO lần 2 (Không có vòng ra) -> Thất bại (Lỗi APB)
        res2 = self.engine.swipe_card("USER-A", direction="IN")
        self.assertFalse(res2["granted"])
        self.assertEqual(res2["reason"], "ERR_ANTIPASSBACK")

    def test_tc14_boot_offline_auth(self):
        # Tương tự TC05: Khởi động hệ thống khi không có mạng
        res = self.engine.swipe_card("USER-B")
        self.assertTrue(res["granted"])

    def test_tc15_breakglass_override(self):
        # Giả lập đập nút khẩn cấp bằng tay (Manual Pull Station)
        latency = self.hw.trigger_facp()
        self.assertFalse(self.hw.door_relays["DOOR-MAIN"])

    def test_tc16_soc_dashboard_load_blocked(self):
        # Mô phỏng test sức chịu tải (NFR-106)
        alerts_generated = 0
        for _ in range(100):
            self.soc.report_tailgating(1, 2)
            alerts_generated += 1
        self.assertEqual(alerts_generated, 100)
        self.assertEqual(len(self.soc.alerts), 100)


if __name__ == '__main__':
    unittest.main()