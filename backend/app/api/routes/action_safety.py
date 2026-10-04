from fastapi import APIRouter

from app.schemas.evidence import ActionSafetyRequest, ActionSafetyResponse

router = APIRouter(prefix="/action-safety", tags=["action-safety"])


@router.post("/check", response_model=ActionSafetyResponse)
async def action_safety(body: ActionSafetyRequest):
    plan = body.planned_action.strip()
    lower = plan.lower()
    if any(w in lower for w in ("transfer", "pay", "upi", "otp", "send money")):
        return ActionSafetyResponse(
            appears_to_plan="You appear to be considering sending money or sharing a payment secret.",
            risk_why="Urgent payment requests are a common scam and bribe pattern. Money sent this way is often hard to reverse.",
            safer_step="Pause before transferring. Verify the request through an official channel rather than relying only on the message.",
        )
    if any(w in lower for w in ("sign", "thumb", "blank")):
        return ActionSafetyResponse(
            appears_to_plan="You appear to be considering signing or providing a fingerprint on a document.",
            risk_why="Signing something you have not read can create obligations you did not intend.",
            safer_step="Photograph the document, take time to read it, and ask a trusted person or legal-aid desk before signing.",
        )
    if any(w in lower for w in ("delete", "wipe")):
        return ActionSafetyResponse(
            appears_to_plan="You appear to be considering deleting messages or files.",
            risk_why="Deleted items are hard to recover and may be the only record of what was said.",
            safer_step="Keep originals. You can hide them in the vault instead of deleting them.",
        )
    if any(w in lower for w in ("confront", "fight", "argue", "record secretly")):
        return ActionSafetyResponse(
            appears_to_plan="You appear to be considering confrontation or covert recording.",
            risk_why="Escalation can increase personal risk. Recording rules vary and can create separate legal issues.",
            safer_step="Move to safety, write a note of what happened, and use a legitimate channel rather than a roadside argument.",
        )
    return ActionSafetyResponse(
        appears_to_plan=plan or "You asked whether an action is safe.",
        risk_why="Any irreversible step (payment, signature, deletion, confrontation) deserves a pause.",
        safer_step="Verify through an official app, website, or known number. If unsure, contact legal aid or a qualified professional.",
    )
