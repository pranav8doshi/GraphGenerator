from flask import Flask, render_template, request, jsonify
import pandas as pd
import plotly
import plotly.express as px
import json

app = Flask(__name__)

data = None  # To store the uploaded DataFrame globally


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    global data
    file = request.files.get("file")
    if file:
        data = pd.read_excel(file)
        columns = list(data.columns)
        return jsonify({"columns": columns})
    return jsonify({"error": "File upload failed"}), 400


@app.route("/generate", methods=["POST"])
def generate():
    global data
    if data is None:
        return jsonify({"error": "No data available"}), 400

    x_axis = request.json.get("x_axis")
    y_axis = request.json.get("y_axis")
    graph_type = request.json.get("graph_type")

    if not x_axis or not graph_type:
        return jsonify({"error": "X-axis and graph type are required"}), 400

    try:
        if graph_type == "Scatter Plot":
            fig = px.scatter(data, x=x_axis, y=y_axis, title="Scatter Plot")
        elif graph_type == "Line Chart":
            fig = px.line(data, x=x_axis, y=y_axis, title="Line Chart")
        elif graph_type == "Bar Chart":
            fig = px.bar(data, x=x_axis, y=y_axis, title="Bar Chart")
        elif graph_type == "Histogram":
            fig = px.histogram(data, x=x_axis, title="Histogram")
        elif graph_type == "Pie Chart":
            fig = px.pie(data, names=x_axis, values=y_axis, title="Pie Chart")
        elif graph_type == "Area Chart":
            fig = px.area(data, x=x_axis, y=y_axis, title="Area Chart")
        elif graph_type == "Bubble Chart":
            fig = px.scatter(data, x=x_axis, y=y_axis, size=y_axis, title="Bubble Chart")
        elif graph_type == "Box Plot":
            fig = px.box(data, x=x_axis, y=y_axis, title="Box Plot")
        elif graph_type == "Treemap":
            fig = px.treemap(data, path=[x_axis], values=y_axis, title="Treemap")
        elif graph_type == "Heatmap":
            fig = px.imshow(data.corr(), title="Heatmap", color_continuous_scale="Viridis")
        elif graph_type == "Funnel Chart":
            fig = px.funnel(data, x=x_axis, y=y_axis, title="Funnel Chart")
        elif graph_type == "Sunburst Chart":
            fig = px.sunburst(data, path=[x_axis], values=y_axis, title="Sunburst Chart")
        else:
            return jsonify({"error": "Invalid graph type"}), 400

        graph_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return jsonify({"graph": graph_json})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
