import json, boto3, traceback
from .logic import run_portfolio_analysis 

s3 = boto3.client("s3")
BUCKET_NAME = "fastapi-bucket-project"  # 👈 cámbialo

def handler(event, context):
    for record in event["Records"]:
        try:
            body = json.loads(record["body"])
            job_id = body["job_id"]

            print(f"👉 Procesando job {job_id}")

            # Ejecuta tu análisis
            result = run_portfolio_analysis(job_id)

            # Guardar resultado en S3
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=f"jobs/{job_id}.json",
                Body=json.dumps({"status": "done", "result": result}).encode("utf-8"),
                ContentType="application/json"
            )

            print(f"✅ Job {job_id} terminado")
        except Exception as e:
            print("❌ Error procesando job:", e)
            print(traceback.format_exc())
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=f"jobs/{job_id}.json",
                Body=json.dumps({"status": "error", "error": str(e)}).encode("utf-8"),
                ContentType="application/json"
            )
    return {"status": "ok"}
