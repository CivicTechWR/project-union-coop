# Flask Business Search Application

## Requirements

Install Flask:
```bash
pip install flask
```

## Running the Application

1. Navigate to the directory:
```bash
cd etl/data_analysis
```

2. Run the Flask app:
```bash
python app.py
```

3. Open your browser and go to:
```
http://127.0.0.1:5000
```

## Features

- **Search**: Search across all fields or specific columns (Business Name, Corporation Number, Location)
- **Filters**: Filter by Business Type, Status, and City
- **Pagination**: Browse through results with page navigation
- **Statistics**: View comprehensive statistics about the data
- **Export**: Export search results to CSV
- **Responsive Design**: Works on desktop and mobile devices

## File Structure

```
etl/data_analysis/
├── app.py                 # Flask application
├── templates/
│   └── index.html        # Main HTML template
├── static/
│   └── style.css         # Styles
└── README_FLASK.md       # This file
```
