import os
import google.generativeai as genai
from typing import List, Dict, Any
from dotenv import load_dotenv
import pathlib

# Load environment variables
current_dir = pathlib.Path(__file__).parent.absolute()
env_path = current_dir / ".env"
load_dotenv(dotenv_path=env_path)

# Initialize Gemini AI with API key
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

# Remove quotes if present
API_KEY = API_KEY.strip('"\'')
genai.configure(api_key=API_KEY)

# Configure the models
model = genai.GenerativeModel('gemini-1.5-pro')  # Used for content processing
agent_model = genai.GenerativeModel('gemini-2.0-flash')  # Used for agent workflow

def process_agent_workflow(user_prompt: str, page_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process the agent workflow using LLM to decide which functions to call
    
    Args:
        user_prompt: User's prompt
        page_content: Page content with url, title, and content
        
    Returns:
        Dictionary with all results (summary, headlines, sentiment)
    """
    system_prompt = """
    You are a news agent that follows a specific 3-step workflow for analyzing articles.
    
    Step 1: First summarize the article
    Step 2: Then extract headlines from the summary
    Step 3: Finally analyze sentiment based on the summary and headlines
    
    Respond with EXACTLY ONE of these formats:
    FUNCTION_CALL: python_function_name|input
    FINAL_ANSWER: [result]

    where python_function_name is one of the following:
        summarize_article(text) - Use this FIRST to summarize the full article
        extract_headlines(text) - Use this SECOND to extract headlines from the summary
        analyze_sentiment(text) - Use this THIRD to analyze sentiment based on summary and headlines

    After completing all 3 steps, provide a FINAL_ANSWER with the sentiment result.
    IMPORTANT: Always follow the correct workflow order: summarize → headlines → sentiment → FINAL_ANSWER
    """
    
    # Initialize variables
    iteration = 0
    max_iterations = 5
    iteration_responses = []
    results = {}
    current_query = user_prompt
    
    # Store the original page content for use by functions
    context = {
        "page_content": page_content,
        "summary": None,
        "headlines": None,
        "sentiment": None
    }
    
    # Print workflow header
    print("\n" + "-"*50)
    print(" NEWS ANALYSIS WORKFLOW ".center(50, "*"))
    print("-"*50)
    
    while iteration < max_iterations:
        print(f"\n--- Iteration {iteration + 1} ---")
        
        # Prepare agent query based on current iteration
        if iteration == 0:
            agent_query = f"{current_query}\n\nLet's first summarize this article."
        elif iteration == 1:
            agent_query = f"{current_query}\n\n{' '.join(iteration_responses)}\n\nNow that we have a summary, let's extract key headlines."
        elif iteration == 2:
            agent_query = f"{current_query}\n\n{' '.join(iteration_responses)}\n\nWith the summary and headlines, let's analyze the sentiment."
        elif iteration == 3 and "summary" in results and "headlines" in results and "sentiment" in results:
            agent_query = f"{current_query}\n\n{' '.join(iteration_responses)}\n\nNow provide a FINAL_ANSWER with the sentiment: '{results['sentiment']}'"
        else:
            agent_query = f"{current_query}\n\n{' '.join(iteration_responses)}\n\nWhat should I do next?"

        # Get agent's response
        prompt = f"{system_prompt}\n\nQuery: {agent_query}"
        
        try:
            response = agent_model.generate_content(prompt)
            response_text = response.text.strip()
            print(f"LLM Response: {response_text}")
            
            # Parse the response to determine which function to call
            if response_text.startswith("FUNCTION_CALL:"):
                # Extract function name and input
                function_call = response_text.replace("FUNCTION_CALL:", "").strip()
                function_parts = function_call.split("|")
                
                function_name = function_parts[0].strip()
                function_input = function_parts[1].strip() if len(function_parts) > 1 else ""
                
                # Call the appropriate function
                result = None
                if function_name == "summarize_article":
                    if iteration == 0:
                        result = summarize_article(user_prompt, context["page_content"])
                        context["summary"] = result
                        results["summary"] = result
                    else:
                        input_text = function_input if function_input else get_content_from_context(context)
                        result = summarize_article(user_prompt, {"content": input_text})
                        context["summary"] = result
                        results["summary"] = result
                        
                elif function_name == "extract_headlines":
                    input_text = context["summary"] if context["summary"] else function_input
                    result = extract_headlines(user_prompt, input_text)
                    context["headlines"] = result
                    results["headlines"] = result
                    
                elif function_name == "analyze_sentiment":
                    if context["summary"]:
                        if context["headlines"]:
                            input_text = f"{context['summary']}\n\nHeadlines: {', '.join(context['headlines'])}"
                        else:
                            input_text = context["summary"]
                    else:
                        input_text = function_input
                    
                    result = analyze_sentiment(user_prompt, input_text)
                    context["sentiment"] = result
                    results["sentiment"] = result
                
                # Format the response for the next iteration
                if result:
                    # Truncate result display if it's too long
                    result_display = str(result)
                    if isinstance(result, str) and len(result) > 50:
                        result_display = result[:47] + "..."
                    elif isinstance(result, list) and len(str(result)) > 100:
                        result_display = str(result[:3]) + "...]"
                    
                    print(f"  Result: {result_display}")
                    
                    # Format the iteration response for the LLM
                    if function_name == "summarize_article":
                        iteration_response = f"In the {iteration+1} iteration you called summarize_article with user prompt and page content parameters, and the function returned [{result_display}]"
                    elif function_name == "extract_headlines":
                        headlines_str = str(result).replace("'", "\"")
                        iteration_response = f"In the {iteration+1} iteration you called extract_headlines with `summarize_article()` return output parameters, and the function returned {headlines_str}"
                    elif function_name == "analyze_sentiment":
                        iteration_response = f"In the {iteration+1} iteration you called analyze_sentiment with `summarize_article()` and `extract_headlines()` return output parameters, and the function returned [\"{result}\"]"
                    
                    iteration_responses.append(iteration_response)
                
            elif response_text.startswith("FINAL_ANSWER:"):
                # Extract the final answer
                final_answer = response_text.replace("FINAL_ANSWER:", "").strip()
                results["final_answer"] = final_answer
                print(f"  Result: {final_answer}")
                break
                
            else:
                # Invalid response format
                print(f"  Error: Invalid response format")
        
        except Exception as e:
            print(f"  Error: {str(e)}")
        
        iteration += 1
        
        # Check if we have all necessary results
        if iteration >= 4 and "summary" in results and "headlines" in results and "sentiment" in results:
            # If we have all results but no final answer yet, create one
            if "final_answer" not in results and "sentiment" in results:
                results["final_answer"] = f"[\"{results['sentiment']}\"]"
                print(f"LLM Response: FINAL_ANSWER: [\"{results['sentiment']}\"]")
                print(f"  Result: [\"{results['sentiment']}\"]")
            break
    
    # Ensure we have a final answer even if the LLM didn't provide one
    if "final_answer" not in results and "sentiment" in results:
        results["final_answer"] = f"[\"{results['sentiment']}\"]"
        print(f"LLM Response: FINAL_ANSWER: [\"{results['sentiment']}\"]")
        print(f"  Result: [\"{results['sentiment']}\"]")
    
    print("\n=== Agent Execution Complete ===\n")
    return results

def get_content_from_context(context):
    """Helper function to extract content from context for function input"""
    if context["summary"]:
        return context["summary"]
    elif context["page_content"] and "content" in context["page_content"]:
        return context["page_content"]["content"]
    return ""

def summarize_article(prompt: str, page_content: Dict[str, Any]) -> str:
    """Summarize an article using Gemini AI"""
    try:
        # Validate input
        if not isinstance(page_content, dict):
            raise ValueError("page_content must be a dictionary")
            
        # Construct the prompt for Gemini
        title = page_content.get('title', 'Untitled')
        content = page_content.get('content', '')
        url = page_content.get('url', '')
        
        # Check if content is present
        if not content:
            return "No content to summarize"
        
        gemini_prompt = f"""
        User prompt: {prompt}
        
        I need to summarize the following article:
        URL: {url}
        Title: {title}
        
        Content:
        {content[:8000]}  # Truncate content to avoid token limits
        
        Please provide a detailed summary of this article.
        """
        
        # Call Gemini AI
        response = model.generate_content(gemini_prompt)
        
        # Return the summary
        return response.text
    except Exception as e:
        print(f"Error in summarize_article: {str(e)}")
        raise

def extract_headlines(prompt: str, summary: str) -> List[str]:
    """Extract headlines from a summary using Gemini AI"""
    # Construct the prompt for Gemini
    gemini_prompt = f"""
    User prompt: {prompt}
    
    I have a summary of an article:
    {summary}
    
    Please extract 3-5 key headlines or main points from this summary. 
    Format your response as a list of headlines, with each headline on a new line.
    Do not include numbers, bullets, or any other formatting - just plain text for each headline.
    """
    
    # Call Gemini AI
    response = model.generate_content(gemini_prompt)
    
    # Process the response to get a list of headlines
    headlines_text = response.text.strip()
    headlines = [line.strip() for line in headlines_text.split('\n') if line.strip()]
    
    return headlines

def analyze_sentiment(prompt: str, text: str) -> str:
    """Analyze sentiment of the content using Gemini AI"""
    # Construct the prompt for Gemini
    gemini_prompt = f"""
    User prompt: {prompt}
    
    I have the following text:
    {text}
    
    Please analyze the overall sentiment of this content. This is a news article analysis.
    Pay special attention to the following:
    - News about disasters, accidents, conflicts, or deaths should be considered NEGATIVE
    - News about political tensions, economic downturns, or health crises should be considered NEGATIVE
    - News about celebrations, achievements, positive developments should be considered POSITIVE
    - Only classify as NEUTRAL if there is truly no positive or negative sentiment
    
    Remember: News articles that report on tragedies, conflicts, or problems usually have a negative sentiment
    even if the reporting tone is neutral.
    
    Classify the content as exactly one of:
    - Positive
    - Negative
    - Neutral
    
    Provide only one word as your answer: Positive, Negative, or Neutral.
    """
    
    # Call Gemini AI
    response = model.generate_content(gemini_prompt)
    
    # Process the response to get the sentiment
    sentiment = response.text.strip()
    
    # Normalize the sentiment to one of the three categories
    if "positive" in sentiment.lower():
        return "Positive"
    elif "negative" in sentiment.lower():
        return "Negative"
    else:
        return "Neutral" 