# filename: stock_performance_analysis.py

import matplotlib.pyplot as plt

# Given data for the stocks
stock_data = {
    'ADANIPORTS.NS': {
        'name': 'Adani Ports and Special Economic Zone Limited',
        'current_price': 1077.05,
        'currency': 'INR',
        'PE_ratio': 22.674738,
        'forward_PE': 18.720848,
        'dividends': 0.0055,
        'price_to_book': 4.068654,
        'debt_to_equity': 85.449,
        'return_on_equity': 0.17819999,
        'normalized_prices': [100.0, 101.03405626474662, 100.0164096160751, 100.61551087402545, 98.4448131988613, 95.44932694527083, 96.34796881411572, 94.56709469250103, 92.92982975674498, 91.27615520491383, 87.53795850751436, 91.6782909795599, 92.64669876192553, 94.43988510463684, 95.4862535904801, 94.2716414585043, 90.78374650569347, 90.45958145260566, 90.60320065654494, 89.79483171227432, 88.79770209273697, 88.69100953400697, 90.02461642772876, 88.39146892311244]
    },
    'ZOMATO.NS': {
        'name': 'Zomato Limited',
        'current_price': 218.8,
        'currency': 'INR',
        'PE_ratio': 287.89474,
        'forward_PE': 113.9708,
        'dividends': 'N/A',
        'price_to_book': 9.303907,
        'debt_to_equity': 5.439,
        'return_on_equity': 0.03615,
        'normalized_prices': [100.0, 98.56433242718161, 98.0148862168189, 100.88621054445585, 96.72102098551329, 93.88514724325452, 89.48953969735346, 88.63877973827582, 86.97270499649875, 86.12193962842117, 80.52108790566011, 82.80751543755618, 86.45869855351442, 85.74973011794972, 88.19567446604786, 84.98759121331764, 76.05459000700249, 76.72810785718899, 78.6777710549919, 76.42679951747394, 73.09464462491994, 73.80361306048464, 78.87273845657216, 77.56114793257747]
    }
}

# Calculate percentage change for each stock
for stock, data in stock_data.items():
    normalized_prices = data['normalized_prices']
    percentage_change = ((normalized_prices[-1] - normalized_prices[0]) / normalized_prices[0]) * 100
    print(f'Percentage change for {data["name"]}: {percentage_change:.2f}%')

# Plotting the normalized prices
plt.figure(figsize=(12, 6))

# Plot normalized prices for each stock
for stock, data in stock_data.items():
    plt.plot(data['normalized_prices'], label=data['name'])

plt.title('Normalized Prices Over 3 Months')
plt.xlabel('Months')
plt.ylabel('Normalized Prices')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Save the plot to a file named normalized_prices.png
plt.savefig('normalized_prices.png')
plt.show()