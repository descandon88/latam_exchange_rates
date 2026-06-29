"""Manual smoke test for the real BCU SOAP extractor.

Walks backward from an end date (today by default, or an explicit
YYYY-MM-DD passed as the first CLI arg) until it finds a published quote,
exercising the live `awsbcucotizaciones` call, the weekend/holiday skip path
(`BCUNoQuoteForDateError`), and the generic service-error path in one run.
Pass an explicit past date to rule out the container clock being ahead of
what BCU's live database actually has data for.
Meant to be run inside the `bcu-extractor` docker-compose service.
"""
import sys
from datetime import date, datetime, timedelta

from src.extractors.bcu import BCUNoQuoteForDateError, BCUServiceError, fetch_bcu_rate

MAX_DAYS_BACK = 8

if __name__ == "__main__":
    end_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date() if len(sys.argv) > 1 else date.today()
    for offset in range(MAX_DAYS_BACK):
        rate_date = end_date - timedelta(days=offset)
        try:
            raw = fetch_bcu_rate(rate_date)
        except BCUNoQuoteForDateError as exc:
            print(f"{rate_date}: no quote ({exc})")
            continue
        except BCUServiceError as exc:
            print(f"{rate_date}: service error ({exc})")
            continue
        print(f"{rate_date}: {raw}")
        break
    else:
        print(f"No quote found in the last {MAX_DAYS_BACK} days.")
