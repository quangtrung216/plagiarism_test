import uvicorn
from api.pdf_upload_api import app

if __name__ == "__main__":
    print("Starting PDF Upload API with MinHash Integration...")
    print("API will be available at: http://localhost:8001")
    print("API Documentation: http://localhost:8001/docs")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )