from flask import Flask, render_template, request, Response
import pandas as pd
import os
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Global variable to store the dataframe
df = None

# Function to extract data from CSV into a DataFrame
def extract_csv_as_df(pathname: str) -> pd.DataFrame:
    """Extracts the content of the CSV into a pandas DataFrame."""
    return pd.read_csv(pathname)

def validate_columns(x_axis: str, y_axis: str, df: pd.DataFrame):
    """Validates the X-axis and Y-axis column names against the DataFrame."""
    valid_columns = df.columns.tolist()
    error = None
    suggestion = None

    if x_axis not in valid_columns:
        error = f"Error: '{x_axis}' is not a valid column. "
        suggestion = f"Did you mean one of these? {', '.join(valid_columns)}"
    elif y_axis not in valid_columns:
        error = f"Error: '{y_axis}' is not a valid column."
        suggestion = f"Did you mean one of these? {', '.join(valid_columns)}"
    
    return error, suggestion

def generate_graph(df: pd.DataFrame, chart_type: str, x_axis: str, y_axis: str) -> io.BytesIO:
    """Generates a graph based on the user's query and returns it as a byte stream."""
    try:
        plt.figure(figsize=(10, 6))

        if chart_type == 'bar':
            plt.bar(df[x_axis], df[y_axis])
            plt.xlabel(x_axis)
            plt.ylabel(y_axis)
            plt.title(f"{y_axis} by {x_axis}")

        elif chart_type == 'line':
            plt.plot(df[x_axis], df[y_axis], marker='o')
            plt.xlabel(x_axis)
            plt.ylabel(y_axis)
            plt.title(f"{y_axis} over {x_axis}")

        elif chart_type == 'pie':
            plt.pie(df[y_axis], labels=df[x_axis], autopct='%1.1f%%')
            plt.title(f"Pie chart of {y_axis}")

        elif chart_type == 'scatter':
            plt.scatter(df[x_axis], df[y_axis])
            plt.xlabel(x_axis)
            plt.ylabel(y_axis)
            plt.title(f"Scatter Plot of {y_axis} vs {x_axis}")

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save the graph to a byte stream
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()

        return img

    except Exception as e:
        return f"Error generating graph: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    global df
    graph_image = None
    if request.method == 'POST':
        if 'file' in request.files:  # If a file is uploaded
            file = request.files['file']
            if file.filename == '':
                return "Error: No selected file", 400

            if file and file.filename.endswith('.csv'):
                try:
                    # Extract CSV content into the global dataframe
                    df = extract_csv_as_df(file)

                    # Render template with dropdowns populated with column names
                    return render_template('GraphGenerator.html', columns=df.columns.tolist(), graph_image=None)

                except Exception as e:
                    return f"Error: {str(e)}", 500

        elif df is not None and 'x_axis' in request.form and 'y_axis' in request.form:  # When options are selected
            try:
                # Retrieve the user's selected columns and chart type
                x_axis = request.form.get('x_axis')
                y_axis = request.form.get('y_axis')
                chart_type = request.form.get('chart_type')

                # Validate the columns
                error, suggestion = validate_columns(x_axis, y_axis, df)
                if error:
                    return render_template('GraphGenerator.html', columns=df.columns.tolist(), error_message=error, suggestion=suggestion, graph_image=None)

                # Generate the graph based on the selected options
                img = generate_graph(df, chart_type, x_axis, y_axis)

                # Convert the image to base64 to pass to the template
                graph_image = base64.b64encode(img.getvalue()).decode('utf-8')

                return render_template('GraphGenerator.html', columns=df.columns.tolist(), graph_image=graph_image, error_message=None, suggestion=None)

            except Exception as e:
                return f"Error: {str(e)}", 500

    # If no file uploaded or no graph generated yet
    return render_template('GraphGenerator.html', columns=None, graph_image=None)

if __name__ == "__main__":
    app.run(debug=True)
