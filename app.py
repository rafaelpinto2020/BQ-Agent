import os
import time
from google.cloud import bigquery
import streamlit as st
from vertexai.generative_models import FunctionDeclaration, GenerativeModel, Part, Tool

# Set the credentials environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/rafael.pinto/Downloads/newson-vinson-ga4-41e210d8a741.json"

# Set the BigQuery dataset ID
BIGQUERY_DATASET_ID = "newson-vinson-ga4.analytics_406732140"

list_datasets_func = FunctionDeclaration(
    name="list_datasets",
    description="Get a list of datasets that will help answer the user's question",
    parameters={
        "type": "object",
        "properties": {},
    },
)

list_tables_func = FunctionDeclaration(
    name="list_tables",
    description="List tables in a dataset that will help answer the user's question",
    parameters={
        "type": "object",
        "properties": {
            "dataset_id": {
                "type": "string",
                "description": "Dataset ID to fetch tables from.",
            }
        },
        "required": [
            "dataset_id",
        ],
    },
)

# Modify the get_table function to better handle nested fields
def format_schema(fields, prefix=''):
    schema_info = []
    for field in fields:
        field_info = {
            'name': prefix + field.name,
            'field_type': field.field_type,
            'mode': field.mode
        }
        
        if field.field_type == 'RECORD':
            # For nested fields, recursively get their structure
            nested_prefix = prefix + field.name + '.'
            nested_fields = format_schema(field.fields, nested_prefix)
            schema_info.extend(nested_fields)
        else:
            schema_info.append(field_info)
    
    return schema_info

get_table_func = FunctionDeclaration(
    name="get_table",
    description="Get information about a table, including the description, schema, and number of rows that will help answer the user's question. Always use the fully qualified dataset and table names.",
    parameters={
        "type": "object",
        "properties": {
            "table_id": {
                "type": "string",
                "description": "Fully qualified ID of the table to get information about",
            }
        },
        "required": [
            "table_id",
        ],
    },
)

sql_query_func = FunctionDeclaration(
    name="sql_query",
    description="Get information from data in BigQuery using SQL queries",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query on a single line that will help give quantitative answers to the user's question when run on a BigQuery dataset and table. In the SQL query, always use the fully qualified dataset and table names.",
            }
        },
        "required": [
            "query",
        ],
    },
)

analyze_metrics_func = FunctionDeclaration(
    name="analyze_metrics",
    description="Analyze key metrics and their relationships within a table",
    parameters={
        "type": "object",
        "properties": {
            "table_id": {
                "type": "string",
                "description": "Fully qualified table ID to analyze"
            },
            "metric_columns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of columns containing metrics to analyze"
            }
        },
        "required": ["table_id", "metric_columns"]
    }
)

get_data_insights_func = FunctionDeclaration(
    name="get_data_insights",
    description="Generate insights about trends, patterns, and correlations in the data",
    parameters={
        "type": "object",
        "properties": {
            "table_id": {
                "type": "string",
                "description": "Fully qualified table ID"
            },
            "time_column": {
                "type": "string",
                "description": "Column containing timestamp or date information"
            },
            "metric_column": {
                "type": "string",
                "description": "Column containing the metric to analyze"
            }
        },
        "required": ["table_id", "metric_column"]
    }
)

# Add a new function declaration for event analysis
analyze_event_metrics_func = FunctionDeclaration(
    name="analyze_event_metrics",
    description="Analyze metrics for specific events in GA4 data",
    parameters={
        "type": "object",
        "properties": {
            "table_id": {
                "type": "string",
                "description": "Fully qualified table ID"
            },
            "event_name": {
                "type": "string",
                "description": "Name of the event to analyze"
            },
            "metric_path": {
                "type": "string",
                "description": "Nested path to the metric (e.g., 'event_params.value.string_value')"
            }
        },
        "required": ["table_id", "event_name"]
    }
)

sql_query_tool = Tool(
    function_declarations=[
        list_datasets_func,
        list_tables_func,
        get_table_func,
        sql_query_func,
        analyze_metrics_func,
        get_data_insights_func,
        analyze_event_metrics_func,  # Add the new function
    ],
)

model = GenerativeModel(
    "gemini-1.5-pro-001",
    generation_config={"temperature": 0},
    tools=[sql_query_tool],
)

st.set_page_config(
    page_title="SQL Talk with BigQuery",
    layout="wide",
)

col1, col2 = st.columns([8, 1])
with col1:
    st.title("SQL Talk with BigQuery Dataset")
with col2:
    st.text("Demo")

st.subheader("Powered by Function Calling in Gemini")

st.markdown(
    "[Source Code](https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini/function-calling/sql-talk-app/)   •   [Documentation](https://cloud.google.com/vertex-ai/docs/generative-ai/multimodal/function-calling)   •   [Codelab](https://codelabs.developers.google.com/codelabs/gemini-function-calling)   •   [Sample Notebook](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/gemini/function-calling/intro_function_calling.ipynb)"
)

with st.expander("Sample prompts", expanded=True):
    st.write(
        """
        - What kind of information is in this database?
        - What tables are available in the dataset?
        - Can you show me the schema of table X?
        - What are the main metrics related to X?
        - Analyze the trends in metric Y over the past month
        - What insights can you derive from the engagement metrics?
        - How do metrics A and B correlate with each other?
    """
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"].replace("$", "\$"))  # noqa: W605
        try:
            with st.expander("Function calls, parameters, and responses"):
                st.markdown(message["backend_details"])
        except KeyError:
            pass

if prompt := st.chat_input("Ask me about information in the database..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        chat = model.start_chat()
        client = bigquery.Client()

        prompt += """
            Please give a concise, high-level summary followed by detail in
            plain language about where the information in your response is
            coming from in the database. Only use information that you learn
            from BigQuery, do not make up information.
            """

        response = chat.send_message(prompt)
        response = response.candidates[0].content.parts[0]

        print(response)

        api_requests_and_responses = []
        backend_details = ""

        function_calling_in_process = True
        while function_calling_in_process:
            try:
                params = {}
                for key, value in response.function_call.args.items():
                    params[key] = value

                print(response.function_call.name)
                print(params)

                if response.function_call.name == "list_datasets":
                    api_response = client.list_datasets()
                    api_response = BIGQUERY_DATASET_ID
                    api_requests_and_responses.append(
                        [response.function_call.name, params, api_response]
                    )

                if response.function_call.name == "list_tables":
                    api_response = client.list_tables(params["dataset_id"])
                    api_response = str([table.table_id for table in api_response])
                    api_requests_and_responses.append(
                        [response.function_call.name, params, api_response]
                    )

                if response.function_call.name == "get_table":
                    table = client.get_table(params["table_id"])
                    schema_info = format_schema(table.schema)
                    
                    # Create a more detailed API response
                    api_response = {
                        "description": table.description,
                        "num_rows": table.num_rows,
                        "schema": schema_info
                    }
                    
                    api_requests_and_responses.append(
                        [
                            response.function_call.name,
                            params,
                            {
                                "description": str(api_response["description"]),
                                "num_rows": str(api_response["num_rows"]),
                                "schema": str([
                                    f"{field['name']} ({field['field_type']}, {field['mode']})"
                                    for field in api_response["schema"]
                                ])
                            }
                        ]
                    )
                    api_response = str(api_response)

                if response.function_call.name == "sql_query":
                    job_config = bigquery.QueryJobConfig(
                        maximum_bytes_billed=100000000
                    )  # Data limit per query job
                    try:
                        cleaned_query = (
                            params["query"]
                            .replace("\\n", " ")
                            .replace("\n", "")
                            .replace("\\", "")
                        )
                        query_job = client.query(cleaned_query, job_config=job_config)
                        api_response = query_job.result()
                        api_response = str([dict(row) for row in api_response])
                        api_response = api_response.replace("\\", "").replace("\n", "")
                        api_requests_and_responses.append(
                            [response.function_call.name, params, api_response]
                        )
                    except Exception as e:
                        api_response = f"{str(e)}"
                        api_requests_and_responses.append(
                            [response.function_call.name, params, api_response]
                        )

                if response.function_call.name == "analyze_metrics":
                    try:
                        # Create a query to get summary statistics for the specified metrics
                        metrics = ", ".join([f"AVG({col}) as avg_{col}, MAX({col}) as max_{col}, MIN({col}) as min_{col}" 
                                           for col in params["metric_columns"]])
                        query = f"SELECT {metrics} FROM `{params['table_id']}`"
                        
                        job_config = bigquery.QueryJobConfig(maximum_bytes_billed=100000000)
                        query_job = client.query(query, job_config=job_config)
                        api_response = query_job.result()
                        api_response = str([dict(row) for row in api_response])
                        api_requests_and_responses.append(
                            [response.function_call.name, params, api_response]
                        )
                    except Exception as e:
                        api_response = f"{str(e)}"
                        api_requests_and_responses.append(
                            [response.function_call.name, params, api_response]
                        )

                if response.function_call.name == "get_data_insights":
                    try:
                        # Create a query to analyze trends over time
                        query = f"""
                        SELECT 
                            {params['time_column']},
                            AVG({params['metric_column']}) as avg_metric,
                            COUNT(*) as count
                        FROM `{params['table_id']}`
                        GROUP BY {params['time_column']}
                        ORDER BY {params['time_column']} DESC
                        LIMIT 10
                        """
                        
                        job_config = bigquery.QueryJobConfig(maximum_bytes_billed=100000000)
                        query_job = client.query(query, job_config=job_config)
                        api_response = query_job.result()
                        api_response = str([dict(row) for row in api_response])
                        api_requests_and_responses.append(
                            [response.function_call.name, params, api_response]
                        )
                    except Exception as e:
                        api_response = f"{str(e)}"
                        api_requests_and_responses.append(
                            [response.function_call.name, params, api_response]
                        )

                if response.function_call.name == "analyze_event_metrics":
                    try:
                        query = f"""
                        SELECT
                            event_name,
                            {params.get('metric_path', 'event_params.value.string_value')} as metric_value,
                            COUNT(*) as event_count
                        FROM `{params['table_id']}`,
                        UNNEST(event_params) as event_params
                        WHERE event_name = '{params['event_name']}'
                        GROUP BY 1, 2
                        ORDER BY event_count DESC
                        LIMIT 10
                        """
                        
                        job_config = bigquery.QueryJobConfig(maximum_bytes_billed=100000000)
                        query_job = client.query(query, job_config=job_config)
                        api_response = query_job.result()
                        api_response = str([dict(row) for row in api_response])
                        api_requests_and_responses.append(
                            [response.function_call.name, params, api_response]
                        )
                    except Exception as e:
                        api_response = f"{str(e)}"
                        api_requests_and_responses.append(
                            [response.function_call.name, params, api_response]
                        )

                print(api_response)

                response = chat.send_message(
                    Part.from_function_response(
                        name=response.function_call.name,
                        response={
                            "content": api_response,
                        },
                    ),
                )
                response = response.candidates[0].content.parts[0]

                backend_details += "- Function call:\n"
                backend_details += (
                    "   - Function name: ```"
                    + str(api_requests_and_responses[-1][0])
                    + "```"
                )
                backend_details += "\n\n"
                backend_details += (
                    "   - Function parameters: ```"
                    + str(api_requests_and_responses[-1][1])
                    + "```"
                )
                backend_details += "\n\n"
                backend_details += (
                    "   - API response: ```"
                    + str(api_requests_and_responses[-1][2])
                    + "```"
                )
                backend_details += "\n\n"
                with message_placeholder.container():
                    st.markdown(backend_details)

            except AttributeError:
                function_calling_in_process = False

        time.sleep(3)

        full_response = response.text
        with message_placeholder.container():
            st.markdown(full_response.replace("$", "\$"))  # noqa: W605
            with st.expander("Function calls, parameters, and responses:"):
                st.markdown(backend_details)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": full_response,
                "backend_details": backend_details,
            }
        )
