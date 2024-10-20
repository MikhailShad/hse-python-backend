from http import HTTPStatus
from typing import List

from fastapi import HTTPException, APIRouter, Response, Query

from lecture_2.hw.shop_api.routes.model import Cart
from lecture_2.hw.shop_api.storage.repository import cart_repository, item_repository

router = APIRouter(prefix="/cart")


@router.post("/", status_code=HTTPStatus.CREATED, response_model=Cart)
def create_cart(response: Response):
    cart = cart_repository.create_cart()
    response.headers['location'] = f"/cart/{cart.id}"
    return Cart(id=cart.id, items=[], price=0)


@router.get("/{cart_id}", response_model=Cart)
def get_cart(cart_id: int):
    cart = cart_repository.get_cart(cart_id)
    if not cart:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")

    return Cart(
        id=cart.id,
        items=[
            Cart.Item(
                id=cart_item.item.id,
                name=cart_item.item.name,
                quantity=cart_item.quantity,
                available=cart_item.available()
            ) for cart_item in cart.items
        ],
        price=cart.price()
    )


@router.post("/{cart_id}/add/{item_id}", response_model=Cart)
def add_item_to_cart(cart_id: int, item_id: int, quantity: int = 1):
    item = item_repository.get(item_id)
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    cart = cart_repository.add_item_to_cart(cart_id, item, quantity)

    return Cart(
        id=cart.id,
        items=[
            Cart.Item(
                id=cart_item.item.id,
                name=cart_item.item.name,
                quantity=cart_item.quantity,
                available=cart_item.available()
            ) for cart_item in cart.items
        ],
        price=cart.price()
    )


@router.get("/", response_model=List[Cart])
def list_carts(
        offset: int = Query(0, ge=0),
        limit: int = Query(10, gt=0),
        min_price: float = Query(None, ge=0),
        max_price: float = Query(None, ge=0),
        min_quantity: int = Query(None, ge=0),
        max_quantity: int = Query(None, ge=0)):
    carts = cart_repository.query_carts(offset=offset,
                                        limit=limit,
                                        min_price=min_price,
                                        max_price=max_price,
                                        min_quantity=min_quantity,
                                        max_quantity=max_quantity)

    return [
        Cart(
            id=cart.id,
            items=[
                Cart.Item(
                    id=cart_item.item.id,
                    name=cart_item.item.name,
                    quantity=cart_item.quantity,
                    available=cart_item.available()
                ) for cart_item in cart.items
            ],
            price=cart.price()
        )
        for cart in carts
    ]
