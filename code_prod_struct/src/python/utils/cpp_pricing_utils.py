import numpy as np
import json
import subprocess


def generate_json(spots, past_matrix, rates, dates, today_date, is_today_a_fixing_date, num_days_in_one_year, covar_mat, correl_mat,
                  sample_nb, rel_finite_diff_step):
    data = {
        "Currencies": [
            {"id": "eur", "InterestRate": rates[0], "Volatility": 0},
            {"id": "au_dollar", "InterestRate": rates[1], "Volatility": np.sqrt(covar_mat[4][4]), "Spot": spots[4]},
            {"id": "us_dollar", "InterestRate": rates[2], "Volatility": np.sqrt(covar_mat[5][5]), "Spot": spots[5]},
            {"id": "k_won", "InterestRate": rates[3], "Volatility": np.sqrt(covar_mat[6][6]), "Spot": spots[6]}
        ],
        "DomesticCurrencyId": "eur",
        "Assets": [
            {"CurrencyId": "eur", "Volatility": np.sqrt(covar_mat[0][0]), "Spot": spots[0]},
            {"CurrencyId": "au_dollar", "Volatility": np.sqrt(covar_mat[1][1]), "Spot": spots[1]},
            {"CurrencyId": "us_dollar", "Volatility": np.sqrt(covar_mat[2][2]), "Spot": spots[2]},
            {"CurrencyId": "k_won", "Volatility": np.sqrt(covar_mat[3][3]), "Spot": spots[3]}
        ],
        "Past": past_matrix,
        "Dates": dates,
        "TodayDate": today_date,
        "isTodayAFixingDate": int(is_today_a_fixing_date),
        "NumberOfDaysInOneYear": num_days_in_one_year,
        "Correlation": correl_mat,
        "SampleNb": sample_nb,
        "RelativeFiniteDifferenceStep": rel_finite_diff_step
    }
    
    json_data = json.dumps(data, indent=2)
    return json_data

def send_pricing_request(input_path, output_path):
    # Command to execute
    commands = f"./src/python/pricing {input_path} {output_path}"

    # Run the command using subprocess
    try:
        subprocess.run(commands, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running the command: {e}")
    
    # call C++ code here
    return 0

def get_price_and_deltas(spots, past_matrix, rates, dates, today_date, is_today_a_fixing_date, num_days_in_one_year, covar_mat,
                         correl_mat, sample_nb, rel_finite_diff_step):
    result_json = generate_json(spots, past_matrix, rates, dates, today_date, is_today_a_fixing_date, num_days_in_one_year, covar_mat,
                                correl_mat, sample_nb, rel_finite_diff_step)

    input_path = "src/data/json_params.json"
    output_path = "src/data/results_pricing.json"
    
    with open(input_path, 'w') as json_file:
        json_file.write(result_json)

    # send_pricing_request to c++
    send_pricing_request(input_path, output_path)

    # Open output Json
    with open(output_path, 'r') as file:
        output_json = json.load(file)

    # Extract values
    price = output_json["price"]
    price_std_dev = output_json["priceStdDev"]
    delta = output_json["deltas"]
    delta_std_dev = output_json["deltasStdDev"]

    if is_today_a_fixing_date:
        flux = output_json["flux"]
    else:
        flux = 0
    
    return price, price_std_dev, delta, delta_std_dev, flux