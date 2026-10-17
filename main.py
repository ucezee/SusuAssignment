from susu import SusuGroup, SusuError


def run_demo():
    print("Initializing Susu Group with GHS 50.00 contribution...")
    susu = SusuGroup(weekly_contribution=50.00)

    # 1. Add Members
    ama = susu.add_member("M01", "Ama")
    kofi = susu.add_member("M02", "Kofi")
    esi = susu.add_member("M03", "Esi")

    print("\n--- Initial Report ---")
    print(susu.get_report())

    # 2. Week 1 Partial Payments
    print("\n--- Week 1: Recording Payments ---")
    susu.record_contribution("M01", 50.00)  # Ama pays 50
    susu.record_contribution("M02", 50.00)  # Kofi pays 50
    susu.record_contribution("M03", 30.00)  # Esi pays 30 (Partial)

    # 3. Attempt to Close Week 1 (Should Fail)
    print("\nAttempting to close Week 1...")
    result = susu.close_week()
    if not result["success"]:
        print(f"FAILED: {result['message']}")
        for name, due in result["unpaid"].items():
            print(f" -> {name} owes GHS {due:.2f}")

    # 4. Esi pays remaining 20
    print("\nEsi pays remaining GHS 20.00...")
    susu.record_contribution("M03", 20.00)

    # 5. Close Week 1 (Should Succeed)
    print("Closing Week 1 again...")
    result = susu.close_week()
    if result["success"]:
        print(f"SUCCESS: Week {result['closed_week']} closed. {result['recipient']} received GHS {result['amount']:.2f}")

    # 6. Show Report at Week 2
    print("\n" + susu.get_report())


if __name__ == "__main__":
    run_demo()
