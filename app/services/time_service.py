import ntplib
from datetime import datetime, timedelta

class TimeService:
    _instance = None
    _offset = timedelta(seconds=0)
    _is_synced = False

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def sync_time(self):
        """Menghubungi server NTP internet untuk menghitung selisih waktu dengan mesin lokal."""
        try:
            client = ntplib.NTPClient()
            # Kita gunakan server NTP indonesia untuk ping yang cepat
            response = client.request('id.pool.ntp.org', version=3, timeout=3)
            ntp_time = datetime.fromtimestamp(response.tx_time)
            local_time = datetime.now()
            
            # Hitung seberapa melenceng jam di laptop/VM ini
            self._offset = ntp_time - local_time
            self._is_synced = True
            print(f"NTP Sync Success! Offset: {self._offset.total_seconds():.2f} detik.")
        except Exception as e:
            print(f"Gagal menghubungi server NTP (Offline). Fallback ke jam lokal. Error: {e}")
            self._is_synced = False
            self._offset = timedelta(seconds=0)

    def get_current_time(self) -> datetime:
        """Mengambil waktu saat ini (sudah dikoreksi dengan offset NTP jika ada internet)"""
        return datetime.now() + self._offset
