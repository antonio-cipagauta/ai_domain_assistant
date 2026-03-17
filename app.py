import streamlit as st

from ai_suggestions import get_alternative_domains
from domain_checker import is_domain_available
from rag_engine import RAGEngine

st.set_page_config(page_title="Domain Scout AI", page_icon="🌐")


# Initialize RAG Engine
@st.cache_resource
def load_rag():
    return RAGEngine()


rag_engine = load_rag()

st.title("🌐 Domain Scout AI")
st.write(
    "Check if your dream domain is available, "
    "or get AI-powered alternatives if it's taken!"
)

with st.form("domain_check_form"):
    domain_input = st.text_input(
        "Enter a domain name (e.g., myawesomeidea.com)", placeholder="myawesomeidea.com"
    )
    submit_button = st.form_submit_button("Check Availability", type="primary")

if submit_button:
    if domain_input:
        domain = domain_input.strip().lower()
        with st.spinner(f"Checking availability for {domain}..."):
            available = is_domain_available(domain)

        if available:
            st.success(f"🎉 Great news! **{domain}** appears to be available!")
            st.write("### Where to buy:")

            # Direct links to registrars
            col1, col2, col3 = st.columns(3)
            with col1:
                st.link_button(
                    "Namecheap",
                    f"https://www.namecheap.com/domains/registration/results/?domain={domain}",
                    use_container_width=True,
                )
            with col2:
                st.link_button(
                    "GoDaddy",
                    f"https://www.godaddy.com/domainsearch/find?checkAvail=1&tmskey=&domainToCheck={domain}",
                    use_container_width=True,
                )
            with col3:
                st.link_button(
                    "Squarespace",
                    "https://domains.squarespace.com/domain-search",
                    use_container_width=True,
                )

        else:
            st.error(f"❌ Sorry, **{domain}** is already taken.")

            # RAG Section: Get Expert advice
            with st.spinner("Retrieving expert branding advice..."):
                rag_context = rag_engine.get_relevant_context(domain)

            if rag_context:
                with st.expander("💡 Expert Insight for this search"):
                    st.markdown(rag_context)

            st.write("### Try these AI-generated alternatives instead:")
            with st.spinner("Generating creative alternatives with Gemini..."):
                alternatives = get_alternative_domains(domain, context=rag_context)

            if isinstance(alternatives, list):
                st.write("Checking availability of suggestions...")

                all_suggestions = {}  # domain: is_available
                available_count = 0
                max_retries = 3
                retry_count = 0

                # Initial processing
                for alt in alternatives:
                    if alt not in all_suggestions:
                        is_avail = is_domain_available(alt)
                        all_suggestions[alt] = is_avail
                        if is_avail:
                            available_count += 1

                # Retry loop if not enough available domains found
                while available_count < 4 and retry_count < max_retries:
                    retry_count += 1
                    st.write(f"Refining suggestions (Attempt {retry_count + 1})...")
                    # Pass already found domains to avoid repetition
                    new_alternatives = get_alternative_domains(
                        domain, excluded_domains=list(all_suggestions.keys())
                    )
                    if isinstance(new_alternatives, list):
                        for alt in new_alternatives:
                            if alt not in all_suggestions:
                                is_avail = is_domain_available(alt)
                                all_suggestions[alt] = is_avail
                                if is_avail:
                                    available_count += 1
                                    if available_count >= 4:
                                        break
                    if available_count >= 4:
                        break

                st.success(f"Found {min(available_count, 4)} available alternatives!")

                # Separate available and taken suggestions for sorted display
                available_list = [d for d, avail in all_suggestions.items() if avail]
                taken_list = [d for d, avail in all_suggestions.items() if not avail]

                # Display available results (limited to 4)
                displayed_available = 0
                for alt_domain in available_list:
                    if displayed_available < 4:
                        st.markdown(f"✅ **{alt_domain}** (Available)")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.link_button(
                                "Namecheap",
                                f"https://www.namecheap.com/domains/registration/results/?domain={alt_domain}",
                                use_container_width=True,
                            )
                        with col2:
                            st.link_button(
                                "GoDaddy",
                                f"https://www.godaddy.com/domainsearch/find?checkAvail=1&tmskey=&domainToCheck={alt_domain}",
                                use_container_width=True,
                            )
                        with col3:
                            st.link_button(
                                "Squarespace",
                                "https://domains.squarespace.com/domain-search",
                                use_container_width=True,
                            )
                        st.divider()
                        displayed_available += 1

                # Display taken results (no limit)
                for alt_domain in taken_list:
                    st.markdown(f"❌ ~~{alt_domain}~~ (Taken)")
            else:
                st.error(alternatives)

    else:
        st.warning("Please enter a domain name.")
