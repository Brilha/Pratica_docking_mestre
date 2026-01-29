#!/bin/bash
#
# cleanup_screening_results.sh
# Remove arquivos desnecessários que poluem screening_results
#
# O que remove:
# - *.pse (sessões PyMOL, podem ser recriadas com PLIP)
# - *.sdf (copias dos estruturais, originals estão em templates/)
# - log_docking.txt (logs, não necessários para análise)
# - config.txt (config do vina, pode ser recriado)
# - *_protonated.pdb (intermediário de processamento)
# - plipfixed_*.pdb (intermediário de PLIP)
#

SCREENING_DIR="/home/brilha/bioinformatica/codigos_mestres/screening_results"

echo "=================================="
echo "CLEANUP SCREENING RESULTS"
echo "=================================="
echo ""

total_removed=0

for drug_folder in "$SCREENING_DIR"/ctr3_*; do
    if [ -d "$drug_folder" ]; then
        drug_name=$(basename "$drug_folder")
        echo "Processing: $drug_name"
        
        # Remover .pse (PyMOL sessions, podem ser recriadas)
        pse_files=$(find "$drug_folder" -maxdepth 1 -name "*.pse" 2>/dev/null)
        if [ -n "$pse_files" ]; then
            echo "$pse_files" | while read file; do
                echo "  ❌ Removing: $(basename "$file")"
                rm -f "$file"
                ((total_removed++))
            done
        fi
        
        # Remover .sdf (copias dos originals)
        sdf_files=$(find "$drug_folder" -maxdepth 1 -name "*.sdf" 2>/dev/null)
        if [ -n "$sdf_files" ]; then
            echo "$sdf_files" | while read file; do
                echo "  ❌ Removing: $(basename "$file")"
                rm -f "$file"
                ((total_removed++))
            done
        fi
        
        # Remover log_docking.txt
        if [ -f "$drug_folder/log_docking.txt" ]; then
            echo "  ❌ Removing: log_docking.txt"
            rm -f "$drug_folder/log_docking.txt"
            ((total_removed++))
        fi
        
        # Remover config.txt (pode ser recriado se necessário)
        if [ -f "$drug_folder/config.txt" ]; then
            echo "  ❌ Removing: config.txt"
            rm -f "$drug_folder/config.txt"
            ((total_removed++))
        fi
        
        # Remover *_protonated.pdb (intermediário)
        protonated=$(find "$drug_folder" -maxdepth 1 -name "*_protonated.pdb" 2>/dev/null)
        if [ -n "$protonated" ]; then
            echo "$protonated" | while read file; do
                echo "  ❌ Removing: $(basename "$file")"
                rm -f "$file"
                ((total_removed++))
            done
        fi
        
        # Remover plipfixed_*.pdb (intermediário de PLIP)
        plipfixed=$(find "$drug_folder" -maxdepth 1 -name "plipfixed*" 2>/dev/null)
        if [ -n "$plipfixed" ]; then
            echo "$plipfixed" | while read file; do
                echo "  ❌ Removing: $(basename "$file")"
                rm -f "$file"
                ((total_removed++))
            done
        fi
        
        # Remover *.png (imagens 2D, podem ser recriadas)
        png_files=$(find "$drug_folder" -maxdepth 1 -name "*.png" 2>/dev/null)
        if [ -n "$png_files" ]; then
            echo "$png_files" | while read file; do
                echo "  ❌ Removing: $(basename "$file")"
                rm -f "$file"
                ((total_removed++))
            done
        fi
        
        # Remover *.txt intermediários (mas manter complexo_final_report.txt)
        txt_files=$(find "$drug_folder" -maxdepth 1 -name "*_report.txt" ! -name "complexo_final_report.txt" 2>/dev/null)
        if [ -n "$txt_files" ]; then
            echo "$txt_files" | while read file; do
                echo "  ❌ Removing: $(basename "$file")"
                rm -f "$file"
                ((total_removed++))
            done
        fi
        
        echo ""
    fi
done

echo "=================================="
echo "✅ CLEANUP COMPLETE"
echo "Total items removed: $total_removed"
echo "=================================="
echo ""
echo "Remaining files in each folder:"
for drug_folder in "$SCREENING_DIR"/ctr3_*; do
    echo ""
    drug_name=$(basename "$drug_folder")
    echo "📁 $drug_name: $(ls -1 "$drug_folder" | wc -l) files"
done
