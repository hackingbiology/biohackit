# SPDX-License-Identifier: AGPL-3.0-or-later
"""Owner-only product API (M03 TG-e). Another user's product is a 404."""

from collections.abc import Callable
from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import status  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.exceptions import ValidationError  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.permissions import IsAuthenticated  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.request import Request  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.response import Response  # type: ignore[import-untyped]  # DRF ships no stubs
from rest_framework.views import APIView  # type: ignore[import-untyped]  # DRF ships no stubs

from . import products
from .models import Product, ProductIngredient
from .services import SubstanceError


def ingredient_data(ingredient: ProductIngredient) -> dict[str, Any]:
    amount = ingredient.amount_per_unit
    return {
        "id": ingredient.pk,
        "substance": ingredient.substance_id,
        "amount_per_unit": None if amount is None else format(amount, "f"),
        "unit": ingredient.unit,
        "label_source": ingredient.label_source,
    }


def product_data(product: Product) -> dict[str, Any]:
    return {
        "id": product.pk,
        "name": product.name,
        "label_source": product.label_source,
        "label_fetched_on": product.label_fetched_on.isoformat(),
        "ingredients": [ingredient_data(i) for i in product.ingredients.all()],
    }


def _body(request: Request) -> dict[str, Any]:
    if not isinstance(request.data, dict):
        raise ValidationError({"detail": "Send a JSON object."})
    return dict(request.data)


def _run(call: Callable[[], Any]) -> Any:
    try:
        return call()
    except SubstanceError as exc:
        raise ValidationError(exc.errors) from None


def _mine(request: Request, pk: int) -> Product:
    return get_object_or_404(Product, pk=pk, owner=request.user)


class _Base(APIView):  # type: ignore[misc]  # base is Any: DRF untyped
    permission_classes = [IsAuthenticated]


class ProductListCreateView(_Base):
    def get(self, request: Request) -> Response:
        rows = Product.objects.filter(owner=request.user).prefetch_related(
            "ingredients"
        )
        return Response([product_data(p) for p in rows])

    def post(self, request: Request) -> Response:
        product = _run(lambda: products.create_product(request.user, _body(request)))
        return Response(product_data(product), status=status.HTTP_201_CREATED)


class ProductDetailView(_Base):
    def get(self, request: Request, pk: int) -> Response:
        return Response(product_data(_mine(request, pk)))

    def patch(self, request: Request, pk: int) -> Response:
        product = _run(
            lambda: products.update_product(_mine(request, pk), _body(request))
        )
        return Response(product_data(product))


class IngredientCreateView(_Base):
    def post(self, request: Request, pk: int) -> Response:
        ingredient = _run(
            lambda: products.add_ingredient(_mine(request, pk), _body(request))
        )
        return Response(ingredient_data(ingredient), status=status.HTTP_201_CREATED)


class IngredientDetailView(_Base):
    def _row(self, request: Request, pk: int, ingredient_id: int) -> ProductIngredient:
        return get_object_or_404(_mine(request, pk).ingredients, pk=ingredient_id)

    def patch(self, request: Request, pk: int, ingredient_id: int) -> Response:
        row = self._row(request, pk, ingredient_id)
        _run(lambda: products.update_ingredient(row, _body(request)))
        return Response(ingredient_data(row))

    def delete(self, request: Request, pk: int, ingredient_id: int) -> Response:
        self._row(request, pk, ingredient_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
