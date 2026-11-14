from pydantic import BaseModel, Field


# What the client SENDS to create a restaurant (no id: the server assigns it)
class RestaurantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    city: str
    cuisine: str
    rating: float = Field(default=0.0, ge=0, le=5)
    operational: bool = True


# What the server RETURNS (everything above + id)
class Restaurant(RestaurantCreate):
    id: int


class MenuItemCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    price: int = Field(gt=0, description="Price in rupees")
    is_veg: bool = True


class MenuItem(MenuItemCreate):
    id: int
    restaurant_id: int


class RestaurantUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=80)
    rating: float | None = Field(default=None, ge=0, le=5)
    city: str | None = None
    cuisine: str | None = None
    rating: float | None = Field(default=0.0, ge=0, le=5)
    operational: bool | None = None
