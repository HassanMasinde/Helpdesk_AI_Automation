import logging

def fetch_sheet_data():
    """Fetches knowledge base records."""
    logging.info("Accessing knowledge base data...")
    # Add your Google Sheets API fetching logic here
    return []

def search_knowledge(kb_data, query):
    """Searches knowledge base records for matching resolution steps."""
    matched = []
    query_str = str(query).lower()
    for row in kb_data:
        if isinstance(row, dict):
            if any(query_str in str(val).lower() for val in row.values() if val):
                matched.append(row)
        elif query_str in str(row).lower():
            matched.append(row)
    return matched

def format_knowledge_for_prompt(matched_docs):
    """Formats matching KB items into resolution text."""
    if not matched_docs:
        return "No specific troubleshooting articles found."
    
    resolutions = []
    for doc in matched_docs:
        if isinstance(doc, dict):
            res = doc.get("resolution") or doc.get("answer") or str(doc)
            resolutions.append(res)
        else:
            resolutions.append(str(doc))
            
    return "\n".join(resolutions)