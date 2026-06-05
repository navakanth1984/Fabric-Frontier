import requests
import json
import sseclient

def test_chat_streaming():
    url = "http://localhost:8004/chat"
    payload = {
        "message": "Hello, this is a test from the QA subagent.",
        "stream": True
    }
    
    print(f"Sending POST request to {url}...")
    try:
        response = requests.post(url, json=payload, stream=True)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Successfully received 200 OK.")
            
            # Check if it's SSE (Server-Sent Events) or just streaming lines
            content_type = response.headers.get('content-type', '')
            if 'text/event-stream' in content_type:
                client = sseclient.SSEClient(response)
                for event in client.events():
                    print(f"Received stream event: {event.data}")
            else:
                for line in response.iter_lines():
                    if line:
                        print(f"Received stream line: {line.decode('utf-8')}")
                        
            print("Streaming test completed.")
            print("NOTE: Please verify LangSmith manually to ensure the trace was received, or configure LangSmith API to verify programmatically.")
        else:
            print(f"Error: Received {response.status_code} instead of 200 OK.")
            print(response.text)
    except Exception as e:
        print(f"Failed to connect or stream: {e}")

if __name__ == "__main__":
    test_chat_streaming()
