from report.period import Period
from report.chrono import iter_period_starts
from report.generator import ReportRow, generate_user_orders_report


def print_report_by_rows(rows: list[ReportRow]):
    header = (
        f"| {'Period':<24} | {'NewUsers':>8} | {'Activated':>10} | {'Orders':>8} | "
        f"{'Item1Count':>12} | {'Item1Amount':>14} | {'Item2Count':>12} | {'Item2Amount':>14} | {'TotalAmount':>14} |"
    )
    print("-" * len(header))
    print(header)
    print("-" * len(header))

    for row in rows:
        print(
            f"| {row.period:<24} "
            f"| {row.new_users:<8} "
            f"| {row.activated_users:<10} "
            f"| {row.orders_count:<8} "
            f"| {row.orderitem1_count:<12} "
            f"| {row.orderitem1_amount:<14.2f} "
            f"| {row.orderitem2_count:<12} "
            f"| {row.orderitem2_amount:<14.2f} "
            f"| {row.orders_total_amount:<14.2f} "
            f"|"
        )


__all__ = (
    "Period",
    "ReportRow",
    "iter_period_starts",
    "print_report_by_rows",
    "generate_user_orders_report",
)
