"""
Demo script for testing PDF upload API
"""

import requests
import json
import time
from pathlib import Path


def test_pdf_upload_api():
    """Test the PDF upload API with sample requests."""
    
    # API base URL
    base_url = "http://localhost:8000"
    
    print("=== PDF Upload API Demo ===\n")
    
    # Test health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✓ API is healthy")
            print(f"Services: {json.dumps(response.json()['services'], indent=2)}")
        else:
            print("✗ API health check failed")
            return
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to API: {e}")
        print("Make sure the API is running: python api/pdf_upload_api.py")
        return
    
    print("\n" + "="*50 + "\n")
    
    # Test file upload (you need to have a sample PDF file)
    sample_pdf_path = "sample_document.pdf"
    
    # Create a simple text file as PDF substitute for demo
    if not Path(sample_pdf_path).exists():
        print("Creating a sample text file for demo...")
        with open("sample_document.txt", "w", encoding="utf-8") as f:
            f.write("""
            Machine Learning và Artificial Intelligence
            
            Machine learning là một phương pháp phân tích dữ liệu tự động hóa việc xây dựng mô hình phân tích.
            Đây là một nhánh của trí tuệ nhân tạo dựa trên ý tưởng rằng các hệ thống có thể học từ dữ liệu,
            nhận dạng các mẫu và đưa ra quyết định với sự can thiệp tối thiểu của con người.
            
            Các ứng dụng của machine learning bao gồm:
            - Phân loại email spam
            - Nhận dạng hình ảnh
            - Dịch thuật tự động
            - Hệ thống đề xuất sản phẩm
            - Chẩn đoán y tế
            
            Deep learning là một tập con của machine learning sử dụng mạng nơ-ron nhân tạo với nhiều lớp ẩn.
            Các mạng học sâu có thể học các biểu diễn dữ liệu phức tạp thông qua nhiều cấp độ trừu tượng.
            """)
        
        print("Note: For real PDF upload, replace 'sample_document.txt' with an actual PDF file")
        sample_pdf_path = "sample_document.txt"
    
    print(f"2. Uploading document: {sample_pdf_path}")
    
    try:
        with open(sample_pdf_path, "rb") as f:
            files = {"file": f}
            data = {
                "title": "Machine Learning Document",
                "author": "Demo User",
                "subject_id": 1,
                "metadata": json.dumps({
                    "course": "AI101",
                    "semester": "Fall 2023",
                    "department": "Computer Science"
                })
            }
            
            response = requests.post(f"{base_url}/upload-pdf", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✓ Upload successful!")
                print(f"Document ID: {result['document_id']}")
                print(f"Message: {result['message']}")
                print(f"File info: {json.dumps(result['file_info'], indent=2)}")
                
                doc_id = result['document_id']
                
                # Poll for processing status
                print("\n3. Checking processing status...")
                max_wait = 60  # Wait max 60 seconds
                wait_time = 0
                
                while wait_time < max_wait:
                    status_response = requests.get(f"{base_url}/document-status/{doc_id}")
                    
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"Status: {status_data['status']}")
                        print(f"Sentences: {status_data['processed_sentences']}/{status_data['total_sentences']}")
                        
                        if status_data['status'] in ['completed', 'failed']:
                            if status_data['status'] == 'completed':
                                print("✓ Processing completed successfully!")
                            else:
                                print(f"✗ Processing failed: {status_data.get('error_message', 'Unknown error')}")
                            break
                    else:
                        print("✗ Failed to check status")
                        break
                    
                    time.sleep(3)
                    wait_time += 3
                    print("Waiting...")
                
                # Get document details
                if status_data['status'] == 'completed':
                    print("\n4. Getting document details...")
                    details_response = requests.get(f"{base_url}/document/{doc_id}")
                    
                    if details_response.status_code == 200:
                        details = details_response.json()
                        print("✓ Document details retrieved")
                        print(f"Document: {details['document']['file_name']}")
                        print(f"Upload date: {details['document']['upload_date']}")
                        print(f"Processed sentences: {details['sentences_count']}")
                        
                        # Show sample sentences
                        if details['sentences_sample']:
                            print("\nSample sentences:")
                            for i, sentence in enumerate(details['sentences_sample'][:3], 1):
                                print(f"  {i}. {sentence['processed_sentence']}")
                    
            else:
                print(f"✗ Upload failed: {response.status_code}")
                print(f"Error: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"✗ Upload request failed: {e}")
    except FileNotFoundError:
        print(f"✗ File not found: {sample_pdf_path}")
    
    print("\n" + "="*50 + "\n")
    
    # List all documents
    print("5. Listing all documents...")
    try:
        response = requests.get(f"{base_url}/documents")
        
        if response.status_code == 200:
            documents_data = response.json()
            print(f"✓ Found {documents_data['total']} documents")
            
            for doc in documents_data['documents'][:5]:  # Show first 5
                print(f"  - ID: {doc['id']}, File: {doc['file_name']}, Status: {doc['status']}")
                
        else:
            print(f"✗ Failed to list documents: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ List request failed: {e}")
    
    print("\n=== Demo Complete ===")


def test_api_endpoints():
    """Test individual API endpoints."""
    
    base_url = "http://localhost:8000"
    
    print("=== Testing API Endpoints ===\n")
    
    endpoints = [
        ("GET", "/health", "Health check"),
        ("GET", "/documents", "List documents"),
        ("GET", "/document/999", "Get non-existent document (should return 404)"),
        ("GET", "/document-status/999", "Get non-existent status (should return 404)")
    ]
    
    for method, endpoint, description in endpoints:
        print(f"Testing {method} {endpoint} - {description}")
        
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}")
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"  Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"  Request failed: {e}")
        
        print()


if __name__ == "__main__":
    print("PDF Upload API Demo")
    print("=" * 50)
    print("Make sure the API server is running:")
    print("python api/pdf_upload_api.py")
    print("=" * 50)
    print()
    
    # Run demo
    test_pdf_upload_api()
    
    print("\n")
    
    # Test endpoints
    test_api_endpoints()
