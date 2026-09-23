ARTICLES = {
    "account_access": (
        "Password reset steps: 1. Go to the login page. 2. Click 'Forgot Password'. "
        "3. Enter your username or email. 4. Follow the instructions to reset your password. "
        "If the account stays locked after these steps, contact Hanmak support."
    ),
    "general_support": (
        "Review the problem and follow the standard support process. "
        "If the problem is not clear or cannot be solved with the available information, "
        "contact Hanmak support."
    ),
    "network_issue": (
        "Check that the computer is connected to the internet. Restart the router if needed. "
        "If the connection still does not work, contact Hanmak support."
    ),
    "printer_issue": (
        "Check that the printer is turned on and connected. Make sure the correct printer is selected. "
        "If documents print to the wrong printer, contact Hanmak support to fix the routing."
    ),
    "billing_issue": (
        "Check the receipt and patient account details. If a payment was posted to the wrong account, "
        "contact Hanmak support to reverse it."
    ),
}


def find_article(category):
    return ARTICLES.get(category, ARTICLES["general_support"])


async def find_relevant_kb(analysis):
    if isinstance(analysis, dict):
        category = analysis.get("category", "general_support")
    else:
        category = getattr(analysis, "category", "general_support")

    return [find_article(category)]
