import requests
import json

def query_qwen_local(prompt_text):
    """
    Sends a technical prompt to the local Qwen-Coder model running via Ollama.
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "qwen2.5-coder:7b",
        "prompt": prompt_text,
        "stream": False,
        "options": {
            "temperature": 0.2  # Low temperature for strict, predictable QA logic
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return response.json().get("response", "Error: Empty response from model.")
        else:
            return f"Infrastructure Error: HTTP {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "Connection Error: Cannot reach Ollama. Verify that 'ollama serve' is running."

if __name__ == "__main__":
    # Smoke test to verify container AI communication
    test_prompt = "Respond with a single sentence: Is your coding environment active and ready?"
    print("[SDD-AGENT] Pinging local Qwen model...")
    print(f"[QWEN-RESPONSE] {query_qwen_local(test_prompt)}")