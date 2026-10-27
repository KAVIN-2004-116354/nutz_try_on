import time
import mlflow
from zenml import pipeline, step

@step
def virtual_tryon_step(person_image_path: str, garment_image_path: str) -> str:
    """ZenML step to execute and track the virtual try-on workflow."""
    start_time = time.time()
    
    # Connect directly to your local MLflow Docker container
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("virtual-tryon-production")
    
    with mlflow.start_run(run_name="zenml_catvton_pipeline"):
        mlflow.log_param("person_image", person_image_path)
        mlflow.log_param("garment_image", garment_image_path)
        
        try:
            print(f"Running virtual try-on pipeline for {person_image_path} and {garment_image_path}...")
            time.sleep(1.5) # Simulated generation time
            
            latency = time.time() - start_time
            
            # Log performance metrics
            mlflow.log_metric("inference_latency_seconds", latency)
            mlflow.log_metric("pipeline_success", 1)
            
            output_path = "/home/lenovo/ComfyUI/output/ComfyUI_00001.png"
            return output_path
            
        except Exception as e:
            mlflow.log_metric("pipeline_success", 0)
            mlflow.log_param("error_message", str(e))
            raise e

@pipeline
def virtual_tryon_pipeline(person_img: str, garment_img: str):
    virtual_tryon_step(person_image_path=person_img, garment_image_path=garment_img)

if __name__ == "__main__":
    virtual_tryon_pipeline(
        person_img="person_1.jpg",
        garment_img="garment_1.jpg"
    )
