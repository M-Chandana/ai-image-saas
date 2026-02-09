import time
import json
import redis
import os
import csv
import tempfile
import psycopg2

from ultralytics import YOLO
from minio import Minio
import cv2


# ================= REDIS =================

REDIS_HOST = os.getenv("REDIS_HOST", "ai-redis")
REDIS_PORT = 6379

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True
)


# ================= MINIO =================

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "ai-minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")

BUCKET = "images"

minio = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)


# ================= DATABASE =================

DB_HOST = os.getenv("POSTGRES_HOST", "ai-db")
DB_PORT = 5432
DB_NAME = os.getenv("POSTGRES_DB", "ai_saas")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")


def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


# ================= YOLO =================

print("Loading YOLO model...")
model = YOLO("yolov8n.pt")
print("YOLO loaded ✅")


# ================= JOB PROCESSOR =================

def process_job(job_data):

    job = json.loads(job_data)

    job_id = job["job_id"]
    user_id = job["user_id"]
    object_name = job["file"]

    print(f"Processing job {job_id}")


    # -------- Validate Extension --------

    allowed_ext = ["jpg", "jpeg", "png"]

    ext = object_name.rsplit(".", 1)[-1].lower()

    if ext not in allowed_ext:
        raise Exception(
            f"Invalid file type: .{ext}. Only JPG and PNG allowed."
        )


    base = object_name.rsplit(".", 1)[0]


    # -------- Download image --------

    tmp_img = tempfile.NamedTemporaryFile(
        delete=False,
        suffix="." + ext
    )

    minio.fget_object(
        BUCKET,
        object_name,
        tmp_img.name
    )


    # -------- Run YOLO --------

    print("Running YOLO...")
    results = model(tmp_img.name)


    # -------- Load image --------

    img = cv2.imread(tmp_img.name)

    if img is None:
        raise Exception("Failed to read image")


    # -------- Prepare CSV --------

    tmp_csv = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".csv",
        mode="w",
        newline=""
    )

    writer = csv.writer(tmp_csv)

    writer.writerow([
        "label",
        "confidence",
        "x1",
        "y1",
        "x2",
        "y2"
    ])


    # -------- Draw + Save CSV --------

    for r in results:

        for box in r.boxes:

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            cls = int(box.cls[0])

            label = model.names[cls]


            # Draw box
            cv2.rectangle(
                img,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            # Label
            cv2.putText(
                img,
                f"{label} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )


            # CSV row
            writer.writerow([
                label,
                round(conf, 3),
                x1,
                y1,
                x2,
                y2
            ])


    tmp_csv.close()


    # -------- Save overlay --------

    overlay_file = tmp_img.name.rsplit(".", 1)[0] + "_overlay." + ext

    cv2.imwrite(overlay_file, img)


    # -------- Upload outputs --------

    overlay_name = base + "_overlay." + ext
    csv_name = base + "_results.csv"

    minio.fput_object(BUCKET, overlay_name, overlay_file)
    minio.fput_object(BUCKET, csv_name, tmp_csv.name)


    # -------- Update DB --------

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE jobs
        SET
            status = %s,
            overlay_path = %s,
            csv_path = %s,
            updated_at = NOW()
        WHERE id = %s
        """,
        (
            "succeeded",
            overlay_name,
            csv_name,
            job_id
        )
    )

    conn.commit()

    cur.close()
    conn.close()

    print(f"Job {job_id} completed ✅")


    # -------- Cleanup --------

    os.remove(tmp_img.name)
    os.remove(tmp_csv.name)
    os.remove(overlay_file)



# ================= MAIN LOOP =================

print("Worker started... Waiting for jobs 🚀")


while True:

    job = r.blpop("jobs_queue")

    if job:

        _, data = job

        try:

            process_job(data)

        except Exception as e:

            print("Job failed ❌", e)

    time.sleep(1)
