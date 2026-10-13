from __future__ import annotations

import re

from app.domain.job_text import clean_html_text


SUPPORT_KEYS = (
    "relocation", "visa_sponsorship", "work_permit", "relocation_package", "immigration_support",
)

# A support noun is not an offer. Keep employer assertions separate from
# immigration terminology and prerequisites imposed on the applicant.
_VISA = (
    r"visa sponsor(?:ship)?|visa support|sponsor(?:ing)? (?:a |your )?(?:work )?visa|"
    r"визов\w* поддерж\w*|спонсир\w* виз\w*|visum[- ](?:sponsor\w*|unterstütz\w*)"
)
_RELOCATION = (
    r"relocation(?: (?:support|assistance|package))?|релокац\w*(?: пакет\w*)?|"
    r"помощ\w* (?:с |при )?переезд\w*|оплат\w* переезд\w*|"
    r"umzug(?:s)?[- ]?(?:hilfe|unterstütz\w*)"
)
_PERMIT = (
    r"work permit(?: (?:support|assistance|sponsorship))?|"
    r"(?:помощ\w* (?:с |в )?(?:оформлен\w* )?|поддерж\w* (?:в )?(?:оформлен\w* )?)"
    r"разрешени\w* на работу|arbeitserlaubnis[- ](?:hilfe|unterstütz\w*)"
)
_PACKAGE = (
    r"relocation (?:package|assistance)|релокационн\w* пакет\w*|оплат\w* переезд\w*"
)
_IMMIGRATION = (
    r"immigration (?:support|assistance)|visa support|визов\w* поддерж\w*|"
    r"помощ\w* (?:с |в )?(?:оформлен\w* )?(?:виз\w*|иммиграц\w*)"
)
_TERMS = {
    key: re.compile(rf"\b(?:{pattern})\b")
    for key, pattern in (
        ("relocation", _RELOCATION), ("visa_sponsorship", _VISA),
        ("work_permit", _PERMIT), ("relocation_package", _PACKAGE),
        ("immigration_support", _IMMIGRATION),
    )
}
_ASSERTIONS = re.compile(
    r"\b(?:we|(?:the |our )?(?:company|employer)) "
    r"(?:(?:can|will) )?(?:offer\w*|provide\w*|sponsor\w*|support\w*|assist\w*|help|pay for|fund)\b|"
    r"\b(?:предоставляем|предлагаем|оплачиваем|спонсируем|помогаем)\b|"
    r"\bwir (?:bieten|unterstützen|helfen)\b"
)
_DENY_ASSERTIONS = re.compile(
    r"\b(?:do(?:es)? not|did not|will not|cannot|can not|can't|don't|doesn't|won't|"
    r"unable to|not able to|never) (?:currently )?"
    r"(?:offer|provide|sponsor|support|assist|help|pay for|fund)\b|"
    r"\bне (?:предоставляем|предлагаем|оплачиваем|спонсируем|помогаем)\b|"
    r"\bwir (?:bieten|leisten) keine?\b"
)
_DIRECT_DENIAL = re.compile(r"\b(?:no|without|без|нет|никакой|kein\w*|ohne) (?:any )?$")
_STATUS = re.compile(
    r"\b(?:(?:is|are|will be|can be|wird|werden|ist|sind) )?"
    r"(?P<denied>not |never |nicht |не )?"
    r"(?:available|provided|offered|supported|included|covered|paid|funded|"
    r"предоставляется|предоставляем|предлагается|оплачивается|доступна|доступен|"
    r"verfügbar|angeboten|unterstützt)\b"
)
_INCIDENTAL = re.compile(
    r"\b(?:guidance|information|advice|policy|policies|questions?|requirements?|"
    r"информац\w*|консультац\w*|beratung|informationen)\b"
)
_UNCERTAIN = re.compile(r"\b(?:may|might|could|possibly|potentially|potential|возможно|может|могут)\b")
_REQUIRED = re.compile(r"^(?:(?:is|are) )?(?:not )?(?:required|necessary|needed)\b")
_COORDINATED_TERMS = re.compile(
    rf"\b(?:{_VISA}|{_RELOCATION}|{_PERMIT}|{_PACKAGE}|{_IMMIGRATION})\b"
)
_LIST_WORDS = re.compile(r"\b(?:a|an|the|your|any|and|or|also|plus|with|und|oder|и|или|также)\b")
_ROLE_BENEFIT = re.compile(
    r"^(?:remote(?: worldwide| globally)?|(?:worldwide|globally) remote|"
    r"(?:(?:junior|senior|associate|warehouse|production|hotel|kitchen|construction|"
    r"linux|devops|cloud|software|infrastructure|platform|systems?|technical|support) ){0,4}"
    r"(?:engineer|worker|administrator|developer|assistant|technician|staff|specialist|operator))"
    r" (?:role |position |job )?with\s*$"
)
_CONDITIONAL_AFTER = re.compile(
    r"^(?:(?:is|are) )?(?:may|might|could|possibly|potentially|if|subject to|depending on)\b"
)
_DIRECT_VISA_SPONSOR = re.compile(
    r"\b(?:we|(?:the |our )?(?:company|employer)) "
    r"(?P<denial>cannot |can't |do not |don't |will not |won't |are unable to )?"
    r"(?:can |will )?sponsor (?:a |your |an )?(?:work |employment )?visas?"
    r"(?=$|[,.:;]| (?:for|to|and)\b)"
)


def _support_list(text: str) -> bool:
    remainder = _COORDINATED_TERMS.sub("", text)
    remainder = _LIST_WORDS.sub("", remainder)
    return not remainder.strip(" \t,:&/-")


def support_evidence(text: str) -> dict[str, bool | None]:
    """Extract bounded, explicit support statements; absence remains unknown.

    Only public posting prose is accepted here, never serialized raw metadata.
    Recognized refusals outrank offers for the same component. This deliberately
    small English/Russian/German vocabulary is not a legal-eligibility decision.
    """
    clauses = re.split(
        r"[\n.!?;]+|\b(?:but|however|although|но|однако|aber|jedoch)\b",
        clean_html_text(text).casefold().replace("ё", "е").replace("’", "'"),
    )
    values: dict[str, bool | None] = {key: None for key in SUPPORT_KEYS}
    for clause in clauses:
        clause = " ".join(clause.split())
        # In a direct verb phrase, "sponsor visa" overlaps the term itself;
        # the generic before-noun matcher cannot see its predicate/negation.
        # Keep this employer assertion narrow and reject conditional promises.
        if not (_UNCERTAIN.search(clause) or re.search(r"\b(?:if|unless|subject to)\b", clause)):
            for assertion in _DIRECT_VISA_SPONSOR.finditer(clause):
                if assertion.group("denial"):
                    values["visa_sponsorship"] = False
                elif values["visa_sponsorship"] is not False:
                    values["visa_sponsorship"] = True
        for key, pattern in _TERMS.items():
            for noun in pattern.finditer(clause):
                before = clause[max(0, noun.start() - 100):noun.start()]
                after = clause[noun.end():noun.end() + 100]
                assertions = [
                    found for found in _ASSERTIONS.finditer(before)
                    if _support_list(before[found.end():])
                ]
                denials = [
                    found for found in _DENY_ASSERTIONS.finditer(before)
                    if _support_list(before[found.end():])
                ]
                status = _STATUS.search(after)
                if status and not _support_list(after[:status.start()]):
                    status = None
                # A later offer starts a new predicate, e.g. "we do not offer
                # relocation, and we provide visa sponsorship".
                denied_before = bool(denials) and (
                    not assertions or denials[-1].end() >= assertions[-1].end()
                )
                direct_denial = bool(_DIRECT_DENIAL.search(before)) or any(
                    _support_list(before[found.end():])
                    for found in re.finditer(r"\b(?:no|without|без|нет|никакой|kein\w*|ohne)\s+", before)
                )
                status_prefix = after[:status.end()] if status else ""
                denied_after = bool(status and status.group("denied"))
                if (_INCIDENTAL.match(after.strip()) or _REQUIRED.match(after.strip())
                        or _CONDITIONAL_AFTER.match(after.strip())):
                    continue
                if direct_denial or denied_before or (denied_after and not _UNCERTAIN.search(status_prefix)):
                    values[key] = False
                    continue
                if values[key] is False:
                    continue
                if assertions:
                    assertion_tail = before[assertions[-1].start():]
                    offered = not _INCIDENTAL.search(assertion_tail) and not _UNCERTAIN.search(assertion_tail)
                else:
                    offered = False
                # A concrete vacancy descriptor states a benefit affirmatively,
                # e.g. "Warehouse worker with relocation assistance". Match
                # only bounded role/work descriptors, not any mention of "with".
                included_with_role = bool(_ROLE_BENEFIT.fullmatch(before))
                # "Sponsorship guidance available" and conditional availability
                # are not sponsorship offers. Shared list predicates are allowed.
                incidental_after = _INCIDENTAL.search(status_prefix if status else after[:35])
                available = bool(status and not denied_after and not _UNCERTAIN.search(status_prefix))
                if not incidental_after and (offered or available or included_with_role):
                    values[key] = True
    return values


def existing_work_authorization_required(text: str) -> bool:
    """Recognize prerequisites separately from employer permit assistance."""
    normalized = " ".join(clean_html_text(text).casefold().replace("ё", "е").split())
    requirement = re.compile(
        r"\bmust (?:already )?(?:have (?:the )?right to work|be authorized to work|"
        r"have (?:a |an )?(?:valid |existing )?(?:eu |european union )?work permit)|"
        r"\b(?:eu|existing|valid) work (?:permit|authorization) (?:is )?required\b|"
        r"\b(?:должен|должны) (?:уже )?иметь (?:право|разрешение) на работу\b|"
        r"\b(?:gültige|bestehende) arbeitserlaubnis (?:ist )?(?:erforderlich|vorausgesetzt)\b",
    )
    for found in requirement.finditer(normalized):
        before = normalized[max(0, found.start() - 35):found.start()]
        if re.search(r"\b(?:no|without|не|нет|без|kein\w*|ohne)\s*$", before):
            continue
        return True
    return False
