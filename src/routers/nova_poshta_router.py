from typing import Optional
from fastapi import APIRouter

from src.service.nova_post import NovaPostAPI
from config import NOVA_POST_API

router = APIRouter()
np_api = NovaPostAPI(NOVA_POST_API)


@router.get("/settlements")
async def search_settlements(search: Optional[str] = None):
    try:
        if not search or len(search) < 2:
            return {
                "success": True,
                "data": []
            }

        result = await np_api.search_settlements(search)

        if result.get("success"):
            data = result.get("data", [])
            if not data:
                return {
                    "success": True,
                    "data": []
                }

            if isinstance(data, list) and len(data) > 0:
                addresses = data[0].get("Addresses", [])
                return {
                    "success": True,
                    "data": [
                        {
                            "ref": addr["DeliveryCity"],
                            "name": addr["Present"],
                            "nameRu": addr["MainDescription"],
                            "area": addr.get("Area", ""),
                            "region": addr.get("Region", "")
                        }
                        for addr in addresses
                    ]
                }

        return {
            "success": False,
            "error": "Failed to fetch settlements",
            "details": result
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/delivery-price")
async def get_delivery_price(
    sender_city_ref: str,
    recipient_city_ref: str,
    weight: float = 1,
    cost: float = 100
):
    try:
        result = await np_api.get_document_price(
            sender_city_ref=sender_city_ref,
            recipient_city_ref=recipient_city_ref,
            weight=weight,
            cost=cost
        )
        if result["success"]:
            return {
                "success": True,
                "data": {
                    "cost": result["data"][0]["Cost"],
                    "estimated_delivery_days": result["data"][0].get("EstimatedDeliveryDate", "")
                }
            }
        return {"success": False, "error": "Failed to calculate delivery price"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/warehouses/{city_ref}")
async def get_city_warehouses(
    city_ref: str,
    search: Optional[str] = None,
    page: Optional[int] = 1
):
    try:
        result = await np_api.get_warehouses(
            city_ref=city_ref,
            page=page,
            find_by_string=search or ""
        )

        if not result["success"]:
            return {
                "success": False,
                "error": f"Nova Poshta API error: {result.get('errors', ['Unknown error'])}",
                "raw_response": result
            }

        if not result.get("data"):
            return {
                "success": True,
                "data": [],
                "message": "No warehouses found for this city"
            }

        warehouses = result["data"]
        # Сортировка отделений по номеру
        warehouses.sort(
            key=lambda x: int(''.join(filter(str.isdigit, x["Number"])) or 0)
        )

        formatted_warehouses = [
            {
                "ref": w["Ref"],
                "number": w["Number"],
                "address": w["Description"],
                "addressRu": w.get("DescriptionRu", w["Description"]),
                "type": w["TypeOfWarehouse"],
                "phone": w.get("Phone", ""),
                "schedule": w.get("Schedule", {})
            }
            for w in warehouses
        ]

        return {
            "success": True,
            "data": formatted_warehouses
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/tracking/{ttn}")
async def track_package(ttn: str):
    try:
        result = await np_api.track_document(ttn)
        if result["success"]:
            return {
                "success": True,
                "data": result["data"][0]
            }
        return {"success": False, "error": "Failed to track package"}
    except Exception as e:
        return {"success": False, "error": str(e)}
