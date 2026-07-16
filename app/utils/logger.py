import logging

# Setup sistem pencatatan error (log) agar kalau aplikasi error di komputer dokter, kita gampang mencarinya.
logging.basicConfig(
    filename='physioanx_app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("PhysioAnx")
