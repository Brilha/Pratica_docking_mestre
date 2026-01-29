#!/bin/bash
#
# cleanup_duplicates.sh
# Remove recursive-named files from screening_results
# Example: ctr3_seletividade_seletividade.pdb (should be ctr3_seletividade.pdb)
#
# Usage: bash cleanup_duplicates.sh
#

SCREENING_DIR="/home/brilha/bioinformatica/codigos_mestres/screening_results"

echo "=================================="
echo "CLEANUP DUPLICATES - SCREENING RESULTS"
echo "=================================="
echo ""

# Counter
total_deleted=0

# Process each drug folder
for drug_folder in "$SCREENING_DIR"/ctr3_*; do
    if [ -d "$drug_folder" ]; then
        drug_name=$(basename "$drug_folder")
        echo "Processing: $drug_name"
        
        # Find all files with pattern *_seletividade_seletividade*
        duplicates=$(find "$drug_folder" -maxdepth 1 -name "*_seletividade_seletividade*" 2>/dev/null)
        
        if [ -n "$duplicates" ]; then
            count=$(echo "$duplicates" | wc -l)
            echo "  Found $count duplicate(s):"
            
            # Delete each duplicate
            while IFS= read -r file; do
                filename=$(basename "$file")
                echo "    ❌ Deleting: $filename"
                rm -f "$file"
                ((total_deleted++))
            done <<< "$duplicates"
        else
            echo "  ✅ No duplicates found"
        fi
        echo ""
    fi
done

echo "=================================="
echo "✅ CLEANUP COMPLETE"
echo "Total files deleted: $total_deleted"
echo "=================================="

# Verify cleanup
echo ""
echo "Verification - remaining *_seletividade* files:"
find "$SCREENING_DIR" -maxdepth 2 -name "*_seletividade*" | sed 's|.*/||' | sort

