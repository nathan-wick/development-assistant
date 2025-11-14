model_parameters_billions = 7
average_upfront_hardware_cost_per_billion_parameters = 225
average_monthly_watts_per_billion_parameters = 50
average_electricity_cost_per_kwh = 0.12
average_hours_running_per_month = 730
monthly_maintenance_rate = 0.015

estimated_upfront_hardware_cost = model_parameters_billions * average_upfront_hardware_cost_per_billion_parameters

total_monthly_watts = model_parameters_billions * average_monthly_watts_per_billion_parameters

monthly_power_cost = (total_monthly_watts / 1000) * average_hours_running_per_month * average_electricity_cost_per_kwh

monthly_maintenance_cost = estimated_upfront_hardware_cost * monthly_maintenance_rate

monthly_operating_cost = monthly_power_cost + monthly_maintenance_cost

print(f"Hardware Cost: ${estimated_upfront_hardware_cost:,.2f}")
print(f"Power Cost: ${monthly_power_cost:.2f}")
print(f"Maintenance Cost: ${monthly_maintenance_cost:.2f}")
print(f"Total Monthly: ${monthly_operating_cost:.2f}")