import sys
import time
from extract import extract_text
from scoring import review_cv

path = sys.argv[1]
runs = int(sys.argv[2]) if len(sys.argv) > 2 else 5

text = extract_text(path)
scores = []

for i in range(runs):
    result = review_cv(text)
    scores.append(result["percentage"])
    print(f"Run {i + 1}: {result['percentage']}%")
    time.sleep(2)  # small pause to stay within free-tier rate limits

print()
print("Scores:", scores)
print("Lowest:", min(scores), " Highest:", max(scores))
print("Spread:", max(scores) - min(scores), "points")