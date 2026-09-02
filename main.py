from datetime import datetime
from tabulate import tabulate
from database import init_db, seed_classic_repertoire
from scraper import scrape_latest_gospel_charts
from scheduler import generate_monthly_schedule

def main():
    print("Initializing Database & Schema...")
    init_db()
    seed_classic_repertoire()

    print("\nSynchronizing Contemporary Charts...")
    scrape_latest_gospel_charts()

    today = datetime.today()
    target_year = today.year
    target_month = today.month

    print(f"\nGenerating Schedule for {datetime(target_year, target_month, 1).strftime('%B %Y')}...")
    schedule = generate_monthly_schedule(target_year, target_month)

    for sunday_date, lineup in schedule.items():
        print(f"\n=======================================================")
        print(f" SERVICE DATE: {sunday_date}")
        print(f"=======================================================")
        table_data = [
            [item["slot"], item["title"], item["artist"], item["ensemble"].replace("_", " ").title(), item["key"]]
            for item in lineup
        ]
        print(tabulate(table_data, headers=["Order", "Song Title", "Artist", "Ensemble", "Key"], tablefmt="fancy_grid"))

if __name__ == "__main__":
    main()
