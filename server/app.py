from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import pathlib
from llm_services import summarize_article, extract_headlines, analyze_sentiment, process_agent_workflow

# Load environment variables
current_dir = pathlib.Path(__file__).parent.absolute()
env_path = current_dir / ".env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api/process', methods=['POST'])
def process():
    """
    Endpoint for agent-based workflow processing
    """
    data = request.json
    
    if not data or 'pageContent' not in data:
        print("Error: Missing page content in request data")
        return jsonify({'error': 'Missing page content'}), 400
    
    prompt = data.get('prompt', 'Analyze this article')
    page_content = data['pageContent']
    
    print("\n" + "="*50)
    print(f"PROCESSING NEW REQUEST: {prompt}")
    print("="*50 + "\n")
    
    try:
        # Process the workflow using the agent-based approach
        results = process_agent_workflow(prompt, page_content)
        
        # Ensure we have some results
        if not results:
            print("Warning: Agent workflow returned empty results")
            return jsonify({'error': 'No results generated'}), 500
            
        print("\n" + "="*50)
        print(f"WORKFLOW COMPLETED - Results: {list(results.keys())}")
        print("="*50 + "\n")
        
        return jsonify(results)
    except Exception as e:
        import traceback
        print(f"\nERROR in process endpoint: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/summarize', methods=['POST'])
def summarize():
    """
    Endpoint to summarize an article
    """
    data = request.json
    
    if not data or 'pageContent' not in data:
        print("Missing page content in request data")
        print(f"Received data: {data}")
        return jsonify({'error': 'Missing page content'}), 400
    
    prompt = data.get('prompt', 'Summarize this article')
    page_content = data['pageContent']
    
    print(f"Processing summarize request with prompt: {prompt}")
    print(f"Page content: title={page_content.get('title', 'N/A')}, url={page_content.get('url', 'N/A')}")
    
    try:
        summary = summarize_article(prompt, page_content)
        print(f"Successfully generated summary of length: {len(summary)}")
        return jsonify({'summary': summary})
    except Exception as e:
        import traceback
        print(f"Error in summarize endpoint: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/headlines', methods=['POST'])
def headlines():
    """
    Endpoint to extract headlines from a summary
    """
    data = request.json
    
    if not data or 'summary' not in data:
        return jsonify({'error': 'Missing summary'}), 400
    
    prompt = data.get('prompt', 'Extract headlines')
    summary = data['summary']
    
    try:
        headlines = extract_headlines(prompt, summary)
        return jsonify({'headlines': headlines})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sentiment', methods=['POST'])
def sentiment():
    """
    Endpoint to analyze sentiment
    """
    data = request.json
    
    if not data or 'summary' not in data:
        return jsonify({'error': 'Missing summary'}), 400
    
    prompt = data.get('prompt', 'Analyze sentiment')
    summary = data['summary']
    headlines = data.get('headlines', [])
    
    try:
        sentiment = analyze_sentiment(prompt, summary, headlines)
        return jsonify({'sentiment': sentiment})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test', methods=['GET'])
def test_api():
    """
    Test endpoint to verify Gemini API connectivity
    """
    try:
        # Import and configure Gemini
        import google.generativeai as genai
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return jsonify({'status': 'error', 'message': 'API key missing'}), 500
        
        # Test generating content
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Respond with 'Hello, World!' if you can read this message.")
        
        return jsonify({
            'status': 'success',
            'message': 'Gemini API is working correctly',
            'response': response.text
        })
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        return jsonify({
            'status': 'error', 
            'message': str(e),
            'traceback': error_traceback
        }), 500

if __name__ == '__main__':
    try:
        # Check if API key is available and valid
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("ERROR: GEMINI_API_KEY environment variable not set!")
            print(f"Current directory: {os.getcwd()}")
            print(f".env path: {env_path}")
            print(f".env file exists: {os.path.exists(env_path)}")
            exit(1)
            
        print(f"Starting server with Gemini AI (API key: {api_key[:4]}...{api_key[-4:]})")
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc() 