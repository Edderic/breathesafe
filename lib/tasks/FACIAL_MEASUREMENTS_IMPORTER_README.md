# Facial Measurements Importer

## Overview
A flexible, reusable class for importing facial measurements from CSV strings into the Breathesafe database.

## File Location
- **Class**: `lib/tasks/facial_measurements_importer.rb`

## Usage

### Basic Example
```ruby
# Read CSV file
csv_string = File.read('./data/wayne-community-fit-testing-breathesafe - facial_measurements.csv')

# Create importer instance
importer = FacialMeasurementsImporter.new(
  csv_string: csv_string,
  manager_email: 'wilier-tome-02@icloud.com',
  source: 'wcft'
)

# Run import
importer.import
```

### Using rails runner
```bash
rails runner "
csv_string = File.read('./data/wayne-community-fit-testing-breathesafe - facial_measurements.csv')
importer = FacialMeasurementsImporter.new(
  csv_string: csv_string,
  manager_email: 'wilier-tome-02@icloud.com',
  source: 'wcft'
)
importer.import
"
```

### Create a Wrapper Script
You can create a dedicated runner script for specific imports:

```ruby
# lib/tasks/import_wayne_measurements.rb
require_relative 'facial_measurements_importer'

csv_string = File.read('./data/wayne-community-fit-testing-breathesafe - facial_measurements.csv')
importer = FacialMeasurementsImporter.new(
  csv_string: csv_string,
  manager_email: 'wilier-tome-02@icloud.com',
  source: 'wcft'
)
importer.import
```

Then run:
```bash
rails runner lib/tasks/import_wayne_measurements.rb
```

## Parameters

### `csv_string` (required)
- **Type**: String
- **Description**: The CSV data as a string
- **Example**: `File.read('path/to/file.csv')`

### `manager_email` (required)
- **Type**: String
- **Description**: Email of the manager user who manages the users in the CSV
- **Example**: `'wilier-tome-02@icloud.com'`

### `source` (required)
- **Type**: String
- **Description**: Source identifier for these measurements (stored in `FacialMeasurement.source`)
- **Example**: `'wcft'` (Wayne Community Fit Testing)

## CSV Structure

The CSV must contain the following columns:
- `anonymous_first_name` - UUID used to match existing managed users
- `anonymous_last_name` - (not used)
- `face_width_mm` - Face width in millimeters
- `face_length_mm` - Face length in millimeters
- `nose_bridge_height_mm` - Nose bridge height in millimeters
- `nasal_root_breadth_mm` - Nasal root breadth in millimeters
- `nose_protrusion_mm` - Nose protrusion in millimeters
- `bitragion_subnasale_arc_mm` - Bitragion subnasale arc in millimeters
- `date` - Measurement date (supports formats: YYYY-MM-DD and MM/DD/YY)

## How It Works

1. **User Matching**: Matches rows to existing managed users by comparing `anonymous_first_name` (UUID) with the `first_name` field in the user's profile
2. **Manager**: Only processes users managed by the specified manager email
3. **Update Strategy**: Updates existing facial measurements if found, creates new ones if not
4. **Date Handling**: Parses both `YYYY-MM-DD` and `MM/DD/YY` date formats
5. **Example Row**: Automatically skips rows with `anonymous_first_name = 'EXAMPLE'`

## Output

The importer provides real-time progress updates and a summary:

```
Starting import...
Manager: wilier-tome-02@icloud.com (ID: 123)
Source: wcft
--------------------------------------------------------------------------------
⊘ Skipped example row
✓ Updated facial measurement for user: b10c9dfa-533e-494a-993a-efe12c7fb9a1 (ID: 456)
✓ Created facial measurement for user: 4f9aa562-68de-4f1c-bd7f-04c52440ea67 (ID: 457)
...
--------------------------------------------------------------------------------
Import Summary:
  Total rows processed: 28
  Created: 15
  Updated: 12
  Skipped: 1

No errors!
--------------------------------------------------------------------------------
```

## Fields Mapped

### Imported from CSV:
- `face_width` ← `face_width_mm`
- `face_length` ← `face_length_mm`
- `nose_bridge_height` ← `nose_bridge_height_mm`
- `nasal_root_breadth` ← `nasal_root_breadth_mm`
- `nose_protrusion` ← `nose_protrusion_mm`
- `bitragion_subnasale_arc` ← `bitragion_subnasale_arc_mm`
- `source` ← parameter value
- `created_at` ← parsed from `date` column
- `updated_at` ← parsed from `date` column

### Left as nil:
- `jaw_width`
- `face_depth`
- `lower_face_length`
- `bitragion_menton_arc`
- `cheek_fullness`
- `lip_width`
- `head_circumference`
- `nose_breadth`
- `arkit`

## Error Handling

The importer handles various error cases:
- Missing manager user
- Missing `anonymous_first_name`
- No matching managed user found
- Invalid date format
- Database validation errors
- General exceptions

All errors are collected and displayed in the summary.

## Prerequisites

1. **Manager user must exist**: User with the specified email must exist in the database
2. **Managed users must exist**: Users with matching UUIDs in their `first_name` field must already be created as managed users under the manager
3. **CSV must be valid**: CSV string must be properly formatted with required headers

## Troubleshooting

### "Manager user not found"
- Verify the manager email exists: `User.find_by(email: 'your-email@example.com')`
- Check for typos in the email address

### "No managed user found with first_name"
- The UUID in the CSV doesn't match any managed user's profile first_name
- Check if managed users exist:
  ```ruby
  manager = User.find_by(email: 'your-email@example.com')
  ManagedUser.joins(managed: :profile)
             .where(manager_id: manager.id)
             .pluck('profiles.first_name')
  ```

### Date parsing errors
- Check the date format in the CSV
- Supported formats: `YYYY-MM-DD` and `MM/DD/YY`
- Add additional formats to the `parse_date` method if needed

## Extending the Importer

### Adding New Date Formats
Edit the `parse_date` method to add new format support:

```ruby
def parse_date(date_string)
  # ... existing code ...

  # Add new format
  begin
    return Date.strptime(date_string, '%d/%m/%Y')
  rescue ArgumentError
    nil
  end
end
```

### Adding New CSV Columns
Update the `facial_data` hash in `process_row`:

```ruby
facial_data = {
  # ... existing fields ...
  jaw_width: row[:jaw_width_mm]&.to_f,
  # ... more fields ...
}
```

## Notes

- The importer uses `update` for existing measurements, which overwrites all specified fields
- The `created_at` timestamp is set to the date from the CSV, not the current time
- Rows are processed sequentially with real-time progress reporting
- All errors are collected and displayed in the summary
- The class is reusable for different CSV sources by changing the `source` parameter
