import logging

async def find_relevant_kb(analysis):
    """
    Safely handles the analysis result to find matching KB documentation.
    """
    # Ensure analysis is treated as a clean string representation
    analysis_str = str(analysis)
    
    logging.info(f"Searching knowledge base for analysis: {analysis_str}")
    
    # Return a basic placeholder response for now
    return "Standard troubleshooting step: Please try restarting the device or clearing cache."
