#!/bin/bash

BASE_DIRS=("./Data")

for DIR in "${BASE_DIRS[@]}"; do
  if [ -d "$DIR" ]; then
    for FILE in "$DIR"/*.csv; do
      if [ -f "$FILE" ]; then
        BASENAME=$(basename "$FILE")
        OUTPUT_FILE="${DIR}/${BASENAME%.*}.txt"
        ./DualEloRating -f "$FILE" -opt 2 -n 30 -t 10 -v 2 > "$OUTPUT_FILE"
				if [[ $? -eq 0 ]]; then
						echo "$BASENAME processed successfully."
				else
						echo "Error: Failed to process the file."
						exit 1
				fi
				sleep 120
      fi
    done
  else
    echo "Directory $DIR does not exist."
  fi
done
