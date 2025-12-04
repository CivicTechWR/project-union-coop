#!/usr/bin/env python3
"""
Flask Web Application for Business Data Search
Allows searching through the all_businesses.json data
"""

from flask import Flask, render_template, request, jsonify
import json
from pathlib import Path
from collections import Counter

app = Flask(__name__)

# Custom Jinja filter for number formatting
@app.template_filter('number_format')
def number_format(value):
    """Format number with thousands separator"""
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return value

# Load data once at startup
DATA_FILE = Path(__file__).parent.parent / 'output' / 'all_businesses.json'
business_data = []

def load_data():
    """Load JSON data from file"""
    global business_data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            business_data = json.load(f)
        print(f"Loaded {len(business_data):,} business records")
    except Exception as e:
        print(f"Error loading data: {e}")
        business_data = []

# Load data on startup
load_data()

@app.route('/')
def index():
    """Main search page"""
    # Get unique values for filters
    business_types = sorted(set(entry.get('Business Type', '') for entry in business_data if entry.get('Business Type')))
    statuses = sorted(set(entry.get('Status', '') for entry in business_data if entry.get('Status')))
    
    # Get cities
    cities = set()
    for entry in business_data:
        location = entry.get('Location', '')
        if location:
            city = location.split(',')[0].strip()
            if city:
                cities.add(city)
    cities = sorted(cities)
    
    return render_template('index.html', 
                         business_types=business_types,
                         statuses=statuses,
                         cities=cities[:100],  # Limit to top 100 for dropdown
                         total_records=len(business_data))

@app.route('/search', methods=['POST'])
def search():
    """Search endpoint"""
    data = request.get_json()
    
    search_term = data.get('searchTerm', '').lower()
    business_type = data.get('businessType', '')
    status = data.get('status', '')
    city = data.get('city', '')
    search_field = data.get('searchField', 'all')
    page = int(data.get('page', 1))
    per_page = 50
    
    # Filter results
    results = []
    for entry in business_data:
        # Apply filters
        if business_type and entry.get('Business Type') != business_type:
            continue
        if status and entry.get('Status') != status:
            continue
        if city:
            location = entry.get('Location', '')
            if not location.startswith(city):
                continue
        
        # Apply search term
        if search_term:
            if search_field == 'all':
                # Search all fields
                match = any(search_term in str(value).lower() for value in entry.values())
            else:
                # Search specific field
                field_value = str(entry.get(search_field, '')).lower()
                match = search_term in field_value
            
            if match:
                results.append(entry)
        else:
            # No search term, just apply filters
            results.append(entry)
    
    # Pagination
    total_results = len(results)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_results = results[start_idx:end_idx]
    
    return jsonify({
        'results': paginated_results,
        'total': total_results,
        'page': page,
        'per_page': per_page,
        'total_pages': (total_results + per_page - 1) // per_page
    })

@app.route('/stats')
def stats():
    """Statistics endpoint"""
    # Business type distribution
    business_types = Counter(entry.get('Business Type', 'Unknown') for entry in business_data)
    
    # Status distribution
    statuses = Counter(entry.get('Status', 'Unknown') for entry in business_data)
    
    # Top cities
    cities = Counter()
    for entry in business_data:
        location = entry.get('Location', '')
        if location:
            city = location.split(',')[0].strip()
            if city:
                cities[city] += 1
    
    # Year distribution
    years = Counter()
    for entry in business_data:
        date_str = entry.get('Amalgamation/Inc. Date', '')
        if date_str:
            try:
                year = date_str.split()[-1]
                years[year] += 1
            except:
                pass
    
    return jsonify({
        'total_records': len(business_data),
        'business_types': dict(business_types.most_common()),
        'statuses': dict(statuses),
        'top_cities': dict(cities.most_common(20)),
        'top_years': dict(sorted(years.items(), key=lambda x: x[0], reverse=True)[:10])
    })

@app.route('/export', methods=['POST'])
def export():
    """Export search results"""
    data = request.get_json()
    results = data.get('results', [])
    
    # Convert to CSV format
    if not results:
        return jsonify({'error': 'No results to export'}), 400
    
    # Get headers from first result
    headers = list(results[0].keys())
    
    # Create CSV content
    csv_lines = [','.join(f'"{h}"' for h in headers)]
    for result in results:
        row = ','.join(f'"{result.get(h, "")}"' for h in headers)
        csv_lines.append(row)
    
    csv_content = '\n'.join(csv_lines)
    
    return jsonify({
        'csv': csv_content,
        'filename': 'search_results.csv'
    })

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
