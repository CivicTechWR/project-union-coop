#!/usr/bin/env python3
"""
JSON Data Analysis Script
Analyzes the number of entries with specific keys in all_businesses.json
"""

import json
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime


def load_json_data(file_path):
    """Load JSON data from file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_by_key(data, key_name):
    """Count occurrences of values for a specific key"""
    counter = Counter()
    missing_count = 0
    
    for entry in data:
        value = entry.get(key_name)
        if value:
            counter[value] += 1
        else:
            missing_count += 1
    
    return counter, missing_count


def analyze_location_breakdown(data):
    """Analyze location data by city, province, and country"""
    cities = Counter()
    provinces = Counter()
    countries = Counter()
    missing = 0
    
    for entry in data:
        location = entry.get('Location', '')
        if location:
            parts = [part.strip() for part in location.split(',')]
            if len(parts) >= 1:
                cities[parts[0]] += 1
            if len(parts) >= 2:
                provinces[parts[1]] += 1
            if len(parts) >= 3:
                countries[parts[2]] += 1
        else:
            missing += 1
    
    return cities, provinces, countries, missing


def analyze_date_patterns(data, date_key):
    """Analyze date patterns by year and month"""
    years = Counter()
    months = Counter()
    invalid_dates = 0
    missing = 0
    
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    for entry in data:
        date_str = entry.get(date_key)
        if date_str:
            try:
                # Parse date format: "Month Day, Year"
                parts = date_str.replace(',', '').split()
                if len(parts) == 3:
                    month, day, year = parts
                    years[year] += 1
                    months[month] += 1
                else:
                    invalid_dates += 1
            except Exception:
                invalid_dates += 1
        else:
            missing += 1
    
    return years, months, invalid_dates, missing


def print_analysis_report(data, output_file=None):
    """Generate and print comprehensive analysis report"""
    report_lines = []
    
    def log(message):
        """Helper to print and store output"""
        print(message)
        report_lines.append(message)
    
    log("=" * 80)
    log("JSON DATA ANALYSIS REPORT")
    log(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 80)
    log(f"\nTotal Entries: {len(data):,}")
    log("\n")
    
    # Analyze all available keys
    if data:
        available_keys = list(data[0].keys())
        log("Available Keys:")
        for key in available_keys:
            log(f"  - {key}")
        log("\n")
    
    # Business Type Analysis
    log("-" * 80)
    log("BUSINESS TYPE ANALYSIS")
    log("-" * 80)
    business_types, bt_missing = analyze_by_key(data, 'Business Type')
    for btype, count in business_types.most_common():
        percentage = (count / len(data)) * 100
        log(f"  {btype}: {count:,} ({percentage:.2f}%)")
    if bt_missing:
        log(f"  Missing: {bt_missing:,}")
    log(f"\nUnique Business Types: {len(business_types)}")
    log("\n")
    
    # Status Analysis
    log("-" * 80)
    log("STATUS ANALYSIS")
    log("-" * 80)
    statuses, status_missing = analyze_by_key(data, 'Status')
    for status, count in statuses.most_common():
        percentage = (count / len(data)) * 100
        log(f"  {status}: {count:,} ({percentage:.2f}%)")
    if status_missing:
        log(f"  Missing: {status_missing:,}")
    log("\n")
    
    # Location Analysis
    log("-" * 80)
    log("LOCATION ANALYSIS")
    log("-" * 80)
    cities, provinces, countries, loc_missing = analyze_location_breakdown(data)
    
    log(f"\nTop 20 Cities:")
    for city, count in cities.most_common(20):
        percentage = (count / len(data)) * 100
        log(f"  {city}: {count:,} ({percentage:.2f}%)")
    
    log(f"\nProvinces/States:")
    for province, count in provinces.most_common():
        percentage = (count / len(data)) * 100
        log(f"  {province}: {count:,} ({percentage:.2f}%)")
    
    log(f"\nCountries:")
    for country, count in countries.most_common():
        percentage = (count / len(data)) * 100
        log(f"  {country}: {count:,} ({percentage:.2f}%)")
    
    if loc_missing:
        log(f"\nMissing Location: {loc_missing:,}")
    
    log(f"\nUnique Cities: {len(cities):,}")
    log(f"Unique Provinces: {len(provinces):,}")
    log(f"Unique Countries: {len(countries):,}")
    log("\n")
    
    # Date Analysis
    log("-" * 80)
    log("INCORPORATION DATE ANALYSIS")
    log("-" * 80)
    years, months, invalid_dates, date_missing = analyze_date_patterns(
        data, 'Amalgamation/Inc. Date'
    )
    
    log(f"\nTop 10 Years:")
    for year, count in years.most_common(10):
        percentage = (count / len(data)) * 100
        log(f"  {year}: {count:,} ({percentage:.2f}%)")
    
    log(f"\nMonth Distribution:")
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    for month in month_order:
        if month in months:
            count = months[month]
            percentage = (count / len(data)) * 100
            log(f"  {month}: {count:,} ({percentage:.2f}%)")
    
    if invalid_dates:
        log(f"\nInvalid Dates: {invalid_dates:,}")
    if date_missing:
        log(f"Missing Dates: {date_missing:,}")
    
    log(f"\nDate Range: {min(years.keys()) if years else 'N/A'} - {max(years.keys()) if years else 'N/A'}")
    log("\n")
    
    # Corporation Number Analysis
    log("-" * 80)
    log("CORPORATION NUMBER ANALYSIS")
    log("-" * 80)
    corp_numbers, corp_missing = analyze_by_key(data, 'Corporation Number')
    log(f"Total Corporation Numbers: {len(corp_numbers):,}")
    log(f"Unique Corporation Numbers: {len(corp_numbers):,}")
    if corp_missing:
        log(f"Missing Corporation Numbers: {corp_missing:,}")
    
    # Check for duplicates
    duplicates = {num: count for num, count in corp_numbers.items() if count > 1}
    if duplicates:
        log(f"\nDuplicate Corporation Numbers Found: {len(duplicates)}")
        log("Top 10 Duplicates:")
        for num, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
            log(f"  {num}: {count} occurrences")
    else:
        log("\nNo duplicate Corporation Numbers found.")
    log("\n")
    
    # Business Name Analysis
    log("-" * 80)
    log("BUSINESS NAME ANALYSIS")
    log("-" * 80)
    names, names_missing = analyze_by_key(data, 'Business Name')
    log(f"Total Business Names: {len(names):,}")
    log(f"Unique Business Names: {len(names):,}")
    if names_missing:
        log(f"Missing Business Names: {names_missing:,}")
    
    # Check for duplicate names
    duplicate_names = {name: count for name, count in names.items() if count > 1}
    if duplicate_names:
        log(f"\nDuplicate Business Names Found: {len(duplicate_names)}")
        log("Top 10 Most Common Names:")
        for name, count in sorted(duplicate_names.items(), key=lambda x: x[1], reverse=True)[:10]:
            log(f"  {name}: {count} occurrences")
    else:
        log("\nNo duplicate Business Names found.")
    
    log("\n")
    log("=" * 80)
    log("END OF REPORT")
    log("=" * 80)
    
    # Save report to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        print(f"\nReport saved to: {output_file}")


def main():
    """Main execution function"""
    # Path to JSON file
    script_dir = Path(__file__).parent
    json_file = script_dir.parent / 'output' / 'all_businesses.json'
    
    if not json_file.exists():
        print(f"Error: File not found at {json_file}")
        return
    
    print(f"Loading data from: {json_file}")
    data = load_json_data(json_file)
    
    # Generate report in the same folder as the script
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = script_dir / f'analysis_report_{timestamp}.txt'
    
    print_analysis_report(data, output_file)


if __name__ == "__main__":
    main()
