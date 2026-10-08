import sys
import time
from extract import extract_text
from scoring import review_cv

print(f"{'File':<14}{'Score':>6}{'Found':>7}{'Quant':>7}{'Result':>8}")
for path in sys.argv[1:]:
    r = review_cv(extract_text(path))
    print(f"{path:<14}{str(r['percentage']) + '%':>6}"
          f"{r.get('statements_found', 0):>7}"
          f"{r.get('statements_quantified', 0):>7}"
          f"{r.get('statements_with_results', 0):>8}")
    time.sleep(2)