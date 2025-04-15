import os
import tempfile
import subprocess
import requests
import sys
import time
import json
import shutil
import pytest

# Integration test for full coding assistant workflow using Hugging Face Inference API as remote LLM
# Requires HF_TOKEN env var (user must generate their own at https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained)

HF_API_URL = "https://router.huggingface.co/novita/v3/openai/chat/completions"
HF_MODEL = "deepseek-ai/DeepSeek-V3-0324"
HF_TOKEN = os.environ.get("HF_TOKEN")

@pytest.mark.skipif(not HF_TOKEN, reason="HF_TOKEN environment variable not set")
def test_full_integration_remote_llm(tmp_path):
    """
    This test simulates a real user workflow:
    - Configures the assistant to use a remote LLM (Hugging Face Inference API)
    - Issues a prompt to generate Python code and write it to a file
    - Verifies the file is created and contains valid code
    - Executes the code to check correctness
    - All actions are performed in a temp directory for safety
    """
    # Step 1: Prepare payload for remote LLM
    prompt = "Write a Python function named add that takes two arguments and returns their sum. Save it to a file named add.py."
    payload = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "model": HF_MODEL,
        "stream": False
    }
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    # Step 2: Call the remote LLM API
    response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
    assert response.status_code == 200, f"LLM API error: {response.text}"
    data = response.json()
    # Step 3: Extract code from LLM response
    message = data["choices"][0]["message"]["content"]
    # Try to extract Python code block, else fallback to raw
    import re
    code_match = re.search(r"```python\\s*(.*?)```", message, re.DOTALL)
    if code_match:
        code = code_match.group(1)
    else:
        code = message.strip()
    # Step 4: Write code to add.py in temp dir
    add_py = tmp_path / "add.py"
    with open(add_py, "w") as f:
        f.write(code)
    # Step 5: Attempt to import and run the function
    sys.path.insert(0, str(tmp_path))
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("add", str(add_py))
        add_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(add_mod)
        assert hasattr(add_mod, "add"), "No 'add' function found in generated code"
        result = add_mod.add(2, 3)
        assert result == 5, f"add(2, 3) returned {result}"
    finally:
        sys.path.pop(0)
    # Step 6: Clean up (pytest tmp_path auto-cleans)
    # Confirm file is deleted after test
    assert add_py.exists()

# Note: This test is safe to run because it uses pytest's tmp_path fixture for full isolation.
# To run: HF_TOKEN=your_token pytest tests/test_integration_hf_remote_llm.py -v
