# SusuAssignment
# Rotating Savings Group (Susu) Manager

A lightweight Python module to manage rotating savings and credit associations (Susu/ROSCA).

## Features
- **Precise Financial Math**: Uses Python's standard `decimal.Decimal` module to avoid float rounding inaccuracies.
- **Order-Based Rotation**: Pays out pot strictly according to member join order.
- **Partial Payment Support**: Allows members to make fractional contributions throughout the week.
- **Validation**: Enforces rules against overpayment, zero/negative payments, invalid IDs, and premature week closure.

## Prerequisites
- Python 3.8 or higher. No external third-party dependencies are required.

## How to Run the Demo Program
To execute the demonstration script simulating the example scenario:

```bash
python main.py
