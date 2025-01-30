import aiohttp
from typing import Dict, Any, Optional, Tuple


class NovaPostAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = 'https://api.novaposhta.ua/v2.0/json/'

    async def _send_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Отправка запроса к API Новой Почты"""
        print(f"Sending request to Nova Post API: {params}")  # Отладка
        async with aiohttp.ClientSession() as session:
            async with session.post(self.api_url, json=params) as response:
                result = await response.json()
                print(f"Nova Post API Response: {result}")  # Отладка
                return result

    async def search_settlements(self, search_text: str) -> Dict[str, Any]:
        """Поиск населенных пунктов по названию"""
        params = {
            "apiKey": self.api_key,
            "modelName": "Address",
            "calledMethod": "searchSettlements",
            "methodProperties": {
                "CityName": search_text,
                "Limit": 20,
                "Page": "1"
            }
        }

        try:
            result = await self._send_request(params)
            return result
        except Exception as e:
            print(f"Error in search_settlements: {e}")
            raise

    async def get_settlements(self) -> Dict[str, Any]:
        """Получение списка населенных пунктов с возможностью получения отделений"""
        params = {
            "apiKey": self.api_key,
            "modelName": "AddressGeneral",
            "calledMethod": "getSettlements",
            "methodProperties": {
                "Warehouse": "1"  # Только населенные пункты с отделениями
            }
        }
        return await self._send_request(params)

    async def get_warehouses(
            self,
            city_ref: str,
            page: int = 1,
            limit: int = 50,
            find_by_string: str = ""
    ) -> Dict[str, Any]:
        """Получение списка отделений в городе"""
        params = {
            "apiKey": self.api_key,
            "modelName": "AddressGeneral",
            "calledMethod": "getWarehouses",
            "methodProperties": {
                "CityRef": city_ref,
                "Page": str(page),
                "Limit": str(limit),
                "Language": "UA",
                "TypeOfWarehouseRef": "841339c7-591a-42e2-8233-7a0a00f0ed6f",  # Все типы отделений
                "FindByString": find_by_string
            }
        }

        result = await self._send_request(params)

        return result

    async def create_recipient(
            self,
            first_name: str,
            last_name: str,
            middle_name: str,
            phone: str
    ) -> Dict[str, Any]:
        """Create a new recipient counterparty"""
        params = {
            "apiKey": self.api_key,
            "modelName": "Counterparty",
            "calledMethod": "save",
            "methodProperties": {
                "FirstName": first_name,
                "LastName": last_name,
                "MiddleName": middle_name,
                "Phone": phone.replace("+", ""),
                "Email": "",
                "CounterpartyType": "PrivatePerson",
                "CounterpartyProperty": "Recipient"
            }
        }
        return await self._send_request(params)

    async def create_recipient_contact(
            self,
            counterparty_ref: str,
            first_name: str,
            last_name: str,
            middle_name: str,
            phone: str
    ) -> Dict[str, Any]:
        """Create a contact person for the recipient"""
        params = {
            "apiKey": self.api_key,
            "modelName": "ContactPerson",
            "calledMethod": "save",
            "methodProperties": {
                "CounterpartyRef": counterparty_ref,
                "FirstName": first_name,
                "LastName": last_name,
                "MiddleName": middle_name,
                "Phone": phone.replace("+", "")
            }
        }
        return await self._send_request(params)

    async def create_express_waybill(
            self,
            sender_ref: str,
            sender_city_ref: str,
            sender_contact_ref: str,
            sender_warehouse_ref: str,
            sender_phone: str,
            recipient_ref: str,
            recipient_contact_ref: str,
            recipient_phone: str,
            recipient_city_ref: str,
            recipient_warehouse_ref: str,
            items_weight: float = 0.5,
            items_cost: float = 200,
            description: str = "Посилка",
            payer_type: str = "Sender",
            payment_method: str = "Cash",
            cargo_type: str = "Parcel",  # Changed from Cargo to Parcel
            service_type: str = "WarehouseWarehouse"
    ) -> Dict[str, Any]:
        """Create an express waybill"""
        params = {
            "apiKey": self.api_key,
            "modelName": "InternetDocument",
            "calledMethod": "save",
            "methodProperties": {
                # Sender information
                "Sender": sender_ref,
                "CitySender": sender_city_ref,
                "SenderAddress": sender_warehouse_ref,  # Using warehouse ref directly
                "ContactSender": sender_contact_ref,
                "SendersPhone": sender_phone,

                # Recipient information
                "Recipient": recipient_ref,
                "ContactRecipient": recipient_contact_ref,
                "RecipientsPhone": recipient_phone.replace("+", ""),
                "CityRecipient": recipient_city_ref,
                "RecipientAddress": recipient_warehouse_ref,

                # Delivery parameters
                "PayerType": payer_type,
                "PaymentMethod": payment_method,
                "CargoType": cargo_type,
                "ServiceType": service_type,
                "Weight": str(items_weight),
                "Cost": str(items_cost),
                "SeatsAmount": "1",
                "Description": description
            }
        }

        result = await self._send_request(params)
        return result

    async def get_counterparties(self, counterparty_type: str = "Sender") -> Dict[str, Any]:
        """Получение справочника контрагентов"""
        params = {
            "apiKey": self.api_key,
            "modelName": "Counterparty",
            "calledMethod": "getCounterparties",
            "methodProperties": {
                "CounterpartyProperty": counterparty_type
            }
        }
        return await self._send_request(params)

    async def get_counterparty_addresses(
        self,
        counterparty_ref: str,
        address_type: str = "Sender"
    ) -> Dict[str, Any]:
        """Получение адресов контрагента"""
        params = {
            "apiKey": self.api_key,
            "modelName": "Counterparty",
            "calledMethod": "getCounterpartyAddresses",
            "methodProperties": {
                "Ref": counterparty_ref,
                "CounterpartyProperty": address_type
            }
        }
        try:
            return await self._send_request(params)
        except Exception as e:
            print(f"Error getting addresses: {str(e)}")
            raise

    async def get_counterparty_contact_persons(self, counterparty_ref: str) -> Dict[str, Any]:
        """Получение списка контактных лиц контрагента"""
        params = {
            "apiKey": self.api_key,
            "modelName": "Counterparty",
            "calledMethod": "getCounterpartyContactPersons",
            "methodProperties": {
                "Ref": counterparty_ref
            }
        }
        return await self._send_request(params)

    async def get_document_price(
        self,
        sender_city_ref: str,
        recipient_city_ref: str,
        service_type: str = "WarehouseWarehouse",
        cargo_type: str = "Cargo",
        weight: float = 1,
        cost: float = 100
    ) -> Dict[str, Any]:
        """Расчет стоимости доставки"""
        params = {
            "apiKey": self.api_key,
            "modelName": "InternetDocument",
            "calledMethod": "getDocumentPrice",
            "methodProperties": {
                "CitySender": sender_city_ref,
                "CityRecipient": recipient_city_ref,
                "ServiceType": service_type,
                "CargoType": cargo_type,
                "Weight": str(weight),
                "Cost": str(cost),
                "SeatsAmount": "1"
            }
        }
        return await self._send_request(params)

    async def save_sender_address(
            self,
            first_name: str,
            last_name: str,
            middle_name: str,
            phone: str,
            city_ref: str
    ) -> Dict[str, Any]:
        """Save address for sender"""
        params = {
            "apiKey": self.api_key,
            "modelName": "Counterparty",
            "calledMethod": "save",
            "methodProperties": {
                "FirstName": first_name,
                "LastName": last_name,
                "MiddleName": middle_name,
                "Phone": phone,
                "Email": "",
                "CounterpartyType": "PrivatePerson",
                "CounterpartyProperty": "Sender",
                "CityRef": city_ref
            }
        }
        return await self._send_request(params)

    async def get_or_create_sender_address(
            self,
            sender_ref: str,
            contact_data: Dict[str, Any],
            default_city_ref: str = "8d5a980d-391c-11dd-90d9-001a92567626",  # Киев
            default_warehouse_ref: str = "7a19252a-0ac4-11e5-8a92-005056887b8d"  # Отделение 1
    ) -> Tuple[str, str]:
        """Get sender's address or create a default one"""
        # Try to get existing addresses
        addresses = await self.get_counterparty_addresses(sender_ref, "Sender")

        if addresses["success"] and addresses["data"]:
            address = addresses["data"][0]
            return address["CityRef"], address["Ref"]

        # If no addresses, create a default one
        print("No sender address found, creating default address...")

        try:
            # Save sender address using contact person data
            address_result = await self.save_sender_address(
                first_name=contact_data["FirstName"],
                last_name=contact_data["LastName"],
                middle_name=contact_data["MiddleName"],
                phone=contact_data["Phones"],
                city_ref=default_city_ref
            )

            if not address_result["success"]:
                print(f"Failed to save address: {address_result.get('errors', ['Unknown error'])}")
                return default_city_ref, default_warehouse_ref

            # Return the default values since we just created them
            return default_city_ref, default_warehouse_ref

        except Exception as e:
            print(f"Error saving address: {str(e)}")
            # In case of error, return default values
            return default_city_ref, default_warehouse_ref

    async def track_document(self, document_number: str) -> Dict[str, Any]:
        """Трекинг отправления по номеру ТТН"""
        params = {
            "apiKey": self.api_key,
            "modelName": "TrackingDocument",
            "calledMethod": "getStatusDocuments",
            "methodProperties": {
                "Documents": [
                    {"DocumentNumber": document_number}
                ]
            }
        }
        return await self._send_request(params)
