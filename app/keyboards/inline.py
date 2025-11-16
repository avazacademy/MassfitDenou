from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_panel_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📦 View All Products", callback_data="admin_view_products")],
            [InlineKeyboardButton(text="➕ Add New Product", callback_data="admin_add_product")],
            [InlineKeyboardButton(text="✏️ Edit Product", callback_data="admin_edit_product")],
            [InlineKeyboardButton(text="🗑 Delete Product", callback_data="admin_delete_product")],
            [InlineKeyboardButton(text="🏢 Manage Branches", callback_data="admin_branches")],
            [InlineKeyboardButton(text="🔙 Back to Main Menu", callback_data="admin_back_main")]
        ]
    )
    return keyboard


def get_product_list_keyboard(products):
    keyboard = []
    for product in products:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{product.name} - ${product.price}", 
                callback_data=f"product_view_{product.id}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Admin Panel", callback_data="admin_panel")])
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
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Admin Panel", callback_data="admin_panel")])
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
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Admin Panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_product_detail_keyboard(product_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Edit", callback_data=f"product_edit_{product_id}")],
            [InlineKeyboardButton(text="🗑 Delete", callback_data=f"product_delete_{product_id}")],
            [InlineKeyboardButton(text="🔙 Back to Products", callback_data="admin_view_products")]
        ]
    )
    return keyboard


def get_confirm_delete_keyboard(product_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yes, Delete", callback_data=f"product_confirm_delete_{product_id}"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="admin_view_products")
            ]
        ]
    )
    return keyboard


def get_cancel_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel", callback_data="admin_panel")]
        ]
    )
    return keyboard


def get_branches_panel_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏢 View All Branches", callback_data="admin_view_branches")],
            [InlineKeyboardButton(text="➕ Add New Branch", callback_data="admin_add_branch")],
            [InlineKeyboardButton(text="✏️ Edit Branch", callback_data="admin_edit_branch")],
            [InlineKeyboardButton(text="🗑 Delete Branch", callback_data="admin_delete_branch")],
            [InlineKeyboardButton(text="🔙 Back to Admin Panel", callback_data="admin_panel")]
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
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Branches Panel", callback_data="admin_branches")])
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
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Branches Panel", callback_data="admin_branches")])
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
    keyboard.append([InlineKeyboardButton(text="🔙 Back to Branches Panel", callback_data="admin_branches")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_branch_detail_keyboard(branch_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️ Edit", callback_data=f"branch_edit_{branch_id}")],
            [InlineKeyboardButton(text="🗑 Delete", callback_data=f"branch_delete_{branch_id}")],
            [InlineKeyboardButton(text="🔙 Back to Branches", callback_data="admin_view_branches")]
        ]
    )
    return keyboard


def get_confirm_delete_branch_keyboard(branch_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Yes, Delete", callback_data=f"branch_confirm_delete_{branch_id}"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="admin_view_branches")
            ]
        ]
    )
    return keyboard
