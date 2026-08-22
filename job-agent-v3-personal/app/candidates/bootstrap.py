from __future__ import annotations

from app.database import repository as repo
from app.knowledge.profile import load_profile


async def bootstrap_user(chat_id: int | str, display_name: str = ""):
    user = await repo.get_user_by_chat(chat_id)
    if not user:
        user = await repo.create_user(chat_id, display_name)
    profile = await repo.ensure_default_profile(user.id)

    config = load_profile()
    geography = config.get("geography") or {}
    if not user.current_country and geography.get("current_country"):
        await repo.set_user_country(user.id, str(geography["current_country"]).upper())
        user = await repo.get_user_by_chat(chat_id)

    existing_facts = await repo.list_facts(profile.id)
    candidate = config.get("candidate") or {}
    if not existing_facts:
        for fact in candidate.get("facts") or []:
            await repo.add_fact(profile.id, str(fact), category="experience")

    searches = await repo.list_search_profiles(profile.id)
    if searches and not searches[0].settings:
        search_cfg = dict(config.get("search") or {})
        search_cfg.update(
            {
                "target_countries": geography.get("target_countries") or [],
                "remote_worldwide": geography.get("remote_worldwide", True),
                "remote_regions": geography.get("remote_regions") or [],
                "relocation_enabled": geography.get("relocation_enabled", True),
                "relocation_countries": geography.get("relocation_countries") or [],
                "minimum_salary": {"RUB": search_cfg.pop("minimum_salary_net_rub", 0)},
                "modes": search_cfg.get("modes") or {"local_ru": True, "remote_international": True, "relocation": True},
            }
        )
        await repo.update_search_settings(searches[0].id, search_cfg)

    resumes = await repo.list_resumes(profile.id)
    if not resumes:
        hh_id = config.get("candidate", {}).get("hh_resume_id") or None
        await repo.add_resume(profile.id, "DevOps RU", "ru", "DevOps Engineer", source="hh" if hh_id else "generated", external_id=hh_id)
        await repo.add_resume(profile.id, "DevOps EN", "en", "DevOps Engineer")
        await repo.add_resume(profile.id, "Linux Admin", "ru", "Linux Administrator")
    return user, profile
