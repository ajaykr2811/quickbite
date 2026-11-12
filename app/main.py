from fastapi import FastAPI, HTTPException, Query

from app.schemas import MenuItem, MenuItemCreate, Restaurant, RestaurantCreate, RestaurantUpdate

app = FastAPI(title="QuickBite API", version="0.1.0")

# ---------------------------------------------------------------
# Fake in-memory "database". Build M3 swaps this for a real one.
# ---------------------------------------------------------------
restaurants: dict[int, Restaurant] = {}
menu_items: dict[int, MenuItem] = {}
next_ids = {"restaurant": 1, "menu_item": 1}


def new_id(kind: str) -> int:
    value = next_ids[kind]
    next_ids[kind] += 1
    return value


def get_restaurant_or_404(restaurant_id: int) -> Restaurant:
    restaurant = restaurants.get(restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    return restaurant

def ensure_operational(restaurant: Restaurant) -> None:
    if not restaurant.operational:
        raise HTTPException(status_code=409, detail=f"{restaurant.name} is not operational")
# ---------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/restaurants", response_model=Restaurant, status_code=201)
def create_restaurant(data: RestaurantCreate):
    restaurant = Restaurant(id=new_id("restaurant"), **data.model_dump())
    restaurants[restaurant.id] = restaurant
    return restaurant


@app.get("/restaurants", response_model=list[Restaurant])
def list_restaurants(
    city: str | None = None,
    cuisine: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
):
    result = list(restaurants.values())
    result = [r for r in result if r.operational is True]
    if city:
        result = [r for r in result if r.city.lower() == city.lower()]
    if cuisine:
        result = [r for r in result if r.cuisine.lower() == cuisine.lower()]
    return result[:limit]


@app.get("/restaurants/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: int):
    restaurant = get_restaurant_or_404(restaurant_id)   
    ensure_operational(restaurant)  
    return restaurant


@app.post(  
    "/restaurants/{restaurant_id}/menu",
    response_model=MenuItem,
    status_code=201,
)
def add_menu_item(restaurant_id: int, data: MenuItemCreate):
    get_restaurant_or_404(restaurant_id)
    item = MenuItem(
        id=new_id("menu_item"), restaurant_id=restaurant_id, **data.model_dump()
    )
    menu_items[item.id] = item
    return item


@app.get("/restaurants/{restaurant_id}/menu", response_model=list[MenuItem])
def get_menu(restaurant_id: int, veg_only: bool = False):
    restaurant = get_restaurant_or_404(restaurant_id)
    ensure_operational(restaurant)
    items = [i for i in menu_items.values() if i.restaurant_id == restaurant_id]
    if veg_only:
        items = [i for i in items if i.is_veg]
    return items

@app.patch("/restaurants/{restaurant_id}", response_model=RestaurantUpdate)
def update_restaurant(restaurant_id: int, data:RestaurantUpdate):
    restaurant = get_restaurant_or_404(restaurant_id)
    change = data.model_dump(exclude_unset=True,exclude_none=True)
    updated = restaurant.model_copy(update=change)
    restaurants[restaurant_id] = updated
    return updated

@app.delete("/restaurants/{restaurant_id}", status_code=204)
def delete_restaurant(restaurant_id: int):
    get_restaurant_or_404(restaurant_id)
    del restaurants[restaurant_id]
    item_ids = [i.id for i in menu_items.values() 
                if i.restaurant_id == restaurant_id]
    for item_id in item_ids:
        del menu_items[item_id]
# ---------------------------------------------------------------
# Sample data so /docs has something to show
# ---------------------------------------------------------------
def seed():
    spice = create_restaurant(
        RestaurantCreate(name="Spice Route", city="Pune", cuisine="Indian", rating=4.4)
    )
    bangkok = create_restaurant(
        RestaurantCreate(name="Bangkok Bites", city="Pune", cuisine="Thai", rating=4.1)
    )
    add_menu_item(spice.id, MenuItemCreate(name="Paneer Tikka", price=260))
    add_menu_item(spice.id, MenuItemCreate(name="Chicken Biryani", price=320, is_veg=False))
    add_menu_item(bangkok.id, MenuItemCreate(name="Green Curry", price=340))


seed()
