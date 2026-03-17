import whois

def is_domain_available(domain: str) -> bool:
    """
    Checks if a domain is available by querying its WHOIS record.
    Returns True if available (no record found), False otherwise.
    """
    try:
        # python-whois returns a dictionary of domain information.
        # If the domain is not registered, it typically returns a dict with None values
        # or raises an exception depending on the TLD server response.
        domain_info = whois.whois(domain)
        
        # If domain_info is empty or domain_name is None, it's likely available.
        if not domain_info or not domain_info.domain_name:
            return True
            
        return False
        
    except Exception as e:
        # Check if the error indicates domain not found, which means it's available
        if type(e).__name__ in ('PywhoisError', 'WhoisDomainNotFoundError', 'WhoisCommandFailed'):
            return True
        # For other unexpected errors, we err on the side of caution (assume unavailable)
        print(f"Error checking domain {domain}: {e}")
        return False

if __name__ == "__main__":
    # Test cases
    print(f"google.com available? {is_domain_available('google.com')}")
    print(f"a-very-random-domain-name-12345.com available? {is_domain_available('a-very-random-domain-name-12345.com')}")
