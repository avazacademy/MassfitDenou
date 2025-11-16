from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_panel_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📦 Barcha mahsulotlar", callback_data="admin_view_products")],
            [InlineKeyboardButton(text="➕ Yangi mahsulot qo'shish", callback_data="admin_add_product")],
            [InlineKeyboardButton(text="✏️ Mahsulotni tahrirlash", callback_data="admin_edit_product")],
            [InlineKeyboardButton(text="🗑 Mahsulotni o'chirish", callback_data="admin_delete_product")],
            [InlineKeyboardButton(text="🏢 Filiallarni boshqarish", callback_data="admin_branches")],
            [InlineKeyboardButton(text="🔙 Asosiy menyuga qaytish", callback_data="admin_back_main")]
        ]
    )
    return keyboard


def get_product_list_keyboard(products):
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{product.name} - {product.price} so'm", 
                callback_data=f"product_view_{product.id}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Admin panelga qaytish", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_product_edit_keyboard(products):
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{product.name}", 
                callback_data=f"product_edit_{product.id}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Admin panelga qaytish", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_product_delete_keyboard(products):
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                text=f"❌ {product.name}", 
                callback_data=f"product_delete_{product.id}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Admin panelga qaytish", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_product_detail_keyboard(product_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"product_edit_{product_id}")],
            [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"product_delete_{product_id}")],
            [InlineKeyboardButton(text="🔙 Mahsulotlarga qaytish", callback_data="admin_view_products")]
        ]
    )
    return keyboard


def get_confirm_delete_keyboard(product_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"product_confirm_delete_{product_id}"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_view_products")
            ]
        ]
    )
    return keyboard


def get_cancel_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_panel")]
        ]
    )
    return keyboard


def get_branches_panel_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏢 Barcha filiallar", callback_data="admin_view_branches")],
            [InlineKeyboardButton(text="➕ Yangi filial qo'shish", callback_data="admin_add_branch")],
            [InlineKeyboardButton(text="✏️ Filialni tahrirlash", callback_data="admin_edit_branch")],
            [InlineKeyboardButton(text="🗑 Filialni o'chirish", callback_data="admin_delete_branch")],
            [InlineKeyboardButton(text="🔙 Admin panelga qaytish", callback_data="admin_panel")]
        ]
    )
    return keyboard


def get_branch_list_keyboard(branches):
    keyboard = []
    for branch in branches:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{branch.name}", 
                callback_data=f"branch_view_{branch.id}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Filiallar paneliga qaytish", callback_data="admin_branches")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_branch_edit_keyboard(branches):
    keyboard = []
    for branch in branches:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{branch.name}", 
                callback_data=f"branch_edit_{branch.id}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Filiallar paneliga qaytish", callback_data="admin_branches")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_branch_delete_keyboard(branches):
    keyboard = []
    for branch in branches:
        keyboard.append([
            InlineKeyboardButton(
                text=f"❌ {branch.name}", 
                callback_data=f"branch_delete_{branch.id}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Filiallar paneliga qaytish", callback_data="admin_branches")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_branch_detail_keyboard(branch_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"branch_edit_{branch_id}")],
            [InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"branch_delete_{branch_id}")],
            [InlineKeyboardButton(text="🔙 Filiallarga qaytish", callback_data="admin_view_branches")]
        ]
    )
    return keyboard


def get_confirm_delete_branch_keyboard(branch_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"branch_confirm_delete_{branch_id}"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_view_branches")
            ]
        ]
    )
    return keyboard
