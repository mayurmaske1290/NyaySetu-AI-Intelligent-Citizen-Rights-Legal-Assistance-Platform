from __future__ import annotations

from typing import List, Optional

from app.ai.provider import LLMProvider
from app.schemas.analysis import (
    ActionStep,
    AnalysisResponse,
    Category,
    ConfidenceLabel,
    EvidenceGap,
    EvidenceHint,
    RightItem,
    Severity,
    SourceRef,
    WarningItem,
)
from app.services.confidence import label_from_score
from app.services.severity import fuse_severity

DEMO_SOURCE = SourceRef(
    title="NyaySetu demo knowledge (not a verified government source)",
    url=None,
    source_type="demo",
    verified=False,
    demo=True,
)

DISCLAIMER = (
    "This is informational assistance, not legal advice. "
    "NyaySetu AI is not a replacement for a lawyer. "
    "Demo knowledge is labeled DEMO DATA and must not be treated as official law."
)


def _detect_categories(text: str, hint: Optional[str]) -> List[str]:
    t = text.lower()
    found: List[str] = []

    def add(cat: str) -> None:
        if cat not in found:
            found.append(cat)

    if hint and hint in Category.ALL:
        add(hint)

    traffic = any(
        k in t
        for k in (
            "traffic",
            "challan",
            "pulled over",
            "stopped me",
            "check post",
            "rto",
            "driving licence",
            "driving license",
            "helmet",
            "signal",
            "police stopped",
        )
    )
    bribe = any(
        k in t
        for k in (
            "bribe",
            "₹",
            "rs ",
            "rs.",
            "cash",
            "settle",
            "without receipt",
            "instead of receipt",
            "asked for money",
            "pay unofficial",
            "hafta",
        )
    ) or ("500" in t and ("asked" in t or "demand" in t or "instead" in t))
    scam = any(
        k in t
        for k in (
            "upi",
            "scam",
            "phishing",
            "otp",
            "kyc",
            "lottery",
            "whatsapp",
            "suspicious link",
            "pay now",
            "account will be blocked",
            "click the link",
            "imps",
            "collect request",
        )
    )
    threat = any(
        k in t
        for k in (
            "threat",
            "kill",
            "hurt you",
            "harass",
            " intimid",
            "abusive",
            "blackmail",
            "don't tell anyone",
            "or else",
        )
    )
    notice = any(
        k in t
        for k in (
            "legal notice",
            "summon",
            "summons",
            "court notice",
            "advocate notice",
            "show cause",
            "vakalat",
        )
    )

    if traffic:
        add(Category.TRAFFIC_STOP)
    if bribe:
        add(Category.BRIBE_DEMAND)
    if scam:
        add(Category.SCAM)
    if threat:
        add(Category.THREAT_HARASSMENT)
    if notice:
        add(Category.LEGAL_NOTICE)
    if not found:
        add(Category.OTHER)
    return found


class DemoAIProvider(LLMProvider):
    """Deterministic structured analyzer for demos and offline fallback. Clearly demo."""

    name = "demo"

    async def analyze_situation(
        self,
        text: str,
        language: str = "en",
        category_hint: Optional[str] = None,
        retrieved_context: str = "",
    ) -> AnalysisResponse:
        cats = _detect_categories(text, category_hint)
        primary = cats[0]
        secondary = cats[1:]
        severity = fuse_severity(cats, text)
        score = 0.78 if len(text) > 40 else 0.62
        if primary == Category.OTHER and not secondary:
            score = 0.48
        label = label_from_score(score, has_retrieved=bool(retrieved_context))

        rights, warnings, steps, preserve, gaps = _pack_for(cats, text)
        human = severity == Severity.HIGH
        summary = _summary(cats, text, language)

        uncertain_note = ""
        if label == ConfidenceLabel.UNCERTAIN:
            uncertain_note = (
                "I'm not fully certain about this situation. Please verify with an appropriate "
                "legal professional or legitimate authority before taking action."
            )

        return AnalysisResponse(
            primary_category=primary,
            secondary_categories=secondary,
            severity=severity,
            confidence=score,
            confidence_label=label,
            summary=summary,
            rights=rights,
            what_not_to_do=warnings,
            action_steps=steps,
            evidence_to_preserve=preserve,
            evidence_gaps=gaps,
            sources=[DEMO_SOURCE],
            requires_human_help=human,
            safety_notes=uncertain_note
            or "Prioritize personal safety. Do not escalate a dangerous confrontation.",
            disclaimer=DISCLAIMER,
            demo_mode=True,
            language=language,
        )


def _summary(cats: List[str], text: str, language: str) -> str:
    labels = {
        Category.TRAFFIC_STOP: "a traffic-stop type interaction",
        Category.BRIBE_DEMAND: "a possible improper payment demand",
        Category.SCAM: "a possible scam or phishing attempt",
        Category.THREAT_HARASSMENT: "a threat or harassment situation",
        Category.LEGAL_NOTICE: "a legal-notice type document or message",
        Category.OTHER: "a situation that needs careful next steps",
    }
    joined = " and ".join(labels.get(c, c) for c in cats)
    prefix = {
        "hi": "हमने आपकी बात को इस रूप में समझा: ",
        "mr": "आम्ही तुमची स्थिती अशी समजली: ",
        "en": "Here is what we understood: you appear to be describing ",
    }.get(language, "Here is what we understood: you appear to be describing ")
    clip = text.strip().replace("\n", " ")
    if len(clip) > 180:
        clip = clip[:177] + "..."
    return f"{prefix}{joined}. Your words: “{clip}”"


def _pack_for(cats: List[str], text: str):
    rights: List[RightItem] = []
    warnings: List[WarningItem] = []
    steps: List[ActionStep] = []
    preserve: List[EvidenceHint] = []
    gaps: List[EvidenceGap] = []

    def r(title, explanation, why):
        rights.append(
            RightItem(
                title=title,
                explanation=explanation,
                why=why,
                source_title="DEMO DATA — replace with verified sources",
                source_url=None,
            )
        )

    if Category.TRAFFIC_STOP in cats:
        r(
            "Ask what the stop is about, calmly",
            "You can ask the reason for the stop and what document is being requested. Stay polite. You do not need to argue on the roadside.",
            "Demo card: traffic interaction basics. Not a substitute for the Motor Vehicles Act text.",
        )
        r(
            "Official receipts matter",
            "If a penalty is issued, a proper official receipt or e-challan record is the usual documented path — not an informal cash settlement.",
            "Demo card: documented penalties vs informal payments.",
        )
        warnings.append(
            WarningItem(
                warning="Do not hand over cash without an official receipt, and do not argue aggressively.",
                reason="Informal payments are hard to document. Confrontation can raise safety risk.",
            )
        )
        preserve.append(EvidenceHint(item="Location, time, and vehicle/officer identifiers if safely visible", reason="Helps reconstruct what happened later."))
        gaps.append(EvidenceGap(item="Photo of any written challan or device screen", why_useful="May support what was shown to you.", status="potentially_useful"))

    if Category.BRIBE_DEMAND in cats:
        r(
            "Improper demands are not 'fees'",
            "A request for money to 'settle' without an official process is a warning sign. You can refuse and ask for a documented procedure.",
            "Demo card: anti-corruption citizen guidance. Not a criminal accusation.",
        )
        warnings.append(
            WarningItem(
                warning="Do not pay an undocumented 'settlement' just to leave quickly if you can safely refuse.",
                reason="Cash without a receipt is difficult to explain later. Safety still comes first.",
            )
        )
        warnings.append(
            WarningItem(
                warning="Do not secretly record if you are not sure it is lawful in your situation.",
                reason="Recording rules vary. Prefer notes, receipts, and official channels.",
            )
        )
        preserve.append(EvidenceHint(item="What was said, amount mentioned, and whether a receipt was refused", reason="Your contemporaneous note can support the description."))
        gaps.append(EvidenceGap(item="Any official complaint portal screenshot after you report via a legitimate channel", why_useful="Shows you used an official path.", status="potentially_useful"))
        steps.append(ActionStep(order=0, text="If you feel unsafe, leave the argument and move to a public, well-lit place.", kind="immediate"))

    if Category.SCAM in cats:
        r(
            "Banks and agencies do not usually ask for OTP or secret PINs",
            "Requests to share OTP, remote-access apps, or urgent UPI transfers are common scam patterns. Pause and verify via an official app or number you already trust.",
            "Demo card: cyber/financial fraud hygiene. Not a specific RBI circular citation.",
        )
        warnings.append(
            WarningItem(
                warning="Do not transfer money, share OTP, or install a remote-access app because of urgency or fear.",
                reason="Urgency plus secrecy is a typical scam pattern.",
            )
        )
        warnings.append(
            WarningItem(
                warning="Do not delete the message thread or call logs.",
                reason="Those items may help you explain the sequence later.",
            )
        )
        preserve.append(EvidenceHint(item="Screenshot of the message, number/UPI ID, and time", reason="Supports the described communication."))
        gaps.append(EvidenceGap(item="Bank/UPI transaction record if any payment happened", why_useful="May show amount and counterparty identifiers.", status="potentially_useful"))

    if Category.THREAT_HARASSMENT in cats:
        r(
            "Threats and harassment can be documented",
            "Save messages. Tell a trusted person. If you feel in immediate danger, contact local emergency services. This app cannot dispatch police.",
            "Demo card: safety-first threat response.",
        )
        warnings.append(
            WarningItem(
                warning="Do not meet the person alone or retaliate with threats of your own.",
                reason="Safety and avoiding escalation come first.",
            )
        )
        preserve.append(EvidenceHint(item="Full message screenshots with timestamps visible", reason="Supports the described communication."))
        gaps.append(EvidenceGap(item="List of prior similar messages", why_useful="May show a pattern, if one exists.", status="potentially_useful"))

    if Category.LEGAL_NOTICE in cats:
        r(
            "Do not ignore a real legal document — and do not panic over a lookalike",
            "Read calmly. Note dates. A genuine notice usually identifies a sender and a response path. Lookalike PDFs and WhatsApp 'court notices' are sometimes scams.",
            "Demo card: notice hygiene. Not an interpretation of your specific document.",
        )
        warnings.append(
            WarningItem(
                warning="Do not sign anything you do not understand, and do not pay a 'fee' sent only by message.",
                reason="Pressure to pay or sign immediately is a warning sign.",
            )
        )
        preserve.append(EvidenceHint(item="Photo/PDF of every page plus the envelope or message header", reason="Helps a professional see what you received."))
        gaps.append(EvidenceGap(item="Identity of sender (letterhead, enrollment/registration details if present)", why_useful="Helps check whether the sender looks legitimate.", status="potentially_useful"))

    if Category.OTHER in cats and len(cats) == 1:
        r(
            "You can still preserve facts and ask for legitimate help",
            "Write what happened in order. Keep documents. Use official helplines or legal aid rather than random social-media advice.",
            "Demo card: general citizen next-steps.",
        )
        warnings.append(
            WarningItem(
                warning="Do not share sensitive IDs or OTPs with strangers who offer to 'fix' the case.",
                reason="Opportunistic scams often follow stressful events.",
            )
        )

    warnings.append(
        WarningItem(
            warning="Do not delete relevant photos, chats, or documents.",
            reason="Once deleted, they are hard to recover.",
        )
    )

    # numbered unique steps
    base_steps = [
        ActionStep(order=1, text="Move to safety if anyone is threatening you. Your wellbeing comes first.", kind="immediate"),
        ActionStep(order=2, text="Write a short note of time, place, and what was said. Save screenshots or photos if it is safe.", kind="evidence"),
        ActionStep(order=3, text="Verify any payment, penalty, or legal claim through an official website, app, or known phone number — not only the message you received.", kind="verification"),
        ActionStep(order=4, text="If appropriate, use a legitimate complaint channel (see Find Legitimate Help). Nearest building is not always the right channel.", kind="escalation"),
        ActionStep(order=5, text="If the matter is serious or unclear, speak with a qualified legal professional or legal-aid service.", kind="professional"),
    ]
    # prepend any category-specific immediate steps
    extra = [s for s in steps if s.order == 0]
    out_steps = []
    n = 1
    for s in extra + base_steps:
        out_steps.append(ActionStep(order=n, text=s.text, kind=s.kind))
        n += 1

    return rights, warnings, out_steps, preserve, gaps
