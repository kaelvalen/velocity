"""
Quick test to debug Ollama connection
"""
import asyncio
import httpx

async def test_ollama():
    print("="*70)
    print("OLLAMA CONNECTION TEST")
    print("="*70)
    
    # Test 1: Is Ollama running?
    print("\n[TEST 1] Checking if Ollama is running...")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                print("✓ Ollama is running")
                models = response.json().get('models', [])
                print(f"  Available models: {len(models)}")
                for model in models:
                    print(f"    - {model['name']}")
            else:
                print(f"✗ Ollama responded with status {response.status_code}")
    except Exception as e:
        print(f"✗ Ollama not accessible: {e}")
        print("\n  Solution: Start Ollama")
        print("  Windows: Launch Ollama app")
        print("  Or run: ollama serve")
        return
    
    # Test 2: Can we generate with qwen3:8b?
    print("\n[TEST 2] Testing qwen3:8b generation...")
    url = "http://localhost:11434/api/generate"
    
    # Try different model names
    model_names = ["qwen3:8b", "qwen2.5:7b", "qwen2.5:latest"]
    
    for model_name in model_names:
        print(f"\n  Trying model: {model_name}")
        payload = {
            "model": model_name,
            "prompt": "Say hello in one sentence",
            "stream": False,
            "options": {
                "num_predict": 50
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    generated = result.get('response', 'N/A')
                    print(f"  ✓ Success! Model works.")
                    print(f"    Generated: {generated[:100]}")
                    print(f"\n  → Use this model name in interactive_velocity.py")
                    break
                else:
                    print(f"  ✗ Failed with status {response.status_code}")
                    print(f"    Response: {response.text[:200]}")
        except httpx.TimeoutException:
            print(f"  ✗ Timeout (model might be loading...)")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_ollama())
