# Script to fix the app.py file by removing misplaced lines

# Read the original file
with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the indices of the problematic section
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    # Look for the line after the reading history page route
    if line.strip() == "return render_template('reading_history.html', username=session.get('username', 'User'))":
        start_idx = i + 1  # Start after this line
    # Look for the continue reading page route
    elif line.strip() == "# Route to serve the continue reading page" and i > 1660:  # Make sure it's the second one
        end_idx = i
        break

# If we found both indices, remove the problematic lines
if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
    print(f"Removing lines {start_idx} to {end_idx-1}")
    # Keep lines from 0 to start_idx-1 (inclusive)
    # Skip lines from start_idx to end_idx-1 (these are the problematic lines)
    # Keep lines from end_idx to the end
    fixed_lines = lines[:start_idx] + lines[end_idx:]
    
    # Write the fixed file
    with open('app_fixed.py', 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("Fixed file written to app_fixed.py")
else:
    print("Could not find the problematic section")
    print(f"start_idx: {start_idx}, end_idx: {end_idx}")