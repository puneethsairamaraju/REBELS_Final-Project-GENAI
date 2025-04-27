import requests
import json
import os
import time

def create_payload(model, prompt, target, **kwargs):
    """
    Create the Request Payload for either FAU API or Local Ollama.
    """

    if target == "chat.hpc.fau.edu":
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if kwargs:
            payload["parameters"] = {key: value for key, value in kwargs.items()}

    elif target == "ollama":
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if kwargs:
            payload["options"] = {key: value for key, value in kwargs.items()}

    else:
        print(f'‼️ ERROR: Unknown target: {target}')
        return None

    return payload


def model_req(payload=None, use_fallback=False):
    """
    Issue request to FAU or fallback to local Ollama if needed.
    """

    # Load from environment (set in bot or hardcoded before call)
    url = os.getenv('URL_GENERATE', "https://chat.hpc.fau.edu/api/chat/completions")
    api_key = os.getenv('API_KEY', None)
    target = "chat.hpc.fau.edu"

    if use_fallback:
        url = "http://localhost:11434/api/generate"
        target = "ollama"
        payload["model"] = "llama3:Advanced"
        print("\n⚠️ Switching to Local Ollama `llama3:Advanced` due to FAU API failure.")

    headers = {
        "Content-Type": "application/json"
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    print(f"\n🔄 Sending Request to: {url}")
    print(f"📌 Payload: {json.dumps(payload, indent=2)}")

    try:
        start_time = time.time()
        response = requests.post(url, json=payload, headers=headers)
        delta = time.time() - start_time
    except Exception as e:
        if not use_fallback:
            print("⚠️ FAU API failed, switching to local Ollama...")
            return model_req(payload, use_fallback=True)
        return -1, f"‼️ ERROR: Request failed! {str(e)}"

    if response is None:
        if not use_fallback:
            print("⚠️ No response from FAU API, switching to local Ollama...")
            return model_req(payload, use_fallback=True)
        return -1, "‼️ ERROR: No response from either FAU or Ollama."

    elif response.status_code == 200:
        response_json = response.json()

        if 'choices' in response_json and len(response_json['choices']) > 0:
            result = response_json['choices'][0]['message']['content']
        elif 'response' in response_json:
            result = response_json['response']
        else:
            result = response_json
        
        return round(delta, 3), result

    elif response.status_code in [401, 403]:
        return -1, "‼️ ERROR: Authentication issue – check API key."

    else:
        if not use_fallback:
            print(f"⚠️ FAU API returned HTTP {response.status_code}, switching to local Ollama...")
            return model_req(payload, use_fallback=True)
        return -1, f"‼️ ERROR: HTTP {response.status_code}: {response.text}"


# ✅ DEBUG TEST
if __name__ == "__main__":
    MESSAGE = "Extract functional requirements from a chatbot conversation."

    FEW_SHOT_PROMPT = """
You are an AI specializing in Requirement Analysis. 
Given the following chatbot conversation, extract the functional requirements.

Example:
User: "Explain QuickSort."
Bot: "QuickSort is a divide-and-conquer sorting algorithm..."

Extracted Functional Requirement: 
- The chatbot must explain QuickSort with step-by-step details.

Now, analyze this request:
"""

    PROMPT = FEW_SHOT_PROMPT + MESSAGE

    payload = create_payload(
        target="chat.hpc.fau.edu",
        model="Llama-3.2-11B-Vision-Instruct",
        prompt=PROMPT,
        temperature=0.5,
        num_ctx=1024,
        num_predict=100
    )

    time_taken, response = model_req(payload)
    print(f"\n✅ Extracted Functional Requirements:\n{response}")
    if time_taken > 0:
        print(f"⏱️ Time taken: {time_taken}s")
