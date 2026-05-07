def run(input_data):

    price = input_data["price"]

    if price > 100:
        return {"signal": "SELL"}

    return {"signal": "BUY"}
