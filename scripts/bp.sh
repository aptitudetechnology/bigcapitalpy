#!/bin/bash

# BigCapitalPy Blueprint Configuration Diagnostic
echo "=== Blueprint Configuration Diagnostic ==="
echo "Analyzing modular reports setup..."
echo ""

WEBAPP_DIR="$HOME/bigcapitalpy/packages/webapp/src"

echo "=== 1. Blueprint Registration Analysis ==="
echo "Looking for Blueprint imports and registrations..."

# Find all Python files that mention Blueprint
echo ""
echo "Files with Blueprint references:"
find "$WEBAPP_DIR" -name "*.py" -exec grep -l "Blueprint" {} \; | while read file; do
    echo "📁 $file"
    echo "   Blueprint definitions:"
    grep -n "Blueprint\|register_blueprint" "$file" | sed 's/^/     /'
    echo ""
done

echo "=== 2. Route Handler Analysis ==="
echo "Comparing working vs failing route patterns..."

# Find route files in reports directory
echo ""
echo "Route files in reports module:"
find "$WEBAPP_DIR/routes" -name "*report*" -o -path "*/reports/*" | while read file; do
    echo "📄 $file"
    if [ -f "$file" ]; then
        echo "   render_template calls:"
        grep -n "render_template" "$file" | sed 's/^/     /' || echo "     No render_template calls found"
        echo "   Route definitions:"
        grep -n "@.*route" "$file" | sed 's/^/     /' || echo "     No route definitions found"
    fi
    echo ""
done

echo "=== 3. Template Path Resolution ==="
echo "Checking template_folder configurations..."

# Look for template_folder in Blueprint definitions
echo ""
echo "Blueprint template_folder configurations:"
find "$WEBAPP_DIR" -name "*.py" -exec grep -l "template_folder" {} \; | while read file; do
    echo "📁 $file"
    grep -n -A2 -B2 "template_folder" "$file" | sed 's/^/     /'
    echo ""
done

echo "=== 4. Flask App Template Configuration ==="
echo "Looking for main Flask app template configuration..."

# Find main app file
echo ""
echo "Main Flask app files:"
find "$WEBAPP_DIR" -name "*.py" -exec grep -l "Flask(" {} \; | while read file; do
    echo "📄 $file"
    echo "   Flask app initialization:"
    grep -n -A3 -B1 "Flask(" "$file" | sed 's/^/     /'
    echo "   Template folder config:"
    grep -n "template_folder" "$file" | sed 's/^/     /' || echo "     No explicit template_folder config"
    echo ""
done

echo "=== 5. Working vs Failing Route Comparison ==="
echo "Let's find the working routes (invoice_summary, tax_summary)..."

# Search for working route handlers
echo ""
echo "Working route handlers (invoice_summary, tax_summary):"
find "$WEBAPP_DIR" -name "*.py" -exec grep -l -i "invoice_summary\|tax_summary" {} \; | while read file; do
    echo "📄 $file"
    echo "   Functions:"
    grep -n -A5 -B2 "def.*\(invoice_summary\|tax_summary\)" "$file" | sed 's/^/     /'
    echo ""
done

echo "=== 6. Template Directory Structure ==="
echo "Current template structure:"
find "$WEBAPP_DIR/templates" -name "*.html" | grep -E "(invoice|tax|report)" | sort

echo ""
echo "=== 7. Recent Changes Analysis ==="
echo "This should help identify what changed during modularization..."

# Check if we can see import structure
echo ""
echo "Import patterns in route files:"
find "$WEBAPP_DIR/routes" -name "*.py" -exec echo "📄 {}" \; -exec head -10 {} \; -exec echo "" \;

echo ""
echo "=== SUMMARY ==="
echo "Key things to check:"
echo "1. Are blueprints registered with correct template_folder paths?"
echo "2. Do modular blueprints have different template_folder than working ones?"
echo "3. Are render_template paths relative to blueprint template_folder or global?"
echo "4. Did the modularization change the blueprint registration order?"