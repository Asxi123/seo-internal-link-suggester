import pandas as pd
import os


def save_csv_report(df, output_path):
    """
    Save report as CSV and Excel.
    """

    if df.empty:
        print("No link suggestions generated.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save CSV
    df.to_csv(output_path, index=False, encoding="utf-8")

    print(f"Report saved to: {output_path}")

    # Save Excel version
    excel_path = output_path.replace(".csv", ".xlsx")

    df.to_excel(excel_path, index=False)

    print(f"Excel report saved to: {excel_path}")
