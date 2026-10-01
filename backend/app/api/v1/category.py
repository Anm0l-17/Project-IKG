from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class CategoryItem(BaseModel):
    name: str
    slug: str
    description: str


CATEGORIES: list[CategoryItem] = [
    CategoryItem(
        name="Indian Current Affairs",
        slug="current-affairs",
        description="National news and general Indian affairs",
    ),
    CategoryItem(
        name="Parliament",
        slug="parliament",
        description="Lok Sabha, Rajya Sabha, bills, and legislative updates",
    ),
    CategoryItem(
        name="Economics",
        slug="economics",
        description="RBI policies, inflation, fiscal deficit, and macroeconomics",
    ),
    CategoryItem(
        name="Trade",
        slug="trade",
        description="Import/export policies, FTAs, commerce, and international trade",
    ),
    CategoryItem(
        name="Defence",
        slug="defence",
        description="Indian Armed Forces, strategic security, and defense procurement",
    ),
    CategoryItem(
        name="Geopolitics",
        slug="geopolitics",
        description="Foreign policy, international diplomacy, and multilateral relations",
    ),
]


@router.get("/categories", response_model=list[CategoryItem])
async def get_categories():
    return CATEGORIES
