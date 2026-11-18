import re

from django.core.exceptions import ValidationError


class LetterAndNumberValidator:
    """BR-02: password must contain at least one letter and one number."""

    def validate(self, password, user=None):
        if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
            raise ValidationError(
                "Password must contain at least one letter and one number.",
                code="password_no_letter_number",
            )

    def get_help_text(self):
        return "Your password must contain at least one letter and one number."
