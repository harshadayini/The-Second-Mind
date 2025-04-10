# Multi-Agent Research Assistant

## Project Description
The Multi-Agent Research Assistant is a system designed to iteratively generate, refine, and rank research hypotheses through a collaboration of specialized agents. The system retrieves real-time external data and uses several agents to:
- **Generate** an initial hypothesis based on a given research topic.
- **Reflect** on the hypothesis by integrating external data.
- **Rank** the hypothesis to assess its quality.
- **Evolve** the hypothesis through iterative refinement.
- **Summarize** the gathered data and produce a final cohesive summary.
- **Select** relevant external data using an API Selection Agent.

The pipeline is orchestrated by a Supervisor agent that manages iterations and integrates outputs from Generation, Reflection, Ranking, Evolution, Summarization, and API Selection agents. The final outputs are displayed interactively with visualizations that include score evolution graphs and dynamic metrics heatmaps, making it easy to understand the performance and improvements at each iteration.

## Features
- **Iterative Refinement:** Improve hypotheses over several cycles based on agent feedback.
- **Real-Time Data Integration:** Fetch external data from sources such as Google, NASA, and arXiv.
- **Dynamic Visualization:** Interactive graphs show score evolution and key agent performance metrics.
- **Robust Pipeline:** Modular agent design with clear roles (API Selection Agent retrieves external data, Summarization Agent synthesizes data, etc.).
- **Logging:** Detailed logging for transparency and debugging.

## Setup Instructions

### Prerequisites
- **Python:** Version 3.9 or later
- **API Keys:** 
  - OpenAI API key
  - Google API key and CX identifier (for custom search)
  - NASA API key

### Environment Setup

1. Create and Activate a Virtual Environment: (MacOS)
    python -m venv env
    source env/bin/activate
   
2. Install Dependencies:
    pip install -r requirements.txt

3. Configure API Keys: Create a .env file in the project root with the following content (replace placeholder values with your actual API keys):
    OPENAI_API_KEY=your_openai_api_key
    GOOGLE_API_KEY=your_google_api_key
    GOOGLE_CX=your_google_cx
    NASA_API_KEY=your_nasa_api_key

### Running the Project
To launch the application, run:
    streamlit run main.py

