from typing import List

from app.rag.chunker import LegalChunk

# DEMO LEGAL KNOWLEDGE DATA — not verified statutory text. Replace via knowledge_base ingest.
DEMO_CHUNKS: List[LegalChunk] = [
    LegalChunk(
        id="demo-traffic-1",
        document_id="demo-traffic",
        title="Traffic stop — citizen basics (DEMO)",
        section="demo",
        content=(
            "DEMO DATA: During a traffic stop, staying calm, asking the reason, and requesting a documented "
            "penalty or e-challan path is generally safer than an informal cash settlement without a receipt. "
            "This is educational demo text, not the Motor Vehicles Act."
        ),
        source_name="NyaySetu demo knowledge",
        source_url=None,
        source_type="demo",
        verified_at=None,
        is_demo=True,
    ),
    LegalChunk(
        id="demo-bribe-1",
        document_id="demo-bribe",
        title="Improper payment demands (DEMO)",
        section="demo",
        content=(
            "DEMO DATA: A request for money to close a matter without an official receipt or documented process "
            "is a warning sign. Citizens may refuse and ask for the official procedure. This does not accuse any "
            "person of a crime. For complaints, use verified anti-corruption or vigilance channels — not random numbers."
        ),
        source_name="NyaySetu demo knowledge",
        source_url=None,
        source_type="demo",
        verified_at=None,
        is_demo=True,
    ),
    LegalChunk(
        id="demo-scam-1",
        document_id="demo-scam",
        title="UPI and phishing patterns (DEMO)",
        section="demo",
        content=(
            "DEMO DATA: Common scam patterns include urgent KYC, lottery winnings, job offers, impersonation of "
            "banks or officials, requests for OTP, remote-access apps, and UPI collect requests. Do not transfer "
            "money based only on a message. Verify inside the official bank app or a number you already trust. "
            "National cybercrime reporting is commonly done via official government portals."
        ),
        source_name="NyaySetu demo knowledge",
        source_url="https://www.cybercrime.gov.in/",
        source_type="demo",
        verified_at=None,
        is_demo=True,
    ),
    LegalChunk(
        id="demo-threat-1",
        document_id="demo-threat",
        title="Threats and harassment (DEMO)",
        section="demo",
        content=(
            "DEMO DATA: Save messages. Inform a trusted contact. If you are in immediate danger, contact local "
            "emergency services. Do not meet the person alone. This app does not dispatch police."
        ),
        source_name="NyaySetu demo knowledge",
        source_url=None,
        source_type="demo",
        verified_at=None,
        is_demo=True,
    ),
    LegalChunk(
        id="demo-notice-1",
        document_id="demo-notice",
        title="Legal notices (DEMO)",
        section="demo",
        content=(
            "DEMO DATA: Photograph every page. Note dates. Genuine notices usually identify a sender. Lookalike "
            "PDFs on WhatsApp asking for immediate payment can be scams. Do not sign what you do not understand. "
            "Seek a qualified professional or legal-aid service for interpretation."
        ),
        source_name="NyaySetu demo knowledge",
        source_url=None,
        source_type="demo",
        verified_at=None,
        is_demo=True,
    ),
    LegalChunk(
        id="demo-consumer-1",
        document_id="demo-consumer",
        title="Consumer issues (DEMO)",
        section="demo",
        content=(
            "DEMO DATA: Keep bills, chats with the seller, and warranty papers. Consumer dispute processes exist "
            "under Indian consumer protection framework; replace this card with verified Consumer Protection Act "
            "extracts before production."
        ),
        source_name="NyaySetu demo knowledge",
        source_url="https://ncdrc.nic.in/",
        source_type="demo",
        verified_at=None,
        is_demo=True,
    ),
    LegalChunk(
        id="demo-labour-1",
        document_id="demo-labour",
        title="Wage and labour (DEMO)",
        section="demo",
        content=(
            "DEMO DATA: Keep appointment letters, wage slips, and attendance records. For unpaid wages, official "
            "labour departments and legal-aid desks are typical starting points. Replace with verified Ministry of Labour material."
        ),
        source_name="NyaySetu demo knowledge",
        source_url="https://labour.gov.in/",
        source_type="demo",
        verified_at=None,
        is_demo=True,
    ),
    LegalChunk(
        id="demo-tenant-1",
        document_id="demo-tenant",
        title="Tenancy notes (DEMO)",
        section="demo",
        content=(
            "DEMO DATA: Keep the rent agreement, payment proofs, and notices. State rent and tenancy rules vary. "
            "Do not treat this demo card as your state's statute."
        ),
        source_name="NyaySetu demo knowledge",
        source_url=None,
        source_type="demo",
        verified_at=None,
        is_demo=True,
    ),
    LegalChunk(
        id="demo-safety-1",
        document_id="demo-safety",
        title="Evidence integrity (DEMO)",
        section="demo",
        content=(
            "DEMO DATA: Store originals. Note date and place. A SHA-256 hash can help detect later file changes. "
            "Hashing is an integrity mechanism and does not by itself make evidence legally admissible."
        ),
        source_name="NyaySetu demo knowledge",
        source_url=None,
        source_type="demo",
        verified_at=None,
        is_demo=True,
    ),
]
