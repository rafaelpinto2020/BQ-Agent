# SQL Talk with BigQuery

SQL Talk with BigQuery is a chatbot application designed to interact with BigQuery datasets, providing insights, analysis, and detailed responses to user queries. The application leverages Google Vertex AI's generative models and integrates with Streamlit for a user-friendly interface.

## Features

- **Interactive Querying**: Users can ask natural-language questions about datasets, tables, and metrics.
- **Dataset and Table Exploration**: Automatically lists available datasets and tables, along with detailed schema descriptions.
- **SQL Query Execution**: Supports executing user-provided SQL queries with detailed results.
- **Data Insights**: Analyzes trends, correlations, and event-based metrics within datasets.
- **Scalable Integration**: Powered by Google BigQuery and Vertex AI tools for robust, scalable operations.

## Setup Instructions

### Prerequisites
1. **Python 3.8 or higher**.
2. **Google Cloud Account**:
   - Enable BigQuery and Vertex AI APIs.
   - Download a service account key in JSON format.
3. **Streamlit**: Install using `pip install streamlit`.
4. **Google Cloud SDK** (optional): For local development and testing.

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-repo>/sql-talk-with-bigquery.git
   cd sql-talk-with-bigquery

2. Install dependencies:
   ```bash
   pip install -r requirements.txt

3. Set up Google Cloud credentials:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"

### Configuration

- Update the BIGQUERY_DATASET_ID in app.py with your dataset ID.
- Ensure the service account has the required permissions to access BigQuery datasets.

### Usage
1. Run the application:
  streamlit run app.py

2. Open the Streamlit interface in your browser, typically at http://localhost:8501.

3. Interact with the chatbot using prompts like:
- "List all datasets available."
- "Show the schema of table X."
- "What are the trends in column Y over the past year?"

### Key Components
app.py
The main application file that:

- Defines the chatbot's function calls for querying datasets, tables, and performing analysis.
- Integrates with BigQuery and Vertex AI to provide conversational responses.

### Functionality
- Dataset Listing: list_datasets_func
- Table Listing: list_tables_func
- Schema Formatting: format_schema
- SQL Query Execution: sql_query_func
- Metric Analysis: analyze_metrics_func, analyze_event_metrics_func

### Sample Prompts
- "What kind of information is in this database?"
- "What tables are available in the dataset?"
- "What insights can you derive from engagement metrics?"

### References
- Google Vertex AI
- BigQuery Documentation
- Streamlit Documentation
