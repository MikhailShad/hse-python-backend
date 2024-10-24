from http import HTTPStatus
from typing import List, Optional

from fastapi import HTTPException, APIRouter, Query, Response

from lecture_2.hw.shop_api.routes.model import Item, ItemPatchRequest, ItemPutRequest
from lecture_2.hw.shop_api.storage.repository import item_repository

router = APIRouter(prefix="/item")


@router.post("/", status_code=HTTPStatus.CREATED, response_model=Item)
def create_item(item: Item):
    created_item = item_repository.create(Item(id=0, name=item.name, price=item.price, deleted=False))
    return Item(id=created_item.id, name=created_item.name, price=created_item.price,
                deleted=created_item.deleted)


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: int):
    item = item_repository.get(item_id)
    if not item or item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    return Item(id=item.id, name=item.name, price=item.price, deleted=item.deleted)


@router.get("/", response_model=List[Item])
def list_items(
        offset: int = Query(0, ge=0),
        limit: int = Query(10, gt=0),
        min_price: Optional[float] = Query(None, ge=0),
        max_price: Optional[float] = Query(None, ge=0),
        show_deleted: bool = False):
    items = item_repository.query(offset=offset, limit=limit, min_price=min_price, max_price=max_price,
                                  show_deleted=show_deleted)
    return [Item(id=item.id, name=item.name, price=item.price, deleted=item.deleted) for item in items]


@router.put("/{item_id}", response_model=Item)
def put_item(item_id: int, item_put_request: ItemPutRequest):
    item = item_repository.get(item_id)
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    updated_item = item_repository.update(
        Item(id=item_id, name=item_put_request.name, price=item_put_request.price, deleted=item.deleted))

    return updated_item


@router.patch("/{item_id}", response_model=Item)
def patch_item(response: Response, item_id: int, item_patch_request: ItemPatchRequest):
    item = item_repository.get(item_id)
    if not item:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    if item.deleted:
        response.status_code = HTTPStatus.NOT_MODIFIED
        return item

    updated_item = item_repository.update(
        Item(id=item_id, name=item_patch_request.name, price=item_patch_request.price, deleted=item.deleted))

    return updated_item


@router.delete("/{item_id}")
def delete_item(item_id: int):
    item_to_delete = item_repository.get(item_id)
    if not item_to_delete:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found")

    item_to_delete.deleted = True
    item_repository.update(item_to_delete)
    return {"message": "Item marked as deleted"}
