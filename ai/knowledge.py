ARTICLES = {
    "account_access": "Ask the user to confirm their email, then send the password reset instructions.",
    "general_support": "Acknowledge the request and collect any missing details needed to troubleshoot.",
}


def find_article(category):
    return ARTICLES.get(category, ARTICLES["general_support"])
