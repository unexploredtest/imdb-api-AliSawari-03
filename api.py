from flask import Flask, jsonify, request
import pandas as pd

# from load_data import load_endpoint_1_data

app = Flask(__name__)

endpoint_1_df = pd.read_csv("endpoint_1_data.csv")

@app.route('/api/v1/same-director-writer-alive', methods=['GET'])
def get_same_director_writer_alive():

    # Total count required by the document
    total_count = len(endpoint_1_df)

    # Pagination setup
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    # Calculate pagination slice indices
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    # Slice data for the requested page
    paginated_data = endpoint_1_df.iloc[start_idx:end_idx][["primaryName", "title", "birthYear"]].to_dict(orient="records")

    # Convert birthYear to integer
    for record in paginated_data:
        record['birthYear'] = int(record['birthYear'])

    # 3. Response JSON layout
    return jsonify({
        "total": total_count,
        "page": page,
        "per_page": per_page,
        "data": paginated_data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)