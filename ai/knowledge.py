"""
ai/knowledge.py

WHAT THIS FILE IS
-----------------
Pipeline STEP 2. Given the ticket's `category` (from the analyzer), this file
picks the matching support article to hand to Gemini.

WHO IMPORTS THIS (and when it runs)
-----------------------------------
- `ai/__init__.py` imports `find_article` and `find_relevant_kb`.
- `main.py` (the browser flow) imports `find_relevant_kb`.
- It is called second inside `solve_ticket`, right after the analyzer.

THE ARTICLES DICTIONARY BELOW
-----------------------------
`ARTICLES` is a small, hardcoded set of support articles.

- The KEYS ("account_access", "general_support", ...) are CATEGORY LABELS,
  not real ticket names. They describe the type of problem.
- The VALUES are the article / solution text for that category.

Because the articles are written directly in this file, the `solve_ticket`
pipeline needs no internet to get them. (A separate live runner can instead
pull knowledge from a Google Sheet; that is a different code path and does not
use this dictionary.)
"""

# A module-level dictionary used as a LOOKUP TABLE: category name -> article text.
# Writing it in CAPITALS is a Python convention meaning "this is a constant
# value that is defined once and should not be changed later in the program".
ARTICLES = {
    # Each value is a long string. Notice two string literals sitting next to
    # each other, like "...page. " "3. Enter..." -- Python automatically joins
    # ("concatenates") adjacent strings into one. It is only there to wrap long
    # text across several lines so the code stays readable.
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
    """
    Return the article text for a category.

    `dict.get(key, default)` returns the value stored under `key`, or the
    `default` if the key is not present. Here the default is the
    "general_support" article, so an unknown category still returns something
    useful instead of crashing or returning None.
    """
    return ARTICLES.get(category, ARTICLES["general_support"])


async def find_relevant_kb(analysis):
    """
    Take the analyzer output and return a list containing one knowledge article.

    Parameters
    ----------
    analysis : dict or object
        The result from `analyze_ticket`, which has a `category` field.

    Returns
    -------
    list
        A list holding a single article string. It is wrapped in a list because
        the resolver expects knowledge as a list (it may hold several articles
        in the future), so we keep the same shape even with one item.
    """
    # As in the analyzer, the analysis may arrive as a dict OR as an object.
    # This is "duck typing": we do not care about the exact type, only that it
    # can give us a "category".
    # The local category examples are not an approved live knowledge source.
    # Return no article so callers skip tickets they cannot ground in the KB.
    return []
