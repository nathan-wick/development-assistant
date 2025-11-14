average_lines_per_hour = 20
average_hours_per_day = 8
average_input_tokens_per_line = 10
average_output_tokens_per_line = 10
input_token_cost_per_million = 1.25
output_token_cost_per_million = 10
number_of_developers = 10
average_working_days_per_month = 22

developer_daily_input_cost = (
    average_lines_per_hour
    * average_hours_per_day
    * average_input_tokens_per_line
    * (input_token_cost_per_million / 1_000_000)
)

developer_daily_output_cost = (
    average_lines_per_hour
    * average_hours_per_day
    * average_output_tokens_per_line
    * (output_token_cost_per_million / 1_000_000)
)

developer_daily_cost = developer_daily_input_cost + developer_daily_output_cost

estimated_monthly_api_cost = (
    developer_daily_cost * number_of_developers * average_working_days_per_month
)

print(f"Estimated Monthly API Cost: ${estimated_monthly_api_cost:.2f}")