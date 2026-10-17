from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional


class SusuError(Exception):
    """Base exception class for Susu domain errors."""
    pass


class Member:
    def __init__(self, member_id: str, name: str):
        self.member_id = member_id
        self.name = name

    def __repr__(self) -> str:
        return f"Member(id='{self.member_id}', name='{self.name}')"


class PayoutRecord:
    def __init__(self, week: int, recipient: Member, amount: Decimal):
        self.week = week
        self.recipient = recipient
        self.amount = amount

    def __repr__(self) -> str:
        return f"Payout(Week {self.week}: {self.recipient.name} received GHS {self.amount:.2f})"


class SusuGroup:
    def __init__(self, weekly_contribution: float | str | Decimal):
        contribution = Decimal(str(weekly_contribution))
        if contribution <= Decimal("0.00"):
            raise SusuError("Weekly contribution must be greater than zero.")
        
        self.weekly_contribution: Decimal = contribution.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.members: List[Member] = []
        self._member_lookup: Dict[str, Member] = {}
        
        self.current_week: int = 1
        # week_number -> {member_id -> Decimal}
        self.contributions: Dict[int, Dict[str, Decimal]] = {1: {}}
        self.payout_history: List[PayoutRecord] = []
        self.payout_index: int = 0  # Tracks who receives the next payout

    def add_member(self, member_id: str, name: str) -> Member:
        """Adds a new member to the Susu group."""
        if not member_id or not name:
            raise SusuError("Member ID and name cannot be empty.")
        if member_id in self._member_lookup:
            raise SusuError(f"Member with ID '{member_id}' already exists.")
        if self.current_week > 1 or any(self.contributions[1].values()):
            raise SusuError("Cannot add new members after week 1 has started.")

        member = Member(member_id=member_id, name=name)
        self.members.append(member)
        self._member_lookup[member_id] = member
        return member

    def record_contribution(self, member_id: str, amount: float | str | Decimal) -> Decimal:
        """Records a payment for a member for the current week."""
        if member_id not in self._member_lookup:
            raise SusuError(f"Member '{member_id}' not found in group.")

        payment = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if payment <= Decimal("0.00"):
            raise SusuError("Payment amount must be strictly greater than zero.")

        already_paid = self.contributions[self.current_week].get(member_id, Decimal("0.00"))
        remaining_due = self.weekly_contribution - already_paid

        if payment > remaining_due:
            raise SusuError(
                f"Payment GHS {payment:.2f} exceeds remaining balance of GHS {remaining_due:.2f} for week {self.current_week}."
            )

        new_total = already_paid + payment
        self.contributions[self.current_week][member_id] = new_total
        return new_total

    def get_member_balance_due(self, member_id: str) -> Decimal:
        """Returns remaining balance due for a member in the current week."""
        already_paid = self.contributions[self.current_week].get(member_id, Decimal("0.00"))
        return self.weekly_contribution - already_paid

    def can_close_week(self) -> bool:
        """Checks whether all members have paid their full weekly contribution."""
        if not self.members:
            return False
        return all(self.get_member_balance_due(m.member_id) == Decimal("0.00") for m in self.members)

    def close_week(self) -> Dict:
        """Closes the current week if all payments are complete, otherwise reports arrears."""
        if not self.members:
            raise SusuError("Cannot close week with no members in group.")

        unpaid = {}
        for member in self.members:
            due = self.get_member_balance_due(member.member_id)
            if due > Decimal("0.00"):
                unpaid[member.name] = due

        if unpaid:
            return {
                "success": False,
                "week": self.current_week,
                "message": f"Week {self.current_week} cannot close due to outstanding balances.",
                "unpaid": unpaid,
            }

        # Calculate pot and payout
        pot_amount = self.weekly_contribution * len(self.members)
        recipient = self.members[self.payout_index]
        payout = PayoutRecord(week=self.current_week, recipient=recipient, amount=pot_amount)
        self.payout_history.append(payout)

        payout_info = {
            "success": True,
            "closed_week": self.current_week,
            "recipient": recipient.name,
            "amount": pot_amount,
        }

        # Prepare next week
        self.current_week += 1
        self.payout_index = (self.payout_index + 1) % len(self.members)
        self.contributions[self.current_week] = {}

        return payout_info

    def get_report(self) -> str:
        """Generates a text summary report of current status."""
        lines = [
            f"=== SUSU GROUP REPORT (Week {self.current_week}) ===",
            f"Weekly Contribution: GHS {self.weekly_contribution:.2f}",
            f"Total Members: {len(self.members)}",
            "\n--- Member Status (Current Week) ---",
        ]

        if not self.members:
            lines.append("No members in group.")
        else:
            for member in self.members:
                paid = self.contributions[self.current_week].get(member.member_id, Decimal("0.00"))
                due = self.weekly_contribution - paid
                status = "PAID IN FULL" if due == Decimal("0.00") else f"OWES GHS {due:.2f}"
                lines.append(f"- {member.name} ({member.member_id}): Paid GHS {paid:.2f} | {status}")

        lines.append("\n--- Payout History ---")
        if not self.payout_history:
            lines.append("No payouts completed yet.")
        else:
            for p in self.payout_history:
                lines.append(f"- Week {p.week}: {p.recipient.name} received GHS {p.amount:.2f}")

        return "\n".join(lines)
