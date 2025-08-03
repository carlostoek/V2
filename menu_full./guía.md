Aquí tienes el módulo administrativo completo del bot (plug-and-play), estructurado según la arquitectura actual del proyecto que me compartiste. Todo el código está listo para integrarse directamente a tu proyecto, sin romper compatibilidad con el sistema existente.


---

✅ Estructura de archivos generada

src/
└── bot/
    └── admin/
        ├── __init__.py
        ├── menu.py              # Menú principal de administración
        └── narrativa.py         # Submódulo de narrativa


---

📁 Archivos generados


---

NOMBRE DE ARCHIVO: src/bot/admin/__init__.py

# Registro centralizado del router administrativo
from .menu import router as admin_menu_router
from .narrativa import router as narrativa_router

admin_routers = [
    admin_menu_router,
    narrativa_router,
]


---

NOMBRE DE ARCHIVO: src/bot/admin/menu.py

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router(name="admin_menu")

class AdminMenu(StatesGroup):
    main = State()
    narrativa = State()

@router.message(F.text == "/admin")
async def show_admin_main(msg: Message, state: FSMContext):
    await state.set_state(AdminMenu.main)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📜 Narrativa", callback_data="admin:narrativa")],
        [InlineKeyboardButton(text="🔒 Cerrar", callback_data="admin:close")]
    ])
    await msg.answer("🛠 Panel del Oráculo — Menú Administrativo", reply_markup=kb)

@router.callback_query(F.data == "admin:close")
async def close_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.message.delete()

@router.callback_query(F.data == "admin:narrativa")
async def go_to_narrativa(cb: CallbackQuery, state: FSMContext):
    await state.set_state(AdminMenu.narrativa)
    from .narrativa import show_narrativa_menu
    await show_narrativa_menu(cb, state)


---

NOMBRE DE ARCHIVO: src/bot/admin/narrativa.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from uuid import uuid4

router = Router(name="admin_narrativa")

# Estado interno de creación
class NarrativaFSM(StatesGroup):
    creando_titulo = State()
    creando_contenido = State()

# Memoria temporal simulada (puede migrarse a DB)
_fragments = {}

def generar_markup_fragmentos():
    botones = []
    for fid, data in _fragments.items():
        botones.append([InlineKeyboardButton(text=data["title"][:30], callback_data=f"admin:narrativa:view:{fid}")])
    botones.append([InlineKeyboardButton(text="➕ Nuevo Fragmento", callback_data="admin:narrativa:new")])
    botones.append([InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:back")])
    return InlineKeyboardMarkup(inline_keyboard=botones)

async def show_narrativa_menu(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text("📜 Fragmentos Narrativos", reply_markup=generar_markup_fragmentos())

@router.callback_query(F.data == "admin:narrativa:new")
async def iniciar_creacion(cb: CallbackQuery, state: FSMContext):
    await state.set_state(NarrativaFSM.creando_titulo)
    await cb.message.edit_text("📝 Escribe el *título* del nuevo fragmento:", parse_mode="Markdown")

@router.message(NarrativaFSM.creando_titulo)
async def recibir_titulo(msg: Message, state: FSMContext):
    await state.update_data(title=msg.text)
    await state.set_state(NarrativaFSM.creando_contenido)
    await msg.answer("✍️ Ahora escribe el *contenido* del fragmento:")

@router.message(NarrativaFSM.creando_contenido)
async def recibir_contenido(msg: Message, state: FSMContext):
    data = await state.get_data()
    frag_id = str(uuid4())
    _fragments[frag_id] = {
        "title": data["title"],
        "content": msg.text
    }
    await state.clear()
    await msg.answer(f"✅ Fragmento guardado como `{frag_id[:6]}`")
    
@router.callback_query(F.data.startswith("admin:narrativa:view:"))
async def ver_fragmento(cb: CallbackQuery, state: FSMContext):
    frag_id = cb.data.split(":")[-1]
    frag = _fragments.get(frag_id)
    if not frag:
        await cb.answer("❌ Fragmento no encontrado", show_alert=True)
        return
    await cb.message.edit_text(
        f"*{frag['title']}*\n\n{frag['content']}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Volver", callback_data="admin:narrativa")],
        ]),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "admin:narrativa")
async def reload_narrativa(cb: CallbackQuery, state: FSMContext):
    await show_narrativa_menu(cb, state)

@router.callback_query(F.data == "admin:back")
async def back_to_main(cb: CallbackQuery, state: FSMContext):
    from .menu import show_admin_main
    await show_admin_main(cb.message, state)


---

✅ INSTRUCCIONES DE INTEGRACIÓN (plug & play)

1. Copia los archivos

Coloca todo el contenido en:

src/bot/admin/


---

2. Registra los routers en src/bot/core/handlers.py

from bot.admin import admin_routers  # AÑADIR ESTO

def register_handlers(dp: Dispatcher) -> None:
    ...
    for r in admin_routers:  # AÑADIR ESTA LÍNEA
        dp.include_router(r)


---

3. Protege con middleware de admins (opcional)

En middleware.py, si ya tienes algo como OnlyAdminsMiddleware, úsalo. Si no, puedo generar uno.


---

4. Reinicia el bot

Ya puedes usar /admin y navegar el menú administrativo.

