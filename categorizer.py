import json
import requests

def get_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def categorize_page(filename):
    """
    Submits the content of a file to a local LLM for categorization.
    """
    config = get_config()
    llm_config = config.get('llm', {})
    endpoint = llm_config.get('endpoint')
    api_key = llm_config.get('api_key')

    if not endpoint:
        raise ValueError("LLM endpoint not configured in config.json")

    with open(filename, 'r', encoding='latin-1') as f:
        content = f.read()

    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    data = {
        "model": "local-model",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that categorizes web pages based on their content."},
            {"role": "user", "content": f"Please categorize the following web page content:\n\n{content}"}
        ]
    }

    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with LLM: {e}")
        return None

if __name__ == '__main__':
    # Create a dummy html file for testing
    dummy_html_file = 'test_categorization.html'
    with open(dummy_html_file, 'w') as f:
        f.write('''
            <html>
                <body>
                    <h1>This is a test page about technology and programming.</h1>
                </body>
            </html>
        ''')
    
    # Make sure you have a local LLM running and the config.json is set up correctly.
    # This is an example and will likely fail if you don't have a local LLM running.
    # You can use a tool like LM Studio or Ollama to run a local LLM.
    category = categorize_page(dummy_html_file)
    if category:
        print("Categorization result:")
        print(category)

    import os
    os.remove(dummy_html_file)
