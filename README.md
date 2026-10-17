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

---

### 5. `NOTES.md`


# Design Notes & Assumptions

## Business Assumptions & Rules Enforced
1. **Adding Members Late**: Members cannot be added once Week 1 contributions have commenced or after Week 1 has closed. This keeps the pot size and payout cycle fixed per cycle.
2. **Fixed Contribution**: The weekly contribution amount is fixed for all members across all weeks once initialized.
3. **Exact Currency Representation**: All currency calculations use `Decimal` rounded to 2 decimal places (`0.01`). Floats are converted via string representation to prevent binary floating-point representation drift.
4. **Overpayment Rule**: A member cannot pay more than their remaining balance for the active week.
5. **Rotation Cycle**: Payout follows insertion order (`self.members`). After reaching the last member, the payout order wraps back around to the first member using modular arithmetic (`index % count`).

## Architectural Decisions
- **Domain Exceptions**: Created a dedicated `SusuError` domain exception class to handle business rule violations explicitly instead of generic system exceptions.
- **Decoupled CLI/UI**: Pure Python domain model (`SusuGroup`) separated entirely from UI/CLI logic, making it easy to embed into REST APIs (e.g., FastAPI, Flask) or CLI tools later.

## Future Improvements (With More Time)
1. **Multi-Cycle Management**: Support starting a new cycle with updated contribution rates or member lists once a full cycle completes.
2. **Persistence**: Add SQLite or PostgreSQL persistence via an ORM (e.g., SQLAlchemy) to store historical records across app restarts.
3. **Date & Timestamp Tracking**: Track real calendar timestamps for payments and week closures rather than abstract integer week counters.
4. **Interest / Penalties**: Implement penalty fees for members who cause delays in closing a week due to arrears.
