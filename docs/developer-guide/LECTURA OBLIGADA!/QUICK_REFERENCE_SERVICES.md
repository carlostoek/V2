# 🚀 Diana V2 Services Integration - Quick Reference

## 📋 **TL;DR: How to Connect Any UI to Services**

```python
# 1. Get service from adapter
service = self.services.get('service_name')

# 2. Call service method
result = await service.method_name(params)

# 3. Handle response
if result['success']:
    # Success flow
else:
    # Error flow
```

## 🏗️ **Current Architecture (as of 2025-08-09)**

```
┌─────────────────┐    ┌──────────────────────────┐    ┌─────────────────┐
│   Admin UI      │ ── │  Services Integration    │ ── │  Real Services  │
│ diana_admin_    │    │ diana_admin_services_    │    │ ChannelService  │
│ master.py       │    │ integration.py           │    │ TariffService   │
└─────────────────┘    └──────────────────────────┘    │ Tokeneitor      │
                                                        └─────────────────┘
```

## 🎯 **Services Available Right Now**

| Service Key | Class | File | Main Methods |
|-------------|-------|------|--------------|
| `channel` | ChannelService | `src/modules/channel/service.py` | `create_channel()`, `get_channel()`, `delete_channel()` |
| `tariff` | TariffService | `src/modules/tariff/service.py` | `create_tariff()`, `get_all_tariffs()`, `delete_tariff()` |
| `tokeneitor` | Tokeneitor | `src/modules/token/tokeneitor.py` | `generate_token()`, `create_tariff()` |

## 💡 **Real Examples from Current Code**

### ✅ **Get All Tariffs (WORKING)**
```python
# In diana_admin_services_integration.py
async def get_all_tariffs(self):
    tariff_service = self.services.get('tariff')
    if not tariff_service:
        return []
    
    tariffs_raw = await tariff_service.get_all_tariffs()
    # Convert to dict format for UI
    return [{'id': t.id, 'name': t.name, 'price': t.price} for t in tariffs_raw]
```

### ✅ **Create Channel (WORKING)**  
```python
# In diana_admin_services_integration.py
async def add_vip_channel(self, admin_id, telegram_id, name):
    channel_service = self.services.get('channel')
    if not channel_service:
        return None
        
    new_channel_id = await channel_service.create_channel(
        telegram_id=telegram_id, name=name, 
        description="VIP Channel", channel_type="vip"
    )
    return {"success": True, "channel_info": {"id": new_channel_id}}
```

### ✅ **Delete Tariff (WORKING)**
```python
# In diana_admin_services_integration.py
async def delete_tariff(self, admin_id, tariff_id):
    tariff_service = self.services.get('tariff')
    result = await tariff_service.delete_tariff(tariff_id)
    
    return {
        "success": result['success'], 
        "message": result['message']
    }
```

## 🔄 **Interactive Flow Pattern**

```python
# 1. Start flow - store state
self._pending_operation[user_id] = {'step': 'input', 'data': {}}

# 2. Process input - update state  
self._pending_operation[user_id]['data']['field'] = user_input

# 3. Complete flow - call service
result = await service.method(flow_data)

# 4. Clean up
del self._pending_operation[user_id]
```

## 🎯 **Callback Routing (Current Pattern)**

```
admin:action:vip:manage_tariffs → show_tariffs_management_interface()
admin:action:vip:tariff_create → start_tariff_creation_flow()  
admin:action:vip:tariff_delete:123 → delete_tariff(admin_id, 123)
admin:action:global_config:add_channels → start_channel_registration_flow()
```

## 🚨 **Critical Rules**

1. **NEVER** write direct database queries in integration layer
2. **ALWAYS** use existing services from `self.services.get()`
3. **ALWAYS** check if service exists before calling
4. **ALWAYS** handle service response format `{'success': bool, 'message': str}`
5. **ALWAYS** log operations with emoji prefixes for easy debugging

## 🔧 **How to Add New Service Integration**

```python
# Step 1: Register in adapter.py (if not already done)
from src.modules.myservice.service import MyService
self._my_service = MyService(event_bus)
self._services['myservice'] = self._my_service

# Step 2: Add integration method
async def handle_my_operation(self, admin_id):
    service = self.services.get('myservice')  
    if not service:
        return {"success": False, "message": "Service unavailable"}
    
    result = await service.do_operation(admin_id)
    return result

# Step 3: Connect to UI callback
elif action == "myservice:operation":
    await self.handle_my_operation(user_id)
```

## 📊 **Current Status Health Check**

- ✅ **ChannelService**: Fully integrated 
- ✅ **TariffService**: Fully integrated
- ✅ **Tokeneitor**: Fully integrated  
- ✅ **Interactive Flows**: Working (tariff creation, channel registration)
- ✅ **Error Handling**: Comprehensive with logging
- ✅ **Code Duplication**: ❌ Eliminated

**Architecture Status**: 🟢 **HEALTHY** - All services properly connected through clean abstraction layers.
