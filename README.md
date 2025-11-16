# MassfitDenou - Telegram Nutrition Bot

A comprehensive Telegram bot built with Aiogram 3.22 for managing nutrition products, orders, and delivery services. The bot helps users with proper nutrition by providing meal recommendations and managing orders with delivery or pickup options.

## Features

### 🤖 User Features
- **Product Browsing**: Browse products by category (Weight Loss / Weight Gain)
- **Shopping Basket**: Add products to basket with quantity management
- **Order Management**: Create orders with flexible delivery options
- **Delivery Options**: 
  - 🚚 Home Delivery (with location sharing)
  - 🏢 Branch Pickup (choose from available branches)
- **Order Tracking**: View order status updates in real-time

### 👨‍💼 Admin Features
- **Product Management**: Full CRUD operations for products
  - Add/Edit/Delete products
  - Upload product images
  - Set product types (weight loss/gain)
  - Manage pricing and descriptions
- **Branch Management**: Full CRUD operations for branches
  - Add/Edit/Delete branches
  - Upload branch images
  - Set branch locations and descriptions
- **Order Notifications**: Receive order notifications in a dedicated group
- **Order Status Control**: Update order status (Waiting/Cancelled/Delivered)

## Technology Stack

- **Python 3.11+**
- **Aiogram 3.22** - Telegram Bot Framework
- **SQLAlchemy 2.0** - ORM for database operations
- **PostgreSQL** - Database
- **asyncio** - Asynchronous programming

## Project Structure

```
MassfitDenou/
├── app/
│   ├── database/
│   │   ├── models.py              # Database models
│   │   ├── engine.py              # Database engine configuration
│   │   ├── requests.py            # User database operations
│   │   ├── product_requests.py    # Product database operations
│   │   ├── order_requests.py      # Order database operations
│   │   └── branch_requests.py     # Branch database operations
│   ├── handlers/
│   │   ├── start.py               # Start command and phone registration
│   │   ├── admin/
│   │   │   ├── __init__.py        # Admin router aggregator
│   │   │   ├── panel.py           # Admin panel navigation
│   │   │   ├── products.py        # Product CRUD operations
│   │   │   └── branches.py        # Branch CRUD operations
│   │   └── user/
│   │       ├── __init__.py        # User router aggregator
│   │       ├── products.py        # Product browsing
│   │       ├── basket.py          # Basket management
│   │       └── orders.py          # Order creation and management
│   ├── keyboards/
│   │   ├── reply.py               # Reply keyboard layouts
│   │   └── inline.py              # Inline keyboard layouts
│   └── config.py                  # Configuration and environment variables
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
├── .env                           # Environment variables (create from .env.example)
├── .env.example                   # Environment variables template
└── README.md                      # Project documentation
```

## Installation

### Prerequisites
- Python 3.11 or higher
- PostgreSQL database
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone git@github.com:avazcoderr/MassfitDenou.git
   cd MassfitDenou
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your actual values
   ```

5. **Configure PostgreSQL Database**
   - Create a new PostgreSQL database
   - Update `DATABASE_URL` in `.env` file with your database credentials

6. **Run the bot**
   ```bash
   python3 main.py
   ```

## Environment Variables

See `.env.example` for all required environment variables:

- `BOT_TOKEN` - Your Telegram bot token from BotFather
- `ADMIN_ID` - Telegram user ID of the admin
- `GROUP_ID` - Telegram group ID for order notifications
- `DATABASE_URL` - PostgreSQL connection string

## Database Models

### User
- Telegram user information
- Phone number for contact
- Order history

### Product
- Name, price, description
- Product type (weight_loss/weight_gain)
- Product image

### Branch
- Branch name and location
- Description and image
- Pickup point information

### Order
- User information
- Order items and total price
- Delivery type (pickup/delivery)
- Location or branch information
- Order status (waiting/cancelled/delivered)

## Usage

### For Users

1. **Start the bot**: `/start`
2. **Share phone number**: Required for order contact
3. **Browse products**: Choose between "Lose Weight" or "Gain Weight"
4. **Add to basket**: Select products and adjust quantities
5. **My Orders**: View basket and confirm order
6. **Choose delivery method**: 
   - Delivery: Share your location
   - Pickup: Select a branch
7. **Confirm**: Receive order confirmation

### For Admins

1. **Access admin panel**: `/admin`
2. **Manage Products**: Add, edit, or delete products
3. **Manage Branches**: Add, edit, or delete pickup locations
4. **Monitor Orders**: Receive notifications in the configured group
5. **Update Status**: Mark orders as cancelled or delivered

## Key Features Explained

### Smart Order Flow
- Users can choose between home delivery or branch pickup
- Delivery orders require location sharing
- Pickup orders display all available branches with details
- Real-time order notifications to admin group

### Basket Management
- Dynamic quantity adjustment with +/- buttons
- Real-time price calculation
- Items automatically removed when quantity reaches 0
- Clean basket after order confirmation

### Admin Panel
- Intuitive inline keyboard navigation
- Step-by-step product/branch creation
- Image upload support
- Edit individual fields without recreating entries

### Error Handling
- Pending updates cleanup on bot restart (prevents flooding)
- HTML parse mode for formatted messages
- Graceful error handling with user-friendly messages

## Development

### Adding New Features

1. **New Handler**: Create in appropriate handler directory
2. **New Model**: Add to `app/database/models.py`
3. **New Database Operations**: Create requests file in `app/database/`
4. **Register Router**: Include in `main.py` or appropriate `__init__.py`

### Code Style
- Follow existing patterns for consistency
- Use async/await for all database operations
- Implement FSM (Finite State Machine) for multi-step processes
- Always use HTML parse mode for formatted messages

## Troubleshooting

### Bot doesn't respond
- Check if `BOT_TOKEN` is correct
- Ensure bot is not running elsewhere
- Verify network connection

### Database errors
- Verify PostgreSQL is running
- Check `DATABASE_URL` format
- Ensure database exists

### Messages not formatting
- All messages should use HTML parse mode
- Check for unclosed HTML tags

## Contributing

Contributions are welcome! Please follow the existing code structure and style.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions, please open an issue on GitHub or contact the maintainer.

---

**Built with ❤️ using Aiogram 3.22**
