# News Analysis Extension

A Chrome extension that leverages Google's Gemini AI to analyze news articles, providing summaries, key headlines, and sentiment analysis. This tool helps users quickly understand the key points and emotional tone of news articles through advanced AI processing.

## Features

### 1. Article Analysis
- **Smart Summarization**: 
  - Automatically generates concise summaries of news articles
  - Maintains key information while reducing content length
  - Handles articles up to 8000 characters
  - Preserves context and important details

- **Headline Extraction**: 
  - Identifies 3-5 key headlines or main points from the article
  - Extracts the most significant information
  - Formats headlines in a clean, readable format
  - Removes unnecessary formatting and numbering

- **Sentiment Analysis**: 
  - Determines the overall sentiment (Positive/Negative/Neutral) of the content
  - Considers context and subject matter
  - Applies specific rules for news article classification
  - Provides consistent sentiment categorization

### 2. User Interface
- **Clean and Intuitive Popup Interface**:
  - Modern, responsive design
  - Easy-to-read results display
  - Clear section separation
  - Progress indicators for analysis steps

- **Real-time Analysis Results Display**:
  - Live updates during processing
  - Clear formatting of results
  - Separate sections for summary, headlines, and sentiment
  - Error state handling and display

- **Easy-to-use Prompt Input System**:
  - Simple text input for analysis requests
  - Example prompts provided
  - Clear instructions for users
  - Input validation and error handling

- **Clear Workflow Visualization**:
  - Step-by-step progress indication
  - Current step highlighting
  - Completion status display
  - Error state visualization

### 3. AI Integration
- **Powered by Google's Gemini AI Models**:
  - Gemini 1.5 Pro for content processing
    - High-quality text generation
    - Advanced language understanding
    - Context-aware processing
  - Gemini 2.0 Flash for agent workflow
    - Fast response times
    - Efficient decision making
    - Reliable function calling

- **Intelligent Workflow Management**:
  - Sequential processing of analysis steps
  - Context preservation between steps
  - Error recovery and retry mechanisms
  - State management and tracking

- **Context-aware Analysis**:
  - Maintains article context throughout analysis
  - Uses previous step results for next steps
  - Adapts to different article types
  - Handles various content formats

## Technical Architecture

### Server Components
1. **LLM Services (`server/llm_services.py`)**
   - **AI Model Interactions**:
     - Handles all communication with Gemini AI
     - Manages API calls and responses
     - Implements error handling and retries
     - Processes model outputs

   - **Analysis Workflow Implementation**:
     1. Article Summarization
        - Content validation
        - Length management
        - Key information extraction
        - Summary formatting
     2. Headline Extraction
        - Summary analysis
        - Key point identification
        - Headline formatting
        - List generation
     3. Sentiment Analysis
        - Context consideration
        - Rule application
        - Sentiment classification
        - Result formatting

   - **Context Management**:
     - Maintains state between steps
     - Tracks analysis progress
     - Stores intermediate results
     - Manages data flow

2. **Flask Server (`server/app.py`)**
   - **REST API Endpoints**:
     - `/api/process`: Main analysis endpoint
     - `/api/health`: Server health check
     - Error handling endpoints
     - Status endpoints

   - **CORS and Security**:
     - Cross-origin request handling
     - Request validation
     - API key verification
     - Rate limiting

   - **Communication Management**:
     - Request/response handling
     - Data formatting
     - Error propagation
     - Status reporting

### Extension Components
1. **Popup Interface (`extension/popup.html`)**
   - **User Input Handling**:
     - Prompt input field
     - Input validation
     - Error display
     - Submit button

   - **Results Display**:
     - Summary section
     - Headlines section
     - Sentiment section
     - Error messages

   - **Workflow Status**:
     - Progress indicators
     - Step completion markers
     - Error states
     - Loading states

2. **Content Scripts**
   - **Content Extraction**:
     - Page content parsing
     - Article text extraction
     - Metadata collection
     - Format handling

   - **Server Communication**:
     - API request handling
     - Response processing
     - Error handling
     - Status updates

## Setup Instructions

### Prerequisites
- Python 3.7+ (for server)
- Chrome browser (latest version)
- Google Gemini API key
- Git (for installation)

### Installation

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd news-analysis-extension
   ```

2. **Install Python Dependencies**
   ```bash
   # Create and activate virtual environment (recommended)
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the server directory:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   Note: Keep your API key secure and never commit it to version control.

4. **Load the Extension in Chrome**
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" (top right toggle)
   - Click "Load unpacked"
   - Select the `extension` directory
   - Verify the extension appears in your extensions list

5. **Start the Server**
   ```bash
   cd server
   python app.py
   ```
   The server will start on `http://localhost:5000`

## Usage

1. **Access the Extension**
   - Click the extension icon in Chrome toolbar
   - The popup interface will appear
   - Verify the server connection status

2. **Analyze an Article**
   - Navigate to any news article
   - Click the extension icon
   - Enter your analysis prompt
   - Click "Analyze"
   - Wait for the analysis to complete

3. **View Results**
   The analysis will be performed in three steps:
   1. Article Summary
      - Concise overview
      - Key points highlighted
      - Main story elements
   2. Key Headlines
      - 3-5 main points
      - Clean formatting
      - Important details
   3. Sentiment Analysis
      - Overall sentiment
      - Classification explanation
      - Confidence level

## Example Prompts

1. "Analyze this article: first summarize, then extract headlines, and finally determine the sentiment"
2. "Process this news page by summarizing it, extracting key headlines, and analyzing the overall sentiment"
3. "Follow the 3-step workflow: summarize this article, identify its main headlines, and determine if it's positive or negative"

## Sentiment Analysis Guidelines

The system follows these rules for sentiment classification:

- **Negative**:
  - Disasters and accidents
  - Conflicts and wars
  - Deaths and tragedies
  - Political tensions
  - Economic downturns
  - Health crises
  - Environmental disasters
  - Social unrest

- **Positive**:
  - Celebrations and achievements
  - Scientific breakthroughs
  - Economic growth
  - Social progress
  - Humanitarian efforts
  - Environmental improvements
  - Cultural events
  - Personal success stories

- **Neutral**:
  - Balanced reporting
  - Factual information
  - Statistical data
  - Routine updates
  - General announcements
  - Mixed outcomes
  - Unclear implications
  - Standard procedures

## Error Handling

The system includes robust error handling for:

- **API Issues**:
  - Missing API keys
  - Invalid API keys
  - Rate limiting
  - API timeouts

- **Content Problems**:
  - Invalid article content
  - Empty pages
  - Malformed HTML
  - Missing text

- **Network Issues**:
  - Connection failures
  - Timeout errors
  - Server unavailability
  - CORS problems

- **AI Model Errors**:
  - Response parsing errors
  - Invalid outputs
  - Model timeouts
  - Content filtering

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide for Python code
- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Handle errors gracefully
- Maintain backward compatibility

## License

[Specify your license here]

## Support

For support, please:
- Open an issue in the repository
- Contact the maintainers
- Check the documentation
- Join the community forum

## Acknowledgments

- Google Gemini AI team
- Chrome Extension development community
- Open source contributors
- Project maintainers 