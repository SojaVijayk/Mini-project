# Script to fix indentation issues in app.py

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the problematic lines
fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this is the problematic section
    if line.strip() == "# Route to save reading position" and i > 0 and lines[i-1].strip() == "return render_template('reading_history.html', username=session.get('username', 'User'))":
        # Skip the misplaced code
        fixed_lines.append(line)
        i += 1
        
        # Skip lines until we reach the continue reading route
        while i < len(lines) and not lines[i].strip().startswith("# Route to serve the continue reading page"):
            # Check if this line looks like misplaced code from the continue_reading_books function
            if "print(f\"Additional book with position:" in lines[i] or \
               "continue_reading_books.append(book_info)" in lines[i] or \
               "return jsonify({'success': True, 'continue_reading':" in lines[i] or \
               "traceback.print_exc()" in lines[i]:
                print(f"Skipping line {i}: {lines[i].strip()}")
            else:
                # Keep other lines
                fixed_lines.append(lines[i])
            i += 1
            
        # Add the continue reading route if we found it
        if i < len(lines):
            fixed_lines.append(lines[i])
            i += 1
    else:
        fixed_lines.append(line)
        i += 1

# Write the fixed file
with open('app_fixed.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Fixed file written to app_fixed.py")