import unittest
from decimal import Decimal
from susu import SusuGroup, SusuError


class TestSusuGroup(unittest.TestCase):

    def setUp(self):
        self.susu = SusuGroup(weekly_contribution="50.00")
        self.m1 = self.susu.add_member("M1", "Ama")
        self.m2 = self.susu.add_member("M2", "Kofi")
        self.m3 = self.susu.add_member("M3", "Esi")

    # TEST 1: Exact Decimal handling
    def test_exact_money_handling(self):
        self.susu.record_contribution("M1", "33.33")
        self.susu.record_contribution("M1", "16.67")
        self.assertEqual(self.susu.get_member_balance_due("M1"), Decimal("0.00"))

    # TEST 2: Partial payment case
    def test_partial_payment(self):
        self.susu.record_contribution("M3", "30.00")
        self.assertEqual(self.susu.get_member_balance_due("M3"), Decimal("20.00"))

    # TEST 3: Week cannot close when member owes money
    def test_cannot_close_week_if_unpaid(self):
        self.susu.record_contribution("M1", "50.00")
        self.susu.record_contribution("M2", "50.00")
        self.susu.record_contribution("M3", "30.00")  # Esi still owes 20

        res = self.susu.close_week()
        self.assertFalse(res["success"])
        self.assertIn("Esi", res["unpaid"])
        self.assertEqual(res["unpaid"]["Esi"], Decimal("20.00"))
        self.assertEqual(self.susu.current_week, 1)  # Week remains 1

    # TEST 4: Reject payment above amount owed
    def test_reject_overpayment(self):
        with self.assertRaises(SusuError):
            self.susu.record_contribution("M1", "60.00")

        self.susu.record_contribution("M1", "40.00")
        with self.assertRaises(SusuError):
            self.susu.record_contribution("M1", "15.00")  # Owes only 10

    # TEST 5: Reject zero or negative payments
    def test_reject_zero_or_negative_payment(self):
        with self.assertRaises(SusuError):
            self.susu.record_contribution("M1", "0.00")
        with self.assertRaises(SusuError):
            self.susu.record_contribution("M1", "-10.00")

    # TEST 6: Reject unknown or duplicate members
    def test_member_validations(self):
        with self.assertRaises(SusuError):
            self.susu.record_contribution("M99", "50.00")  # Unknown member
        with self.assertRaises(SusuError):
            self.susu.add_member("M1", "Ama Duplicate")  # Duplicate ID

    # TEST 7: Full cycle payout and rotation order
    def test_payout_rotation(self):
        # Week 1 Payout
        for m_id in ["M1", "M2", "M3"]:
            self.susu.record_contribution(m_id, "50.00")
        w1_res = self.susu.close_week()
        self.assertTrue(w1_res["success"])
        self.assertEqual(w1_res["recipient"], "Ama")  # 1st joined
        self.assertEqual(w1_res["amount"], Decimal("150.00"))
        self.assertEqual(self.susu.current_week, 2)

        # Week 2 Payout
        for m_id in ["M1", "M2", "M3"]:
            self.susu.record_contribution(m_id, "50.00")
        w2_res = self.susu.close_week()
        self.assertTrue(w2_res["success"])
        self.assertEqual(w2_res["recipient"], "Kofi")  # 2nd joined


if __name__ == "__main__":
    unittest.main()
