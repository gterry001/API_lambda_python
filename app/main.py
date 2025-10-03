import json, boto3, traceback
from .logic import run_portfolio_analysis , prepare_dashboard_data
import pandas as pd

s3 = boto3.client("s3")
BUCKET_NAME = "fastapi-bucket-project"  # 👈 cámbialo

def handler(event, context):
    for record in event["Records"]:
        try:
            body = json.loads(record["body"])
            job_id = body["job_id"]

            print(f"👉 Procesando job {job_id}")

            # Ejecuta tu análisis
            result = run_portfolio_analysis()
            # Generar datos para dashboard
            print(result)
            portfolio = pd.DataFrame(result["portfolio"])
            df_betas = pd.DataFrame(result["df_betas"])
            print(portfolio)
            dashboard_data = prepare_dashboard_data(portfolio, df_betas)
            
            # Guardar resultado en S3
            s3.put_object(
                Bucket=BUCKET_NAME,
                Key=f"jobs/{job_id}.json",
                Body=json.dumps({"status": "done", "result": dashboard_data}).encode("utf-8"),
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
