from dataclasses import dataclass
from typing import List

from lecture_2.hw.shop_api.routes.model import Item


def id_generator():
    i = 0
    while True:
        i += 1
        yield i


class ItemRepository:
    @dataclass(slots=True)
    class ItemEntity:
        id: int
        name: str
        price: float
        deleted: bool

    __item_table: dict[int, ItemEntity]
    __item_id_generator = id_generator()

    def __init__(self):
        self.__item_table = dict()

    def create(self, item: Item) -> Item:
        item_entity = ItemRepository.ItemEntity(next(self.__item_id_generator), item.name, item.price, item.deleted)
        self.__item_table[item_entity.id] = item_entity

        item.id = item_entity.id
        return item

    def get(self, item_id: int) -> Item:
        assert item_id
        item_entity = self.__item_table.get(item_id)
        assert item_entity, f"Item with id {item_id} not found"
        return Item(item_entity.id, item_entity.name, item_entity.price, item_entity.deleted)

    def query(self, offset=0, limit=10, min_price: int | None = None, max_price: int | None = None,
              show_deleted=False) -> list[Item]:
        item_entities = list(self.__item_table.values())
        item_entities = item_entities[offset:]

        query_result: list[Item] = []

        for item_entity in item_entities:
            if len(query_result) == limit:
                break

            if min_price is not None and item_entity.price < min_price:
                continue
            if max_price is not None and item_entity.price > max_price:
                continue
            if not show_deleted and item_entity.deleted:
                continue

            query_result.append(Item(item_entity.id, item_entity.name, item_entity.price, item_entity.deleted))

        return query_result[:limit]

    def update(self, item: Item) -> Item:
        assert item.id
        item_entity = self.__item_table.get(item.id)
        assert item_entity

        item_entity.name = item.name
        item_entity.price = item.price
        item_entity.deleted = item.deleted

        return Item(item_entity.id, item_entity.name, item_entity.price, item_entity.deleted)


@dataclass(slots=True)
class CartItemEntity:
    id: int
    item: ItemRepository.ItemEntity
    quantity: int

    def available(self) -> bool:
        return not self.item.deleted


@dataclass(slots=True)
class CartEntity:
    id: int
    items: List[CartItemEntity]

    def price(self) -> float:
        price = 0
        for cart_item in self.items:
            if cart_item.available():
                price += cart_item.quantity * cart_item.item.price

        return price


class CartRepository:
    __cart_table: dict[int, CartEntity]
    __cart_item_table: dict[int, CartItemEntity]
    __cart_id_generator = id_generator()
    __cart_item_id_generator = id_generator()

    def __init__(self):
        self.__cart_table = dict()
        self.__cart_item_table = dict()

    def create_cart(self) -> CartEntity:
        cart_id = next(self.__cart_id_generator)
        new_cart = CartEntity(id=cart_id, items=[])
        self.__cart_table[cart_id] = new_cart
        return new_cart

    def get_cart(self, cart_id: int) -> CartEntity:
        assert cart_id
        cart = self.__cart_table.get(cart_id)
        assert cart, f"Cart with id {cart_id} not found"
        return cart

    def add_item_to_cart(self, cart_id: int, item: ItemRepository.ItemEntity, quantity: int = 1) -> CartEntity:
        assert cart_id
        cart = self.__cart_table.get(cart_id)
        assert cart, f"Cart with id {cart_id} not found"

        for cart_item in cart.items:
            if cart_item.item.id == item.id:
                cart_item.quantity += quantity
                return cart

        cart_item_id = next(self.__cart_item_id_generator)
        new_cart_item = CartItemEntity(
            id=cart_item_id,
            item=item,
            quantity=quantity
        )
        cart.items.append(new_cart_item)
        self.__cart_item_table[cart_item_id] = new_cart_item
        return cart

    def query_carts(
            self,
            offset: int = 0,
            limit: int = 10,
            min_price: float = None,
            max_price: float = None,
            min_quantity: int = None,
            max_quantity: int = None
    ) -> List[CartEntity]:
        cart_entities = list(self.__cart_table.values())
        cart_entities = cart_entities[offset:]

        query_result: List[CartEntity] = []
        for cart_entity in cart_entities:
            if len(query_result) == limit:
                break

            total_price = cart_entity.price()
            total_quantity = sum(item.quantity for item in cart_entity.items)

            if min_price is not None and total_price < min_price:
                continue
            if max_price is not None and total_price > max_price:
                continue
            if min_quantity is not None and total_quantity < min_quantity:
                continue
            if max_quantity is not None and total_quantity > max_quantity:
                continue

            query_result.append(cart_entity)

        return query_result[:limit]


item_repository = ItemRepository()
cart_repository = CartRepository()
